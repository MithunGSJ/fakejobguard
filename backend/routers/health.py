# backend/routers/health.py
import os
from fastapi import APIRouter

router = APIRouter()


@router.get('/health')
def health():
    """Health check — shows which AI models and services are active."""
    gemini_configured = bool(os.getenv('GEMINI_API_KEY', ''))
    safe_browsing_configured = bool(os.getenv('GOOGLE_SAFE_BROWSING_KEY', ''))

    return {
        'status': 'ok',
        'message': 'FakeJobGuard API is running',
        'services': {
            'gemini_ai': 'configured' if gemini_configured else 'NOT configured — add GEMINI_API_KEY env var',
            'safe_browsing': 'configured' if safe_browsing_configured else 'NOT configured',
            'ml_models': 'loaded',
        }
    }
