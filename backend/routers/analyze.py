# backend/routers/analyze.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.text_analyzer import analyze_text
from services.image_analyzer import analyze_image
from services.url_checker import check_url_safety
from services.risk_scorer import calculate_final_risk

router = APIRouter(prefix='/analyze', tags=['Analysis'])


class TextRequest(BaseModel):
    text: str


class URLRequest(BaseModel):
    url: str


@router.post('/text')
def analyze_text_endpoint(req: TextRequest):
    """Analyze job posting text for fraud indicators."""
    text_result = analyze_text(req.text)
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
    """Check a job posting URL for safety (phishing, domain age, redirects)."""
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
    Full analysis — analyze text, image, and URL all at once.
    At least one input must be provided.
    Returns combined risk score from all provided inputs.
    """
    # TC-07: Validate at least one input is provided
    if not text and not url and not file:
        raise HTTPException(
            status_code=422,
            detail="At least one input is required: text, url, or image file."
        )
    text_result = analyze_text(text) if text else None
    image_result = analyze_image(await file.read()) if file else None
    url_result = check_url_safety(url) if url else None
    final = calculate_final_risk(text_result, image_result, url_result)
    return {
        'text_analysis': text_result,
        'image_analysis': image_result,
        'url_analysis': url_result,
        'final_result': final
    }
