"""
app.py — Streamlit demo for Suicidal Ideation Detection.
Loads the best saved model (BERT if available, else best ML model)
and provides a live prediction interface with LLM explanation.

Run:
    streamlit run app.py
"""

import os
import sys
import joblib
import streamlit as st

SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
sys.path.insert(0, SRC_DIR)

from preprocess import clean_text, remove_stopwords_and_lemmatize

MODELS_DIR   = os.path.join(os.path.dirname(__file__), "models")
BERT_DIR     = os.path.join(MODELS_DIR, "bert_finetuned")
ML_MODEL_PATH = os.path.join(MODELS_DIR, "Logistic_Regression.pkl")

st.set_page_config(
    page_title="Suicidal Ideation Detector",
    page_icon="🧠",
    layout="centered",
)

# ---- Sidebar ---------------------------------------------------------------
st.sidebar.title("Settings")
use_llm = st.sidebar.checkbox("Enable LLM Explanation (requires API key)", value=False)
api_key = ""
if use_llm:
    api_key = st.sidebar.text_input("Anthropic API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Models available:**\n"
    "- BERT (fine-tuned) — highest accuracy\n"
    "- Logistic Regression (TF-IDF) — fastest\n"
)

# ---- Model loading ---------------------------------------------------------
@st.cache_resource
def load_bert():
    import torch
    from transformers import BertTokenizer, BertForSequenceClassification
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = BertTokenizer.from_pretrained(BERT_DIR)
    model     = BertForSequenceClassification.from_pretrained(BERT_DIR).to(device)
    model.eval()
    return tokenizer, model, device


@st.cache_resource
def load_ml_model():
    return joblib.load(ML_MODEL_PATH)


def predict_bert(text: str):
    import torch
    tokenizer, model, device = load_bert()
    enc = tokenizer(text, max_length=128, padding="max_length",
                    truncation=True, return_tensors="pt")
    input_ids      = enc["input_ids"].to(device)
    attention_mask = enc["attention_mask"].to(device)
    with torch.no_grad():
        logits = model(input_ids=input_ids, attention_mask=attention_mask).logits
        probs  = torch.softmax(logits, dim=1).cpu().numpy()[0]
    return int(probs.argmax()), float(probs.max())


def predict_ml(text: str):
    model = load_ml_model()
    clean = remove_stopwords_and_lemmatize(clean_text(text))
    pred  = int(model.predict([clean])[0])
    if hasattr(model.named_steps["clf"], "decision_function"):
        import numpy as np
        score = model.decision_function([clean])[0]
        conf  = float(1 / (1 + np.exp(-abs(score))))
    else:
        proba = model.predict_proba([clean])[0]
        conf  = float(proba.max())
    return pred, conf


# ---- UI --------------------------------------------------------------------
st.title("🧠 Suicidal Ideation Detection")
st.markdown(
    "> **Disclaimer:** This tool is for research and educational purposes only. "
    "It is not a medical device and should not replace professional clinical judgment."
)

st.markdown("---")

# Choose model
bert_available = os.path.isdir(BERT_DIR)
ml_available   = os.path.isfile(ML_MODEL_PATH)

if bert_available:
    model_choice = st.selectbox("Select model", ["BERT (fine-tuned)", "Logistic Regression (TF-IDF)"])
elif ml_available:
    model_choice = "Logistic Regression (TF-IDF)"
    st.info("BERT model not found. Using Logistic Regression. Run main.py to train BERT.")
else:
    st.error("No trained model found. Please run `python main.py` first.")
    st.stop()

# Text input
user_text = st.text_area(
    "Enter a social media post to analyse:",
    height=150,
    placeholder="Type or paste text here...",
)

if st.button("Analyse", type="primary") and user_text.strip():
    with st.spinner("Analysing..."):
        # Predict
        if "BERT" in model_choice and bert_available:
            label, confidence = predict_bert(user_text)
        else:
            label, confidence = predict_ml(user_text)

    # Result display
    st.markdown("### Result")
    if label == 1:
        st.error(f"⚠️ **HIGH RISK — Suicidal Ideation Detected**\n\nConfidence: {confidence:.1%}")
        st.markdown(
            "**If you or someone you know is in crisis, please reach out:**\n"
            "- **iCall (India):** 9152987821\n"
            "- **Vandrevala Foundation:** 1860-2662-345\n"
            "- **International Association for Suicide Prevention:** https://www.iasp.info/resources/Crisis_Centres/"
        )
    else:
        st.success(f"✅ **LOW RISK — No Suicidal Ideation Detected**\n\nConfidence: {confidence:.1%}")

    # LLM Explanation
    if use_llm and api_key:
        st.markdown("### LLM Explanation")
        with st.spinner("Generating explanation..."):
            os.environ["ANTHROPIC_API_KEY"] = api_key
            from llm_explainer import explain_prediction
            explanation = explain_prediction(user_text, label, confidence)
        st.markdown(explanation)

    st.markdown("---")
    st.caption(f"Model used: **{model_choice}** | Confidence: {confidence:.1%}")

# ---- Batch analysis --------------------------------------------------------
st.markdown("---")
st.subheader("Batch Analysis")
uploaded = st.file_uploader("Upload a CSV with a 'text' column", type=["csv"])
if uploaded:
    import pandas as pd
    df = pd.read_csv(uploaded)
    if "text" not in df.columns:
        st.error("CSV must have a 'text' column.")
    else:
        with st.spinner(f"Analysing {len(df):,} rows..."):
            results = []
            for text in df["text"].fillna("").astype(str):
                if "BERT" in model_choice and bert_available:
                    lbl, conf = predict_bert(text)
                else:
                    lbl, conf = predict_ml(text)
                results.append({
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "prediction": "suicide" if lbl == 1 else "non-suicide",
                    "confidence": f"{conf:.1%}",
                })
            result_df = pd.DataFrame(results)
        st.dataframe(result_df, use_container_width=True)

        csv = result_df.to_csv(index=False)
        st.download_button("Download Results", csv, "predictions.csv", "text/csv")
