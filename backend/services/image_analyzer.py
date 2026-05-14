# backend/services/image_analyzer.py
"""
Image analyzer using OpenAI's CLIP model.
CLIP is loaded lazily — only when an image is actually analyzed.
This allows the backend to start without torch/transformers installed.
"""
import io

# Global model references — loaded once on first use
_clip_model = None
_clip_processor = None
_CLIP_AVAILABLE = None  # None = not checked yet

# These are the text prompts we compare the image against
SUSPICIOUS_PROMPTS = [
    'a WhatsApp scam message with fake job offer and unrealistic salary',
    'a fraudulent work from home job posting promising easy money',
    'a spam advertisement asking for registration fee or personal bank details',
    'a low quality screenshot of a suspicious job offer',
]

LEGIT_PROMPTS = [
    'an official campus placement notice from a college or university',
    'a professional company job advertisement with company logo',
    'a legitimate corporate recruitment document or hiring poster',
    'a formal job circular issued by a government or reputed organization',
]


def _load_clip():
    """Load CLIP model lazily on first use."""
    global _clip_model, _clip_processor, _CLIP_AVAILABLE
    if _CLIP_AVAILABLE is not None:
        return _CLIP_AVAILABLE
    try:
        from transformers import CLIPProcessor, CLIPModel
        _clip_model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
        _clip_processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
        _clip_model.eval()
        _CLIP_AVAILABLE = True
        print('[ImageAnalyzer] CLIP model loaded successfully')
    except Exception as e:
        _CLIP_AVAILABLE = False
        print(f'[ImageAnalyzer] CLIP not available: {e}')
    return _CLIP_AVAILABLE


def analyze_image(image_bytes: bytes) -> dict:
    """
    Takes image as bytes, returns analysis dict with:
    - risk_score: int (0-100)
    - flags: list of suspicious findings
    - confidence: float
    """
    # Try CLIP analysis
    if _load_clip():
        return _clip_analyze(image_bytes)
    else:
        return _fallback_image_analysis(image_bytes)


def _clip_analyze(image_bytes: bytes) -> dict:
    """Full CLIP-based image analysis."""
    try:
        import torch
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        flags = []
        risk = 0

        all_prompts = SUSPICIOUS_PROMPTS + LEGIT_PROMPTS
        inputs = _clip_processor(
            text=all_prompts,
            images=image,
            return_tensors='pt',
            padding=True
        )

        with torch.no_grad():
            outputs = _clip_model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)[0].tolist()

        suspicious_scores = probs[:len(SUSPICIOUS_PROMPTS)]
        legit_scores = probs[len(SUSPICIOUS_PROMPTS):]

        max_suspicious = max(suspicious_scores)
        max_legit = max(legit_scores)
        suspicious_margin = max_suspicious - max_legit

        # Only flag if suspicious score is clearly dominant (not just barely above threshold)
        # Requires: suspicious > 0.5 AND suspicious > legit by at least 0.15 margin
        if max_suspicious > 0.5 and suspicious_margin > 0.15:
            susp_idx = suspicious_scores.index(max_suspicious)
            flags.append(f'Visual pattern suggests possible scam: {SUSPICIOUS_PROMPTS[susp_idx]}')
            risk += int(max_suspicious * 60)
        elif max_legit > max_suspicious:
            # Legit wins — positive signal, reduce risk
            risk = max(0, risk - 10)

        # Check image dimensions — very small images are suspicious
        w, h = image.size
        if w < 200 or h < 200:
            flags.append(
                f'Very small image ({w}x{h}px) — may be a copied thumbnail'
            )
            risk += 15

        risk = min(risk, 100)
        return {
            'risk_score': risk,
            'flags': flags,
            'confidence': round(max_suspicious, 3)
        }
    except Exception as e:
        return {
            'risk_score': 0,
            'flags': [f'Image analysis failed: {str(e)}'],
            'confidence': 0
        }


def _fallback_image_analysis(image_bytes: bytes) -> dict:
    """
    Fallback when CLIP is not available.
    Does basic image size and format checks.
    """
    try:
        from PIL import Image
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        flags = []
        risk = 0

        w, h = image.size
        if w < 200 or h < 200:
            flags.append(
                f'Very small image ({w}x{h}px) — may be a copied thumbnail'
            )
            risk += 20

        flags.append(
            'CLIP model not available — only basic image checks performed. '
            'Install transformers and torch for full image analysis.'
        )

        return {
            'risk_score': min(risk, 100),
            'flags': flags,
            'confidence': 0.0
        }
    except Exception as e:
        return {
            'risk_score': 0,
            'flags': [f'Image analysis failed: {str(e)}'],
            'confidence': 0
        }
