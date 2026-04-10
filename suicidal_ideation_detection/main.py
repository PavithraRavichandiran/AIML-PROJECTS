"""
main.py — Full pipeline orchestrator for Suicidal Ideation Detection.

Stages:
  1. EDA
  2. ML models  (Logistic Regression, Naive Bayes, Linear SVM)
  3. DL models  (LSTM, BiLSTM)
  4. BERT       (fine-tuned transformer)
  5. Model comparison table
  6. LLM explanations (optional, requires ANTHROPIC_API_KEY)

Usage:
    python main.py              # Run all stages
    python main.py --skip-bert  # Skip BERT (faster)
    python main.py --skip-dl    # Skip DL models
"""

import sys
import os
import argparse

# Make src/ importable
SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
sys.path.insert(0, SRC_DIR)

from preprocess   import load_data, preprocess, split_data
from eda          import run_eda
from ml_models    import train_and_evaluate as ml_train
from dl_models    import train_and_evaluate as dl_train
from bert_model   import train_and_evaluate as bert_train
from llm_explainer import batch_explain
from evaluate      import comparison_table


def parse_args():
    parser = argparse.ArgumentParser(description="Suicidal Ideation Detection Pipeline")
    parser.add_argument("--skip-dl",   action="store_true", help="Skip deep learning (LSTM/BiLSTM)")
    parser.add_argument("--skip-bert", action="store_true", help="Skip BERT fine-tuning")
    parser.add_argument("--skip-llm",  action="store_true", help="Skip LLM explanations")
    parser.add_argument("--ml-sample",   type=int, default=100000, help="Samples for ML (default 100k)")
    parser.add_argument("--dl-sample",   type=int, default=50000,  help="Samples for DL (default 50k)")
    parser.add_argument("--bert-sample", type=int, default=20000,  help="Samples for BERT (default 20k)")
    return parser.parse_args()


def main():
    args = parse_args()
    print("\n" + "="*60)
    print("  SUICIDAL IDEATION DETECTION — FULL PIPELINE")
    print("="*60)

    # -------------------------------------------------------
    # STAGE 1: EDA
    # -------------------------------------------------------
    print("\n[Stage 1/5] Exploratory Data Analysis")
    eda_df = load_data(sample_size=50000)
    run_eda(eda_df)
    del eda_df

    # -------------------------------------------------------
    # STAGE 2: ML Models
    # -------------------------------------------------------
    print(f"\n[Stage 2/5] Machine Learning Models  (sample={args.ml_sample:,})")
    ml_df = load_data(sample_size=args.ml_sample)
    ml_df = preprocess(ml_df, full_clean=True)
    X_train_ml, X_test_ml, y_train_ml, y_test_ml = split_data(ml_df)
    ml_train(X_train_ml, X_test_ml, y_train_ml, y_test_ml)
    del ml_df, X_train_ml, X_test_ml, y_train_ml, y_test_ml

    # -------------------------------------------------------
    # STAGE 3: Deep Learning Models
    # -------------------------------------------------------
    if not args.skip_dl:
        print(f"\n[Stage 3/5] Deep Learning Models  (sample={args.dl_sample:,})")
        dl_df = load_data(sample_size=args.dl_sample)
        dl_df = preprocess(dl_df, full_clean=False)   # keep stopwords for context
        X_train_dl, X_test_dl, y_train_dl, y_test_dl = split_data(dl_df)
        dl_train(X_train_dl, X_test_dl, y_train_dl, y_test_dl)
        del dl_df, X_train_dl, X_test_dl, y_train_dl, y_test_dl
    else:
        print("\n[Stage 3/5] Deep Learning — SKIPPED")

    # -------------------------------------------------------
    # STAGE 4: BERT
    # -------------------------------------------------------
    if not args.skip_bert:
        print(f"\n[Stage 4/5] BERT Fine-tuning  (sample={args.bert_sample:,})")
        bert_df = load_data(sample_size=args.bert_sample)
        bert_df = preprocess(bert_df, full_clean=False)  # BERT handles own tokenisation
        X_train_b, X_test_b, y_train_b, y_test_b = split_data(bert_df)
        bert_train(X_train_b, X_test_b, y_train_b, y_test_b)

        # LLM Explanations on BERT test predictions
        if not args.skip_llm:
            print("\n[Stage 4b] LLM Explanations for high-risk posts...")
            try:
                import torch
                from transformers import BertTokenizer, BertForSequenceClassification
                from bert_model import eval_epoch, SuicideDataset, DEVICE, BATCH_SIZE
                from torch.utils.data import DataLoader

                tok  = BertTokenizer.from_pretrained(os.path.join("models", "bert_finetuned"))
                mdl  = BertForSequenceClassification.from_pretrained(
                    os.path.join("models", "bert_finetuned")
                ).to(DEVICE)
                ds   = SuicideDataset(X_test_b.tolist(), y_test_b.tolist(), tok)
                ldr  = DataLoader(ds, batch_size=BATCH_SIZE)
                _, preds = eval_epoch(mdl, ldr)

                batch_explain(
                    texts=X_test_b.tolist(),
                    labels=preds.tolist(),
                    max_samples=3,
                )
            except Exception as e:
                print(f"  [LLM] Skipped — {e}")
        del bert_df, X_train_b, X_test_b, y_train_b, y_test_b
    else:
        print("\n[Stage 4/5] BERT — SKIPPED")

    # -------------------------------------------------------
    # STAGE 5: Model Comparison
    # -------------------------------------------------------
    print("\n[Stage 5/5] Final Model Comparison")
    comparison_table()

    print("\n" + "="*60)
    print("  PIPELINE COMPLETE. Results saved to results/ folder.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
