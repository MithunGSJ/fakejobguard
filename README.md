# 🛡️ FakeJobGuard — AI-Powered Fake Job Posting Detection System

> Detect fake job postings on LinkedIn, Naukri, Indeed, Facebook & Instagram using AI

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge)](https://your-app.vercel.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react)](https://reactjs.org/)
[![BERT](https://img.shields.io/badge/BERT-FF6F00?style=for-the-badge)](https://huggingface.co/bert-base-uncased)

## 📋 About

FakeJobGuard is a web application that uses **Artificial Intelligence** (Machine Learning + NLP + Computer Vision) to automatically detect whether a job posting is real or fake. The system works on both **job board posts** (LinkedIn, Naukri, Internshala) and **social media job ads** (Facebook, Instagram, Meta Ads).

### 3 Input Types
| Input Type | What User Does | AI Analysis | Output |
|-----------|---------------|-------------|--------|
| 📝 **Text** | Paste job post text | BERT NLP classifier | Risk Score + SHAP Reasons |
| 🖼️ **Image** | Upload ad screenshot | CLIP vision model | Suspicious Visual Flags |
| 🔗 **URL** | Paste job/ad URL | Domain age, SSL, Safe Browsing | Safe / Unsafe flag |

## 🏗️ System Architecture

```
User Input → React Frontend → FastAPI Backend → AI Modules → Risk Scorer → Response
                                                  ├── BERT (Text NLP)
                                                  ├── CLIP (Image Analysis)
                                                  └── URL Checker (Safety)
```

**Risk Score Weights**: Text 60% + Image 25% + URL 15% = Final Score (0-100)

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| ML (Text) | scikit-learn, transformers, PyTorch, SHAP | TF-IDF + RF baseline, BERT classifier, explainability |
| ML (Image) | CLIP (OpenAI), Pillow | Vision-based ad analysis |
| URL Check | requests, python-whois | Google Safe Browsing, domain age |
| Backend | FastAPI, uvicorn, pydantic | REST API for ML model serving |
| Frontend | React 18, Axios, TailwindCSS | Interactive web interface |
| Deployment | Render (backend), Vercel (frontend) | Cloud hosting |

## 🚀 Features

- ✅ **Text Analysis**: BERT-powered NLP detects suspicious language patterns
- ✅ **Image Detection**: CLIP vision model identifies fake ad screenshots
- ✅ **URL Verification**: Checks domain age, SSL, Safe Browsing database
- ✅ **SHAP Explainability**: Shows exactly WHICH words caused the flag
- ✅ **Risk Scoring**: Combined 0-100 score with color-coded labels
- ✅ **Meta Ad Library**: Checks Facebook/Instagram ad metadata
- ✅ **Real-time Analysis**: Results in under 5 seconds
- ✅ **Responsive UI**: Works on desktop and mobile

## 📦 How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000/docs for Swagger API documentation.

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open http://localhost:5173 in your browser.

### ML Model Training
```bash
# 1. Download EMSCAD dataset from Kaggle
# Place at: datasets/raw/fake_job_postings.csv

# 2. Run notebooks in order:
# ml/01_eda.ipynb
# ml/02_preprocessing.ipynb
# ml/03_baseline_model.ipynb
# ml/04_bert_model.ipynb
# ml/05_shap_explainability.ipynb
```

## 📡 API Documentation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/analyze/text` | POST | Analyze text `{"text": "..."}` |
| `/analyze/image` | POST | Analyze image (multipart/form-data) |
| `/analyze/url` | POST | Check URL `{"url": "..."}` |
| `/analyze/full` | POST | Full analysis (text + image + url) |

### Example Request
```bash
curl -X POST http://localhost:8000/analyze/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Work from home earn 50000 daily no experience needed"}'
```

## 📊 Dataset

- **EMSCAD** (Employment Scam Aegean Dataset) from Kaggle
- 17,880 rows, 18 columns
- Class distribution: 17,014 real (95.16%) / 866 fake (4.84%)

## 🎯 Model Accuracy

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| TF-IDF + Random Forest | ~98% | 0.97 | 0.98 | 0.97 |
| Fine-tuned BERT | ~99% | 0.99 | 0.99 | 0.99 |
| Ensemble (RF + BERT) | 99%+ | 0.99 | 0.99 | 0.99 |

## 👥 Team Members & Roles

| Role | Responsibilities |
|------|-----------------|
| P1 — ML Engineer (Text) | EMSCAD dataset, preprocessing, ADASYN, TF-IDF+RF, BERT, SHAP |
| P2 — ML Engineer (Image+URL) | CLIP image analyzer, URL checker, Meta API, risk scorer |
| P3 — Backend Developer | FastAPI, endpoints, CORS, Render deployment |
| P4 — Frontend Developer | React, TailwindCSS, components, Vercel deployment |

## 📚 References

1. EMSCAD Dataset — Kaggle
2. BERT: Pre-training of Deep Bidirectional Transformers
3. CLIP: Learning Transferable Visual Models
4. SHAP: A Unified Approach to Interpreting Model Predictions

---

Built with ❤️ — Fake Job Posting Detection System
