"""
Model downloader — runs at startup on Render if model files are missing.
Models are hosted on Hugging Face Hub under your username.
Set HF_MODEL_REPO env var to your repo, e.g. 'yourname/fakejobguard-models'
"""
import os
import urllib.request

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

# Map: local filename -> Hugging Face raw file URL
# Fill in your HF repo URL after uploading
HF_REPO = os.getenv('HF_MODEL_REPO', '')

MODEL_FILES = {
    'rf_model.pkl': f'https://huggingface.co/{HF_REPO}/resolve/main/rf_model.pkl',
    'tfidf_vectorizer.pkl': f'https://huggingface.co/{HF_REPO}/resolve/main/tfidf_vectorizer.pkl',
    'shap_explainer.pkl': f'https://huggingface.co/{HF_REPO}/resolve/main/shap_explainer.pkl',
}


def download_models():
    if not HF_REPO:
        print('[ModelDownloader] HF_MODEL_REPO not set — skipping download')
        return

    for filename, url in MODEL_FILES.items():
        dest = os.path.join(MODELS_DIR, filename)
        if os.path.exists(dest):
            print(f'[ModelDownloader] {filename} already exists — skipping')
            continue
        print(f'[ModelDownloader] Downloading {filename} ...')
        try:
            urllib.request.urlretrieve(url, dest)
            size_mb = os.path.getsize(dest) / 1024 / 1024
            print(f'[ModelDownloader] {filename} downloaded ({size_mb:.1f} MB)')
        except Exception as e:
            print(f'[ModelDownloader] Failed to download {filename}: {e}')


if __name__ == '__main__':
    download_models()
