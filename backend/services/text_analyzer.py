# backend/services/text_analyzer.py
import joblib
import re
import numpy as np
import os

# Try importing BERT dependencies (torch must come first)
try:
    import torch
    from transformers import BertTokenizer, BertForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Load both models at startup — only loaded once
BASE = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE, 'models')

RF_MODEL_PATH = os.path.join(MODELS_DIR, 'rf_model.pkl')
TFIDF_PATH    = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')
SHAP_PATH     = os.path.join(MODELS_DIR, 'shap_explainer.pkl')

rf_model  = None
tfidf     = None
explainer = None

if os.path.exists(RF_MODEL_PATH):
    rf_model = joblib.load(RF_MODEL_PATH)
    print('[TextAnalyzer] Random Forest model loaded')

if os.path.exists(TFIDF_PATH):
    tfidf = joblib.load(TFIDF_PATH)
    print('[TextAnalyzer] TF-IDF vectorizer loaded')

if os.path.exists(SHAP_PATH):
    explainer = joblib.load(SHAP_PATH)
    print('[TextAnalyzer] SHAP explainer loaded')

# BERT (optional)
BERT_PATH     = os.path.join(MODELS_DIR, 'bert_model')
USE_BERT      = False
bert_tokenizer = None
bert_model    = None

if TRANSFORMERS_AVAILABLE and os.path.exists(BERT_PATH) and \
   os.path.exists(os.path.join(BERT_PATH, 'config.json')):
    try:
        bert_tokenizer = BertTokenizer.from_pretrained(BERT_PATH)
        bert_model = BertForSequenceClassification.from_pretrained(BERT_PATH)
        bert_model.eval()
        USE_BERT = True
        print('[TextAnalyzer] BERT model loaded')
    except Exception as e:
        print(f'[TextAnalyzer] Could not load BERT: {e}')

# ─── Constants ────────────────────────────────────────────────────────────────

STOPWORDS = {
    'the','a','an','is','are','was','were','be','been','being',
    'have','has','had','do','does','did','will','would','could','should',
    'may','might','shall','can','to','of','in','for','on','with','at',
    'by','from','as','or','and','but','not','this','that','it','its',
    'we','you','he','she','they','i','my','our','your','their',
    'am','good','happy','name','hi','hello','thank','please','about',
    'boy','girl','play','like','love','nice','great','very','just','get',
    'one','two','three','day','time','now','all','new','more','any'
}

# Common English words — used for gibberish detection
COMMON_ENGLISH_WORDS = {
    'the','be','to','of','and','a','in','that','have','it','for','not',
    'on','with','he','as','you','do','at','this','but','his','by','from',
    'they','we','say','her','she','or','an','will','my','one','all','would',
    'there','their','what','so','up','out','if','about','who','get','which',
    'go','me','when','make','can','like','time','no','just','him','know',
    'take','people','into','year','your','good','some','could','them','see',
    'other','than','then','now','look','only','come','its','over','think',
    'also','back','after','use','two','how','our','work','first','well',
    'way','even','new','want','because','any','these','give','day','most',
    'job','company','salary','experience','apply','position','skills','role',
    'candidate','requirements','qualifications','interview','joining','office',
    'hiring','vacancy','fresher','resume','work','team','management','process',
    'location','contact','email','phone','please','send','immediate','urgent',
    'pay','earn','income','money','registration','fee','deposit','guarantee',
    'home','online','daily','weekly','monthly','part','full','remote','training'
}

JOB_KEYWORDS = {
    'job','hiring','vacancy','apply','salary','experience','work',
    'company','position','role','skills','requirements','resume','cv',
    'joining','candidate','qualification','interview','office','remote',
    'full time','part time','internship','fresher','lpa','ctc','per month',
    'earn','income','payment','whatsapp','urgent','immediate','data entry',
    'work from home','typing','copy paste','registration','deposit'
}

# Salary reality check: role keyword → realistic max monthly salary (INR)
SALARY_BENCHMARKS = {
    'data entry': 18000, 'typing': 15000, 'copy paste': 12000,
    'packing': 15000, 'telecaller': 20000, 'receptionist': 25000,
    'delivery': 20000, 'driver': 25000, 'helper': 15000,
    'housekeeping': 15000, 'security': 18000, 'sweeper': 12000,
}

# ─── Helper functions ─────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Clean and normalize text for model input."""
    text = str(text).lower()
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def strip_emojis(text: str) -> str:
    """Remove emoji characters, return clean text."""
    emoji_pattern = re.compile(
        '[\U00010000-\U0010ffff'
        '\U0001F600-\U0001F64F'
        '\U0001F300-\U0001F5FF'
        '\U0001F680-\U0001F6FF'
        '\U0001F1E0-\U0001F1FF'
        '\u2600-\u26FF\u2700-\u27BF]+',
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text).strip()


