"""
BERT fine-tuning for suicidal ideation detection using HuggingFace Transformers.
Uses a smaller sample (20K) due to compute constraints.
"""

import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    AdamW,
    get_linear_schedule_with_warmup,
)
from sklearn.metrics import f1_score

from evaluate import compute_metrics, print_report, plot_confusion_matrix, save_metrics

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

MODEL_NAME  = "bert-base-uncased"
MAX_LEN     = 128
BATCH_SIZE  = 16
EPOCHS      = 3
DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class SuicideDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=MAX_LEN):
        self.texts     = list(texts)
        self.labels    = list(labels)
        self.tokenizer = tokenizer
        self.max_len   = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids":      encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "label":          torch.tensor(self.labels[idx], dtype=torch.long),
        }


def train_epoch(model, loader, optimizer, scheduler):
    model.train()
    total_loss = 0
    for batch in loader:
        input_ids      = batch["input_ids"].to(DEVICE)
        attention_mask = batch["attention_mask"].to(DEVICE)
        labels         = batch["label"].to(DEVICE)

        optimizer.zero_grad()
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total_loss += loss.item()
    return total_loss / len(loader)


def eval_epoch(model, loader):
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for batch in loader:
            input_ids      = batch["input_ids"].to(DEVICE)
            attention_mask = batch["attention_mask"].to(DEVICE)
            labels         = batch["label"].to(DEVICE)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    return np.array(all_labels), np.array(all_preds)


def train_and_evaluate(X_train, X_test, y_train, y_test):
    """Fine-tune BERT and evaluate."""
    print(f"\n[BERT] Using device: {DEVICE}")
    print(f"[BERT] Train size: {len(X_train):,} | Test size: {len(X_test):,}")

    print("[BERT] Loading tokenizer and model...")
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
    model     = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    model     = model.to(DEVICE)

    train_dataset = SuicideDataset(X_train.tolist(), y_train.tolist(), tokenizer)
    test_dataset  = SuicideDataset(X_test.tolist(),  y_test.tolist(),  tokenizer)
    train_loader  = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader   = DataLoader(test_dataset,  batch_size=BATCH_SIZE)

    optimizer = AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(0.1 * total_steps),
        num_training_steps=total_steps,
    )

    best_f1   = 0
    best_preds = None

    for epoch in range(1, EPOCHS + 1):
        avg_loss = train_epoch(model, train_loader, optimizer, scheduler)
        y_true, y_pred = eval_epoch(model, test_loader)
        f1 = f1_score(y_true, y_pred)
        print(f"  Epoch {epoch}/{EPOCHS} | Loss: {avg_loss:.4f} | Val F1: {f1:.4f}")

        if f1 > best_f1:
            best_f1    = f1
            best_preds = y_pred
            model.save_pretrained(os.path.join(MODELS_DIR, "bert_finetuned"))
            tokenizer.save_pretrained(os.path.join(MODELS_DIR, "bert_finetuned"))

    print(f"\n[BERT] Best Val F1: {best_f1:.4f}")
    metrics = compute_metrics(y_test, best_preds, model_name="BERT")
    print_report(y_test, best_preds, model_name="BERT")
    plot_confusion_matrix(y_test, best_preds, model_name="BERT")
    save_metrics(metrics)

    return metrics


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from preprocess import load_data, preprocess, split_data

    print("Loading data (20K sample for BERT)...")
    df = load_data(sample_size=20000)
    df = preprocess(df, full_clean=False)   # Keep natural text for BERT
    X_train, X_test, y_train, y_test = split_data(df)
    train_and_evaluate(X_train, X_test, y_train, y_test)
