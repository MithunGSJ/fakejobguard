"""
backend/services/gemini_analyzer.py

Gemini AI reasoning engine — the most powerful layer of FakeJobGuard.
Understands context like a human: detects if text is even a job posting,
identifies red flags, explains reasoning, and handles gibberish/emoji/Hindi.
"""
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv('GEMINI_API_KEY', '')

# Initialize Gemini
_model = None

def _get_model():
    global _model
    if _model is None and GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
        _model = genai.GenerativeModel('gemini-1.5-flash')
        print('[GeminiAnalyzer] Gemini 1.5 Flash ready')
    return _model


PROMPT_TEMPLATE = """You are an expert fraud detection AI specializing in fake job posting detection in India.

Analyze the following text and respond ONLY with valid JSON (no markdown, no explanation outside JSON).

STEP 1 — Is this actually a job posting?
If the text is gibberish, random words, emojis, greetings, or unrelated content, return:
{{"is_job_posting": false, "reason": "brief explanation of what it is instead", "risk_score": 0, "verdict": "NOT_A_JOB_POSTING", "confidence": 99, "red_flags": [], "green_flags": [], "explanation": "This is not a job posting."}}

STEP 2 — If it IS a job posting, analyze for fraud and return:
{{
  "is_job_posting": true,
  "verdict": "SCAM" or "SUSPICIOUS" or "LEGITIMATE",
  "confidence": 0-100,
  "risk_score": 0-100,
  "red_flags": ["list every specific red flag found — be detailed"],
  "green_flags": ["list legitimacy signals like company name, proper requirements, portal link"],
  "explanation": "One clear sentence summarizing your verdict and main reason"
}}

SCAM indicators to look for:
- Unrealistic salary (Rs. 50,000+/day, guaranteed income)
- WhatsApp/Telegram contact instead of email/portal
- No company name or vague company ("XYZ International", "Global Solutions")  
- Registration fee, security deposit, training fee, kit charges
- "No experience needed" + high salary
- Work from home with guaranteed daily/weekly cash
- Direct mobile numbers (Indian: starts with 6-9, 10 digits)
- Urgency pressure ("apply today", "only 5 seats", "last date")
- Promises: "guaranteed job", "100% placement", "no interview"
- Data entry / copy-paste / typing work with high pay
- Multi-level marketing / referral income

LEGITIMATE indicators:
- Company website or LinkedIn mentioned
- Proper job requirements and qualifications
- Realistic salary for the role
- Application through job portal (Naukri, LinkedIn, Indeed)
- Specific role description with responsibilities
- HR email at company domain

Text to analyze:
\"\"\"
{text}
\"\"\"
"""


def analyze_with_gemini(text: str) -> dict:
    """
    Analyze job posting text using Gemini AI.
    Returns structured result with verdict, risk_score, red_flags, explanation.
    """
    model = _get_model()

    if not model:
        return {
            'available': False,
            'error': 'Gemini API key not configured'
        }

    if not text or len(text.strip()) < 5:
        return {
            'available': True,
            'is_job_posting': False,
            'verdict': 'NOT_A_JOB_POSTING',
            'risk_score': 0,
            'confidence': 99,
            'red_flags': [],
            'green_flags': [],
            'explanation': 'Input is too short to analyze.',
            'reason': 'Text is empty or too short.'
        }

    prompt = PROMPT_TEMPLATE.format(text=text[:3000])  # cap at 3000 chars

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,     # Low temperature = consistent, factual
                max_output_tokens=1024,
            )
        )

        raw = response.text.strip()

        # Strip markdown code blocks if Gemini wraps in ```json
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)

        result = json.loads(raw)
        result['available'] = True
        return result

    except json.JSONDecodeError as e:
        print(f'[GeminiAnalyzer] JSON parse error: {e} | Raw: {raw[:200]}')
        return {
            'available': True,
            'error': 'Could not parse Gemini response',
            'is_job_posting': None,
            'risk_score': None
        }
    except Exception as e:
        print(f'[GeminiAnalyzer] Error: {e}')
        return {
            'available': False,
            'error': str(e)
        }
