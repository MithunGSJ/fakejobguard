# backend/routers/health.py
from fastapi import APIRouter

router = APIRouter()


@router.get('/health')
def health():
    """Health check endpoint — verify the API is running."""
    return {
        'status': 'ok',
        'message': 'Fake Job Detector API is running'
    }
