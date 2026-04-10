"""
Shared evaluation utilities — metrics, confusion matrix, and comparison table.
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def compute_metrics(y_true, y_pred, model_name: str = "") -> dict:
    """Return a dict of standard classification metrics."""
    metrics = {
        "model": model_name,
        "accuracy":  round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1":        round(f1_score(y_true, y_pred, zero_division=0), 4),
    }
    return metrics


def print_report(y_true, y_pred, model_name: str = ""):
    """Print full classification report."""
    print(f"\n{'='*50}")
    print(f"  {model_name} — Evaluation Report")
    print(f"{'='*50}")
    print(classification_report(y_true, y_pred, target_names=["non-suicide", "suicide"]))


def plot_confusion_matrix(y_true, y_pred, model_name: str = "", save: bool = True):
    """Plot and optionally save confusion matrix."""
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["non-suicide", "suicide"],
                yticklabels=["non-suicide", "suicide"], ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix — {model_name}")
    plt.tight_layout()
    if save:
        path = os.path.join(RESULTS_DIR, f"cm_{model_name.replace(' ', '_')}.png")
        fig.savefig(path, dpi=120)
        print(f"  Saved confusion matrix → {path}")
    plt.show()
    plt.close()


def save_metrics(metrics: dict):
    """Append metrics dict to the results JSON file."""
    results_file = os.path.join(RESULTS_DIR, "all_metrics.json")
    existing = []
    if os.path.exists(results_file):
        with open(results_file) as f:
            existing = json.load(f)
    # Replace if same model name exists
    existing = [m for m in existing if m.get("model") != metrics["model"]]
    existing.append(metrics)
    with open(results_file, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"  Metrics saved → {results_file}")


def comparison_table():
    """Load all saved metrics and print a comparison table."""
    results_file = os.path.join(RESULTS_DIR, "all_metrics.json")
    if not os.path.exists(results_file):
        print("No results found yet.")
        return
    with open(results_file) as f:
        data = json.load(f)
    df = pd.DataFrame(data).set_index("model")
    df = df.sort_values("f1", ascending=False)
    print("\n" + "="*60)
    print("       MODEL COMPARISON TABLE")
    print("="*60)
    print(df.to_string())
    print("="*60)

    # Bar chart
    fig, ax = plt.subplots(figsize=(10, 5))
    df[["accuracy", "precision", "recall", "f1"]].plot(kind="bar", ax=ax, colormap="Set2")
    ax.set_title("Model Performance Comparison")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1)
    ax.legend(loc="lower right")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "model_comparison.png")
    fig.savefig(path, dpi=120)
    print(f"  Comparison chart saved → {path}")
    plt.show()
    plt.close()
    return df
