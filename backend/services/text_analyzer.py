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

# Load Random Forest model and TF-IDF vectorizer
RF_MODEL_PATH = os.path.join(MODELS_DIR, 'rf_model.pkl')
TFIDF_PATH = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')
SHAP_PATH = os.path.join(MODELS_DIR, 'shap_explainer.pkl')

# Initialize as None — will load if files exist
rf_model = None
tfidf = None
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

# Load BERT model (optional — use if available)
BERT_PATH = os.path.join(MODELS_DIR, 'bert_model')
USE_BERT = False
bert_tokenizer = None
bert_model = None

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


def clean_text(text: str) -> str:
    """Clean and normalize text for model input."""
    text = str(text).lower()
    text = re.sub(r'<[^>]+>', ' ', text)       # remove HTML tags
    text = re.sub(r'http\S+', '', text)         # remove URLs
    text = re.sub(r'[^a-z0-9\s]', ' ', text)   # keep only alphanumeric
    text = re.sub(r'\s+', ' ', text).strip()    # remove extra spaces
    return text


def analyze_text(text: str) -> dict:
    """
    Analyzes job posting text for fraud signals.

    Returns dict with:
    - prediction: int (0=real, 1=fake)
    - probability: float (0-1)
    - risk_score: int (0-100)
    - top_reasons: list of {word, impact} dicts from SHAP
    """
    cleaned = clean_text(text)

    # If models aren't loaded, use keyword-based fallback
    if rf_model is None or tfidf is None:
        return _fallback_analysis(cleaned)

    # Random Forest prediction
    vec = tfidf.transform([cleaned]).toarray()
    rf_prob = rf_model.predict_proba(vec)[0][1]  # prob of being fake
    rf_pred = 1 if rf_prob > 0.5 else 0

    # BERT prediction (if model exists)
    bert_prob = rf_prob  # default to RF
    if USE_BERT and bert_tokenizer and bert_model:
        try:
            inputs = bert_tokenizer(
                cleaned, return_tensors='pt',
                max_length=256, truncation=True, padding=True
            )
            with torch.no_grad():
                logits = bert_model(**inputs).logits
                bert_prob = torch.softmax(logits, dim=1)[0][1].item()
        except Exception:
            bert_prob = rf_prob  # fallback to RF on error

    # Ensemble: weighted average (BERT gets more weight)
    final_prob = 0.4 * rf_prob + 0.6 * bert_prob if USE_BERT else rf_prob
    final_pred = 1 if final_prob > 0.5 else 0

    # SHAP: get top reasons — only show words that actually appear in the input
    reasons = []
    if explainer is not None:
        try:
            shap_vals_raw = explainer.shap_values(vec, check_additivity=False)
            # Handle both old SHAP (list of arrays per class)
            # and new SHAP 0.43+ (single 3D array: samples x features x classes)
            if isinstance(shap_vals_raw, list):
                shap_vals = shap_vals_raw[1][0]
            else:
                shap_vals = shap_vals_raw[0, :, 1]
            feat_names = tfidf.get_feature_names_out()

            # Only consider features (words/ngrams) that are NON-ZERO in the input
            # This ensures we only show words actually present in the text
            nonzero_idx = np.where(vec[0] > 0)[0]
            if len(nonzero_idx) > 0:
                nonzero_shap = [(i, shap_vals[i]) for i in nonzero_idx]
                nonzero_shap.sort(key=lambda x: abs(x[1]), reverse=True)
                reasons = [
                    {
                        'word': feat_names[i],
                        # Clamp to [-1, 1] to prevent display of huge floats
                        'impact': round(float(np.clip(shap_val, -1.0, 1.0)), 4)
                    }
                    for i, shap_val in nonzero_shap[:5]
                ]
        except Exception:
            pass

    return {
        'prediction': final_pred,
        'probability': round(float(final_prob), 3),
        'risk_score': int(final_prob * 100),
        'top_reasons': reasons
    }


def _fallback_analysis(text: str) -> dict:
    """
    Keyword-based fallback when ML models are not loaded.
    Uses heuristic rules to detect suspicious patterns.
    """
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
    prediction = 1 if risk_score > 50 else 0

    reasons = [
        {'word': kw, 'impact': 0.15}
        for kw in found_keywords[:5]
    ]

    return {
        'prediction': prediction,
        'probability': round(risk_score / 100, 3),
        'risk_score': risk_score,
        'top_reasons': reasons
    }
