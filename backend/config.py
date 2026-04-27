# backend/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GOOGLE_SAFE_BROWSING_KEY = os.getenv('GOOGLE_SAFE_BROWSING_KEY', '')

# Model paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# App settings
APP_TITLE = 'Fake Job Detector API'
APP_VERSION = '1.0.0'
APP_DESCRIPTION = 'Detects fake job postings using NLP, Vision, and URL analysis'

# CORS
ALLOWED_ORIGINS = ['*']  # In production: replace with your Vercel URL