def is_gibberish(text: str) -> bool:
    """
    Returns True if text is random characters / not real language.
    Checks: ratio of real English words in the text.
    """
    cleaned = clean_text(text)
    words = [w for w in cleaned.split() if len(w) > 1]
    if len(words) == 0:
        return True
    real_words = sum(1 for w in words if w in COMMON_ENGLISH_WORDS)
    ratio = real_words / len(words)
    return ratio < 0.25  # less than 25% real words = gibberish


def is_job_posting(text: str) -> bool:
    """Check if text looks like a job posting at all."""
    text_lower = text.lower()
    matched = sum(1 for kw in JOB_KEYWORDS if kw in text_lower)
    return matched >= 2


def detect_heuristic_signals(text: str) -> list:
    """
    Rule-based scam signal detector.
    Returns list of flag strings found in the text.
    """
    flags = []
    text_lower = text.lower()

    # 1. Phone number detection (Indian mobile: 10 digits starting 6-9)
    phones = re.findall(r'\b[6-9]\d{9}\b', text)
    if phones:
        flags.append(f'Direct phone number in job posting ({phones[0]}) — legitimate companies use application portals')

    # 2. WhatsApp/Telegram contact
    if 'whatsapp' in text_lower or 'telegram' in text_lower or 'wa.me' in text_lower:
        flags.append('Asking to contact via WhatsApp/Telegram — scam jobs avoid official channels')

    # 3. Registration / deposit fee
    fee_patterns = [
        r'registration\s*fee', r'security\s*deposit', r'refundable\s*deposit',
        r'training\s*fee', r'kit\s*charges', r'pay\s*rs\.?\s*\d+',
        r'pay\s*₹\s*\d+', r'advance\s*payment', r'joining\s*fee'
    ]
    for pat in fee_patterns:
        if re.search(pat, text_lower):
            flags.append('Requires upfront payment or deposit — legitimate employers NEVER ask for money')
            break

    # 4. Unrealistic salary check
    salary_matches = re.findall(
        r'(?:rs\.?|inr|₹)\s*(\d[\d,]*)\s*(?:/|-|per)\s*(day|daily|week|weekly|month)',
        text_lower
    )
    for amount_str, period in salary_matches:
        try:
            amount = int(amount_str.replace(',', ''))
            if period in ('day', 'daily') and amount > 3000:
                flags.append(f'Unrealistic daily salary of Rs.{amount:,} — average is Rs.500-1500/day')
            elif period in ('week', 'weekly') and amount > 20000:
                flags.append(f'Unrealistic weekly salary of Rs.{amount:,}')
            elif period in ('month',) and amount > 150000:
                flags.append(f'Suspicious monthly salary of Rs.{amount:,} for non-technical role')
        except ValueError:
            pass

    # 5. Role + salary mismatch
    for role, max_sal in SALARY_BENCHMARKS.items():
        if role in text_lower:
            sal_match = re.search(r'(\d[\d,]+)\s*(?:per month|/month|monthly)', text_lower)
            if sal_match:
                try:
                    sal = int(sal_match.group(1).replace(',', ''))
                    if sal > max_sal * 2:
                        flags.append(f'Claimed salary for {role} work is {int(sal/max_sal)}x higher than industry average')
                except ValueError:
                    pass

    # 6. Guaranteed income promise
    guarantee_patterns = ['guaranteed', '100% placement', 'assured income', 'fixed income', 'guaranteed salary']
    for pat in guarantee_patterns:
        if pat in text_lower:
            flags.append(f'Uses "{pat}" — no legitimate job can guarantee income before hiring')
            break

    # 7. No experience + high pay combination
    if ('no experience' in text_lower or 'fresher' in text_lower) and \
       re.search(r'(\d[\d,]+)', text_lower):
        sal_match = re.search(r'(\d[\d,]+)\s*(?:per month|/month|lpa)', text_lower)
        if sal_match:
            try:
                sal = int(sal_match.group(1).replace(',', ''))
                if sal > 40000:
                    flags.append('High salary offered for "no experience" role — classic scam pattern')
            except ValueError:
                pass

    # 8. Urgency pressure tactics
    urgency = ['apply immediately', 'last date today', 'only.*seats', 'limited vacancy',
               'urgent requirement', 'join today', 'direct joining']
    for urg in urgency:
        if re.search(urg, text_lower):
            flags.append('Uses urgency pressure tactics to rush decision-making')
            break

    # 9. Data entry / typing / copy-paste jobs (almost always scams)
    scam_job_types = ['data entry', 'copy paste', 'typing job', 'copy typing', 'form filling']
    for jt in scam_job_types:
        if jt in text_lower:
            flags.append(f'"{jt}" jobs are extremely common in online job scams in India')
            break

    return flags


# ─── Main analysis function ───────────────────────────────────────────────────

