"""
Data loading and text preprocessing for suicidal ideation detection.
"""

import re
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
def download_nltk_data():
    for pkg in ["stopwords", "wordnet", "omw-1.4"]:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass

download_nltk_data()

DATASET_PATH = r"C:\Users\admin\Downloads\Suicide_Detection.csv"

LABEL_MAP = {"suicide": 1, "non-suicide": 0}


def load_data(path: str = DATASET_PATH, sample_size: int = None, random_state: int = 42) -> pd.DataFrame:
    """Load and optionally sample the dataset."""
    df = pd.read_csv(path, usecols=["text", "class"])
    df.rename(columns={"class": "label"}, inplace=True)
    df.dropna(subset=["text", "label"], inplace=True)
    df["label"] = df["label"].map(LABEL_MAP)
    df.dropna(subset=["label"], inplace=True)
    df["label"] = df["label"].astype(int)
    df.reset_index(drop=True, inplace=True)

    if sample_size:
        df = df.sample(n=min(sample_size, len(df)), random_state=random_state).reset_index(drop=True)

    return df


def clean_text(text: str) -> str:
    """Clean a single text string."""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)          # remove URLs
    text = re.sub(r"@\w+|#\w+", "", text)               # remove mentions/hashtags
    text = re.sub(r"[^a-z\s]", "", text)                # keep only letters
    text = re.sub(r"\s+", " ", text).strip()            # normalise whitespace
    return text


def remove_stopwords_and_lemmatize(text: str) -> str:
    """Remove stopwords and lemmatize tokens."""
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words and len(t) > 2]
    return " ".join(tokens)


def preprocess(df: pd.DataFrame, full_clean: bool = True) -> pd.DataFrame:
    """Apply full preprocessing pipeline to dataframe."""
    print(f"  Cleaning {len(df):,} samples...")
    df = df.copy()
    df["clean_text"] = df["text"].apply(clean_text)
    if full_clean:
        df["clean_text"] = df["clean_text"].apply(remove_stopwords_and_lemmatize)
    df = df[df["clean_text"].str.strip().astype(bool)].reset_index(drop=True)
    return df


def split_data(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """Split into train/test sets."""
    X = df["clean_text"]
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"  Train: {len(X_train):,} | Test: {len(X_test):,}")
    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    df = load_data(sample_size=50000)
    print(f"Loaded: {df.shape}")
    print(df["label"].value_counts())
    df = preprocess(df)
    X_train, X_test, y_train, y_test = split_data(df)
    print("Preprocessing complete.")
