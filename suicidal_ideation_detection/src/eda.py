"""
Exploratory Data Analysis (EDA) for the Suicide Detection dataset.
Generates visualisations saved to the results/ folder.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="Set2")


def plot_class_distribution(df: pd.DataFrame):
    """Bar chart of class balance."""
    counts = df["label"].map({1: "suicide", 0: "non-suicide"}).value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    counts.plot(kind="bar", ax=ax, color=["#e74c3c", "#2ecc71"], edgecolor="black")
    ax.set_title("Class Distribution")
    ax.set_xlabel("Class")
    ax.set_ylabel("Count")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2, p.get_height()),
                    ha="center", va="bottom", fontsize=11)
    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "class_distribution.png")
    fig.savefig(path, dpi=120)
    print(f"  Saved → {path}")
    plt.show()
    plt.close()


def plot_text_length(df: pd.DataFrame):
    """Histogram of text length distribution by class."""
    df = df.copy()
    df["text_len"] = df["text"].apply(lambda x: len(str(x).split()))
    df["class_label"] = df["label"].map({1: "suicide", 0: "non-suicide"})

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, cls in zip(axes, ["suicide", "non-suicide"]):
        subset = df[df["class_label"] == cls]["text_len"]
        ax.hist(subset.clip(upper=300), bins=50, color="#e74c3c" if cls == "suicide" else "#2ecc71",
                edgecolor="black", alpha=0.8)
        ax.set_title(f"Word Count — {cls}")
        ax.set_xlabel("Words")
        ax.set_ylabel("Frequency")
        ax.axvline(subset.median(), color="navy", linestyle="--", label=f"Median: {subset.median():.0f}")
        ax.legend()
    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "text_length_distribution.png")
    fig.savefig(path, dpi=120)
    print(f"  Saved → {path}")
    plt.show()
    plt.close()


def plot_top_words(df: pd.DataFrame, n: int = 20):
    """Bar charts of top N words per class."""
    stop_words = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
        "he", "she", "it", "they", "them", "what", "which", "who", "this", "that",
        "a", "an", "the", "and", "but", "if", "or", "as", "at", "by", "for",
        "with", "about", "to", "from", "in", "is", "was", "are", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "not", "no",
        "so", "just", "like", "get", "got", "it", "its", "im", "dont", "cant",
        "on", "of", "up", "out", "all", "when", "there", "their", "than", "then",
    }

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for ax, (label_val, label_str) in zip(axes, [(1, "suicide"), (0, "non-suicide")]):
        texts = df[df["label"] == label_val]["text"].fillna("").astype(str)
        words = []
        for t in texts:
            words.extend([w.lower() for w in re.findall(r"\b[a-z]{3,}\b", t) if w.lower() not in stop_words])
        top = Counter(words).most_common(n)
        words_list, counts = zip(*top)
        color = "#e74c3c" if label_str == "suicide" else "#2ecc71"
        ax.barh(list(words_list)[::-1], list(counts)[::-1], color=color, edgecolor="black")
        ax.set_title(f"Top {n} Words — {label_str}")
        ax.set_xlabel("Frequency")

    plt.tight_layout()
    path = os.path.join(RESULTS_DIR, "top_words.png")
    fig.savefig(path, dpi=120)
    print(f"  Saved → {path}")
    plt.show()
    plt.close()


def run_eda(df: pd.DataFrame):
    """Run all EDA plots."""
    print("\n[EDA] Running exploratory data analysis...")
    print(f"\n  Dataset shape: {df.shape}")
    print(f"  Class balance:\n{df['label'].value_counts().to_string()}")
    print(f"\n  Sample texts:")
    for i, row in df.sample(3, random_state=42).iterrows():
        lbl = "suicide" if row["label"] == 1 else "non-suicide"
        print(f"    [{lbl}] {str(row['text'])[:100]}...")

    plot_class_distribution(df)
    plot_text_length(df)
    plot_top_words(df)
    print("\n[EDA] Complete.\n")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from preprocess import load_data

    df = load_data(sample_size=50000)
    run_eda(df)
