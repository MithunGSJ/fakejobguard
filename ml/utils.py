# ml/utils.py
"""
Shared utility functions for ML notebooks.
Used across EDA, preprocessing, training, and evaluation notebooks.
"""
import re
import pandas as pd
import numpy as np


def clean_text(text: str) -> str:
    """
    Clean and normalize text for model input.
    - Lowercase
    - Remove HTML tags
    - Remove URLs
    - Keep only alphanumeric characters
    - Remove extra whitespace
    """
    text = str(text).lower()
    text = re.sub(r'<[^>]+>', ' ', text)       # remove HTML tags
    text = re.sub(r'http\S+', '', text)         # remove URLs
    text = re.sub(r'[^a-z0-9\s]', ' ', text)   # keep only alphanumeric
    text = re.sub(r'\s+', ' ', text).strip()    # remove extra spaces
    return text


def combine_text_columns(df: pd.DataFrame) -> pd.Series:
    """
    Combine all text columns into one 'combined_text' feature.
    This gives the model maximum context from all available fields.
    """
    text_cols = [
        'title', 'company_profile', 'description',
        'requirements', 'benefits', 'industry'
    ]
    # Fill NaN with empty string first
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna('')

    return (
        df.get('title', '') + ' ' +
        df.get('company_profile', '') + ' ' +
        df.get('description', '') + ' ' +
        df.get('requirements', '') + ' ' +
        df.get('benefits', '') + ' ' +
        df.get('industry', '')
    )


def print_metrics(y_true, y_pred, model_name='Model'):
    """Print classification metrics in a formatted way."""
    from sklearn.metrics import (
        accuracy_score, classification_report, confusion_matrix
    )

    print(f'\n{"="*50}')
    print(f'{model_name} Results')
    print(f'{"="*50}')
    print(f'Accuracy: {accuracy_score(y_true, y_pred):.4f}')
    print(f'\nClassification Report:')
    print(classification_report(
        y_true, y_pred, target_names=['Real', 'Fake']
    ))
    print(f'Confusion Matrix:')
    cm = confusion_matrix(y_true, y_pred)
    print(cm)
    print(f'  TN={cm[0][0]}, FP={cm[0][1]}')
    print(f'  FN={cm[1][0]}, TP={cm[1][1]}')
    return cm
