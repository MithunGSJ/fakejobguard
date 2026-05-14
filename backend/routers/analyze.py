# backend/routers/analyze.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.text_analyzer import analyze_text
from services.image_analyzer import analyze_image
from services.url_checker import check_url_safety
from services.risk_scorer import calculate_final_risk
from services.gemini_analyzer import analyze_with_gemini

router = APIRouter(prefix='/analyze', tags=['Analysis'])


class TextRequest(BaseModel):
    text: str


class URLRequest(BaseModel):
    url: str


def _merge_gemini(text_result: dict, gemini_result: dict) -> dict:
    """
    Merge Gemini AI result into text_result.
    Gemini overrides the risk score if it's available and confident.
    """
    if not gemini_result.get('available'):
        return text_result

    # If Gemini says it's NOT a job posting, override entirely
    if gemini_result.get('is_job_posting') is False:
        return {
            **text_result,
            'risk_score': 0,
            'probability': 0.01,
            'prediction': 0,
            'warning': gemini_result.get('reason', 'Not a job posting'),
            'gemini': gemini_result
        }

    # If Gemini analyzed a real job posting, blend its score
    gemini_score = gemini_result.get('risk_score')
    if gemini_score is not None:
        ml_score = text_result.get('risk_score', 0)
        # Blend: 50% Gemini (contextual AI) + 50% ML (trained model)
        blended = int(ml_score * 0.4 + gemini_score * 0.6)
        text_result['risk_score'] = blended
        text_result['probability'] = round(blended / 100, 3)
        text_result['prediction'] = 1 if blended > 50 else 0

    # Add Gemini red flags to heuristic_flags
    gemini_flags = gemini_result.get('red_flags', [])
    existing_flags = text_result.get('heuristic_flags', [])
    text_result['heuristic_flags'] = existing_flags + gemini_flags
    text_result['gemini'] = {
        'verdict': gemini_result.get('verdict'),
        'confidence': gemini_result.get('confidence'),
        'explanation': gemini_result.get('explanation'),
        'red_flags': gemini_flags,
        'green_flags': gemini_result.get('green_flags', [])
    }

    return text_result


@router.post('/text')
def analyze_text_endpoint(req: TextRequest):
    """Analyze job posting text — ML + Gemini AI + heuristic rules."""
    text_result = analyze_text(req.text)

    # Only run Gemini if text passed basic validation (no 'warning' that blocked it)
    if not text_result.get('warning') or text_result.get('risk_score', 0) > 0:
        gemini_result = analyze_with_gemini(req.text)
        text_result = _merge_gemini(text_result, gemini_result)

    final = calculate_final_risk(text_result=text_result)
    return {
        'text_analysis': text_result,
        'final_result': final
    }


@router.post('/image')
async def analyze_image_endpoint(file: UploadFile = File(...)):
    """Analyze a job ad screenshot/image for suspicious visual patterns."""
    image_bytes = await file.read()
    image_result = analyze_image(image_bytes)
    final = calculate_final_risk(image_result=image_result)
    return {
        'image_analysis': image_result,
        'final_result': final
    }


@router.post('/url')
def analyze_url_endpoint(req: URLRequest):
    """Check a job posting URL for safety."""
    url_result = check_url_safety(req.url)
    final = calculate_final_risk(url_result=url_result)
    return {
        'url_analysis': url_result,
        'final_result': final
    }


@router.post('/full')
async def analyze_full(
    text: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Full analysis — text + image + URL with Gemini AI reasoning.
    At least one input must be provided.
    """
    if not text and not url and not file:
        raise HTTPException(
            status_code=422,
            detail='At least one input is required: text, url, or image file.'
        )

    text_result = None
    if text:
        text_result = analyze_text(text)
        # Run Gemini on text if it passed basic validation
        gemini_result = analyze_with_gemini(text)
        text_result = _merge_gemini(text_result, gemini_result)

    image_result = analyze_image(await file.read()) if file else None
    url_result   = check_url_safety(url) if url else None

    final = calculate_final_risk(text_result, image_result, url_result)
    return {
        'text_analysis': text_result,
        'image_analysis': image_result,
        'url_analysis': url_result,
        'final_result': final
    }
