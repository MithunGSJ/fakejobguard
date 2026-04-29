# ============================================================
# FakeJobGuard — BERT Training on Google Colab (GPU)
# Run this in Google Colab for ~20 min training vs 2 hrs CPU
# ============================================================

# ---- CELL 1: Check GPU ----
import torch
print(f"GPU available: {torch.cuda.is_available()}")
print(f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
# Should print: GPU available: True, Device: Tesla T4

# ---- CELL 2: Install dependencies ----
# !pip install transformers scikit-learn pandas numpy

# ---- CELL 3: Upload your dataset ----
from google.colab import files
print("Upload your clean_data.csv file now...")
uploaded = files.upload()  # A file picker will appear — select clean_data.csv

# ---- CELL 4: Load data ----
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

df = pd.read_csv('clean_data.csv')
print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"Class distribution:\n{df['fraudulent'].value_counts()}")

texts = df['cleaned_text'].tolist()
labels = df['fraudulent'].tolist()

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)
print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

# ---- CELL 5: Create PyTorch Dataset ----
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup
from sklearn.metrics import classification_report

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Training on: {device}")

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

class JobDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

train_dataset = JobDataset(X_train, y_train, tokenizer)
test_dataset  = JobDataset(X_test,  y_test,  tokenizer)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
test_loader  = DataLoader(test_dataset,  batch_size=16, shuffle=False)

print(f"Train batches: {len(train_loader)}, Test batches: {len(test_loader)}")

# ---- CELL 6: Load model and set up training ----
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
model = model.to(device)

EPOCHS = 3
optimizer = AdamW(model.parameters(), lr=2e-5)
total_steps = len(train_loader) * EPOCHS
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=total_steps // 10,
    num_training_steps=total_steps
)

print(f"Total training steps: {total_steps}")
print("Model ready. Starting training...")

# ---- CELL 7: Training loop ----
import time

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    start = time.time()

    for batch_idx, batch in enumerate(train_loader):
        optimizer.zero_grad()

        input_ids      = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels_batch   = batch['labels'].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels_batch)
        loss = outputs.loss
        total_loss += loss.item()

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()

        if (batch_idx + 1) % 50 == 0:
            elapsed = time.time() - start
            avg_loss = total_loss / (batch_idx + 1)
            print(f"Epoch {epoch+1}/{EPOCHS} | Batch {batch_idx+1}/{len(train_loader)} | Loss: {avg_loss:.4f} | Time: {elapsed:.0f}s")

    avg_epoch_loss = total_loss / len(train_loader)
    print(f"\n✅ Epoch {epoch+1} complete | Avg Loss: {avg_epoch_loss:.4f}\n")

# ---- CELL 8: Evaluate ----
model.eval()
all_preds, all_labels = [], []

with torch.no_grad():
    for batch in test_loader:
        input_ids      = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(batch['labels'].numpy())

print("\n📊 Classification Report:")
print(classification_report(all_labels, all_preds, target_names=['Real', 'Fake']))

# ---- CELL 9: Save model and download ----
import os
import zipfile

save_path = '/content/bert_model'
os.makedirs(save_path, exist_ok=True)
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print(f"Model saved to {save_path}")
print(f"Files: {os.listdir(save_path)}")

# Zip and download
zip_path = '/content/bert_model.zip'
with zipfile.ZipFile(zip_path, 'w') as zf:
    for fname in os.listdir(save_path):
        zf.write(os.path.join(save_path, fname), fname)
print(f"Zipped: {zip_path}")

from google.colab import files
files.download(zip_path)
print("✅ bert_model.zip downloaded to your computer!")
print("Extract it to: C:\\Users\\OM\\Documents\\JOB_FAKING\\backend\\models\\bert_model\\")
