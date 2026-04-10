"""
Baseline ML models using TF-IDF + Logistic Regression, Naive Bayes, SVM.
"""

import os
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from evaluate import compute_metrics, print_report, plot_confusion_matrix, save_metrics

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def build_pipeline(classifier, max_features: int = 50000):
    """Create a TF-IDF + classifier sklearn Pipeline."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )),
        ("clf", classifier),
    ])


def get_ml_models():
    """Return dict of model name → sklearn pipeline."""
    return {
        "Logistic Regression": build_pipeline(
            LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs", n_jobs=-1)
        ),
        "Naive Bayes": build_pipeline(
            MultinomialNB(alpha=0.1)
        ),
        "Linear SVM": build_pipeline(
            LinearSVC(max_iter=2000, C=1.0)
        ),
    }


def train_and_evaluate(X_train, X_test, y_train, y_test):
    """Train all ML models, evaluate, save results and model files."""
    models = get_ml_models()
    all_metrics = []

    for name, pipeline in models.items():
        print(f"\n[ML] Training {name}...")
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        metrics = compute_metrics(y_test, y_pred, model_name=name)
        all_metrics.append(metrics)
        print_report(y_test, y_pred, model_name=name)
        plot_confusion_matrix(y_test, y_pred, model_name=name)
        save_metrics(metrics)

        # Save model
        model_path = os.path.join(MODELS_DIR, f"{name.replace(' ', '_')}.pkl")
        joblib.dump(pipeline, model_path)
        print(f"  Model saved → {model_path}")

    return all_metrics


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from preprocess import load_data, preprocess, split_data

    print("Loading data...")
    df = load_data(sample_size=100000)
    df = preprocess(df)
    X_train, X_test, y_train, y_test = split_data(df)
    train_and_evaluate(X_train, X_test, y_train, y_test)
