"""
Deep learning models: LSTM and BiLSTM using TensorFlow/Keras.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Embedding, LSTM, Bidirectional, Dense, Dropout,
    GlobalMaxPooling1D, SpatialDropout1D,
)
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from evaluate import compute_metrics, print_report, plot_confusion_matrix, save_metrics

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Hyperparameters
VOCAB_SIZE   = 30000
MAX_LEN      = 150
EMBED_DIM    = 128
BATCH_SIZE   = 64
EPOCHS       = 10


def build_tokenizer(texts, vocab_size: int = VOCAB_SIZE):
    """Fit a Keras Tokenizer on training texts."""
    tokenizer = Tokenizer(num_words=vocab_size, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    return tokenizer


def texts_to_sequences(tokenizer, texts, max_len: int = MAX_LEN):
    """Convert texts to padded integer sequences."""
    seqs = tokenizer.texts_to_sequences(texts)
    return pad_sequences(seqs, maxlen=max_len, padding="post", truncating="post")


def build_lstm(vocab_size: int = VOCAB_SIZE, embed_dim: int = EMBED_DIM, max_len: int = MAX_LEN):
    """Unidirectional LSTM model."""
    model = Sequential([
        Embedding(vocab_size, embed_dim, input_length=max_len),
        SpatialDropout1D(0.2),
        LSTM(128, dropout=0.2, recurrent_dropout=0.2, return_sequences=True),
        LSTM(64, dropout=0.2, recurrent_dropout=0.2),
        Dense(64, activation="relu"),
        Dropout(0.3),
        Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def build_bilstm(vocab_size: int = VOCAB_SIZE, embed_dim: int = EMBED_DIM, max_len: int = MAX_LEN):
    """Bidirectional LSTM model."""
    model = Sequential([
        Embedding(vocab_size, embed_dim, input_length=max_len),
        SpatialDropout1D(0.2),
        Bidirectional(LSTM(128, dropout=0.2, recurrent_dropout=0.2, return_sequences=True)),
        Bidirectional(LSTM(64, dropout=0.2, recurrent_dropout=0.2)),
        Dense(64, activation="relu"),
        Dropout(0.3),
        Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def train_dl_model(model, model_name: str, X_train_seq, X_test_seq, y_train, y_test):
    """Train a Keras model and evaluate it."""
    callbacks = [
        EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, verbose=1),
    ]

    print(f"\n[DL] Training {model_name}...")
    model.summary()

    history = model.fit(
        X_train_seq, np.array(y_train),
        validation_split=0.1,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )

    y_prob = model.predict(X_test_seq, verbose=0).flatten()
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = compute_metrics(y_test, y_pred, model_name=model_name)
    print_report(y_test, y_pred, model_name=model_name)
    plot_confusion_matrix(y_test, y_pred, model_name=model_name)
    save_metrics(metrics)

    # Save model
    model_path = os.path.join(MODELS_DIR, f"{model_name.replace(' ', '_')}.keras")
    model.save(model_path)
    print(f"  Model saved → {model_path}")

    return history, metrics


def train_and_evaluate(X_train, X_test, y_train, y_test):
    """Full DL training pipeline: tokenize → LSTM → BiLSTM."""
    print("\n[DL] Fitting tokenizer...")
    tokenizer = build_tokenizer(X_train)

    print("[DL] Converting texts to sequences...")
    X_train_seq = texts_to_sequences(tokenizer, X_train)
    X_test_seq  = texts_to_sequences(tokenizer, X_test)

    all_metrics = []

    # LSTM
    lstm_model = build_lstm()
    _, m1 = train_dl_model(lstm_model, "LSTM", X_train_seq, X_test_seq, y_train, y_test)
    all_metrics.append(m1)

    # BiLSTM
    bilstm_model = build_bilstm()
    _, m2 = train_dl_model(bilstm_model, "BiLSTM", X_train_seq, X_test_seq, y_train, y_test)
    all_metrics.append(m2)

    return tokenizer, all_metrics


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from preprocess import load_data, preprocess, split_data

    print("Loading data...")
    df = load_data(sample_size=50000)
    df = preprocess(df, full_clean=False)   # Keep stopwords for DL context
    X_train, X_test, y_train, y_test = split_data(df)
    train_and_evaluate(X_train, X_test, y_train, y_test)
