"""
Model loader — checks if model files exist on startup.
Models are now committed directly to the GitHub repo.
"""
import os

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')


def download_models():
    """Check model files exist and log status."""
    files = ['rf_model.pkl', 'tfidf_vectorizer.pkl', 'shap_explainer.pkl']
    for f in files:
        path = os.path.join(MODELS_DIR, f)
        if os.path.exists(path):
            size_mb = round(os.path.getsize(path) / 1024 / 1024, 1)
            print(f'[ModelLoader] {f} found ({size_mb} MB)')
        else:
            print(f'[ModelLoader] WARNING: {f} not found in {MODELS_DIR}')


if __name__ == '__main__':
    download_models()
