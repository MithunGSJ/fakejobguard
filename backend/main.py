# backend/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.analyze import router as analyze_router
from routers.health import router as health_router
from download_models import download_models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Download model files from HF Hub if missing (runs on Render startup)
    download_models()
    yield

app = FastAPI(
    title='Fake Job Detector API',
    description='Detects fake job postings using NLP, Vision, and URL analysis',
    version='1.0.0',
    lifespan=lifespan
)

# Allow frontend origin (Vercel + local dev)
ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3000',
    os.getenv('FRONTEND_URL', '*'),  # Set FRONTEND_URL=https://yourapp.vercel.app on Render
]

# CORS — allows React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include routers
app.include_router(health_router)
app.include_router(analyze_router)


@app.get('/')
def root():
    return {
        'message': 'Fake Job Detector API',
        'docs': '/docs',
        'health': '/health'
    }


# Run with: uvicorn main:app --reload --port 8000