def analyze_text(text: str) -> dict:
    """
    Analyzes job posting text for fraud signals.
    Now with: gibberish detection, heuristic signals, phone/fee/salary checks.
    """
    # Step 1: Strip emojis and check if anything remains
    text_no_emoji = strip_emojis(text)
    cleaned = clean_text(text_no_emoji)
    word_count = len(cleaned.split())

    # Too short
    if word_count < 10:
        return {
            'prediction': 0, 'probability': 0.0, 'risk_score': 0,
            'top_reasons': [],
            'warning': f'Text too short ({word_count} words). Paste the full job description for accurate results.'
        }

    # Gibberish check
    if is_gibberish(text_no_emoji):
        return {
            'prediction': 0, 'probability': 0.02, 'risk_score': 2,
            'top_reasons': [],
            'warning': 'Text appears to be random characters or emojis — not analyzable as a job posting. Please paste real job posting content.'
        }

    # Not a job posting
    if not is_job_posting(text):
        return {
            'prediction': 0, 'probability': 0.05, 'risk_score': 5,
            'top_reasons': [],
            'warning': 'This does not appear to be a job posting. Please paste actual job posting text for accurate analysis.'
        }

    # Step 2: Heuristic signal detection (runs on ALL job postings)
    heuristic_flags = detect_heuristic_signals(text)
    heuristic_score = min(len(heuristic_flags) * 20, 60)  # max 60 from heuristics

    # Step 3: ML model prediction
    ml_score = 0
    reasons = []

    if rf_model is not None and tfidf is not None:
        vec = tfidf.transform([cleaned]).toarray()
        rf_prob = rf_model.predict_proba(vec)[0][1]

        bert_prob = rf_prob
        if USE_BERT and bert_tokenizer and bert_model:
            try:
                inputs = bert_tokenizer(cleaned, return_tensors='pt',
                                        max_length=256, truncation=True, padding=True)
                with torch.no_grad():
                    logits = bert_model(**inputs).logits
                    bert_prob = torch.softmax(logits, dim=1)[0][1].item()
            except Exception:
                bert_prob = rf_prob

        final_prob = 0.4 * rf_prob + 0.6 * bert_prob if USE_BERT else rf_prob
        ml_score = int(final_prob * 100)

        # SHAP reasons
        if explainer is not None:
            try:
                shap_vals_raw = explainer.shap_values(vec, check_additivity=False)
                if isinstance(shap_vals_raw, list):
                    shap_vals = shap_vals_raw[1][0]
                else:
                    shap_vals = shap_vals_raw[0, :, 1]
                feat_names = tfidf.get_feature_names_out()
                nonzero_idx = np.where(vec[0] > 0)[0]
                if len(nonzero_idx) > 0:
                    nonzero_shap = [(i, shap_vals[i]) for i in nonzero_idx]
                    nonzero_shap.sort(key=lambda x: abs(x[1]), reverse=True)
                    reasons = [
                        {'word': feat_names[i], 'impact': round(float(np.clip(sv, -1.0, 1.0)), 4)}
                        for i, sv in nonzero_shap[:15]
                        if feat_names[i] not in STOPWORDS
                        and len(feat_names[i]) > 2
                        and abs(sv) > 0.05  # only show meaningful SHAP values
                    ][:5]
            except Exception:
                pass
    else:
        # fallback: keyword score
        ml_score = heuristic_score

    # Step 4: Combine ML + heuristic scores
    # If heuristics found signals, boost the final score
    if heuristic_flags:
        final_score = max(ml_score, heuristic_score)
        # Blend: take the higher of the two, with a small boost
        final_score = min(int(ml_score * 0.6 + heuristic_score * 0.4) + 10, 100)
    else:
        final_score = ml_score

    prediction = 1 if final_score > 50 else 0

    return {
        'prediction': prediction,
        'probability': round(final_score / 100, 3),
        'risk_score': final_score,
        'top_reasons': reasons,
        'heuristic_flags': heuristic_flags  # passed to risk_scorer for display
    }


def _fallback_analysis(text: str) -> dict:
    """Keyword-based fallback when ML models are not loaded."""
    suspicious_keywords = [
        'work from home', 'earn money', 'no experience needed',
        'apply now', 'whatsapp', 'cash daily', 'urgent hiring',
        'guaranteed income', 'free registration', 'part time job',
        'data entry', 'online job', 'click here', 'limited vacancy',
        'send resume to whatsapp', 'telegram', 'investment required',
        'pay registration fee', 'earn daily', 'earn weekly',
        'no interview', 'direct joining', 'work at home',
        'simple typing job', 'copy paste job', 'mobile job'
    ]
    text_lower = text.lower()
    found_keywords = [kw for kw in suspicious_keywords if kw in text_lower]
    risk_score = min(len(found_keywords) * 15, 100)
    return {
        'prediction': 1 if risk_score > 50 else 0,
        'probability': round(risk_score / 100, 3),
        'risk_score': risk_score,
        'top_reasons': [{'word': kw, 'impact': 0.15} for kw in found_keywords[:5]],
        'heuristic_flags': found_keywords
    }
