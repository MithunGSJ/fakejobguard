# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.analyze import router as analyze_router
from routers.health import router as health_router

app = FastAPI(
    title='Fake Job Detector API',
    description='Detects fake job postings using NLP, Vision, and URL analysis',
    version='1.0.0'
)

# CORS — allows React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # In production: replace with your Vercel URL
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
