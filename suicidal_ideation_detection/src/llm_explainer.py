"""
LLM-based explainer: uses Claude API to explain why a post is flagged as high-risk.
Requires ANTHROPIC_API_KEY environment variable.
"""

import os
import anthropic

client = None


def _get_client():
    global client
    if client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable not set.\n"
                "Set it with:  set ANTHROPIC_API_KEY=your_key_here  (Windows)\n"
                "              export ANTHROPIC_API_KEY=your_key_here (Linux/Mac)"
            )
        client = anthropic.Anthropic(api_key=api_key)
    return client


SYSTEM_PROMPT = """You are a clinical mental health AI assistant specialising in suicide risk assessment.
Your role is to explain, in clear and compassionate language, why a given social media post has been
classified as potentially indicating suicidal ideation.

Guidelines:
- Identify specific phrases or linguistic patterns that signal risk.
- Explain the psychological or contextual significance of those patterns.
- Suggest an appropriate intervention or support resource.
- Be empathetic and non-judgmental.
- Keep your response concise (3-5 bullet points)."""


def explain_prediction(text: str, predicted_label: int, confidence: float = None) -> str:
    """
    Use Claude to explain the model's prediction for a given text.

    Args:
        text: Original social media post text.
        predicted_label: 1 = suicide risk, 0 = non-suicide.
        confidence: Optional model confidence score (0-1).

    Returns:
        String explanation from Claude.
    """
    label_str = "HIGH RISK (suicidal ideation detected)" if predicted_label == 1 else "LOW RISK (no suicidal ideation)"
    conf_str  = f" (confidence: {confidence:.1%})" if confidence is not None else ""

    user_message = f"""A machine learning model has classified the following social media post as: **{label_str}{conf_str}**

Post:
\"\"\"
{text}
\"\"\"

Please explain:
1. Which specific words or phrases contributed to this classification.
2. What psychological signals or risk factors are present (or absent).
3. What action or support would be appropriate for this individual."""

    try:
        c = _get_client()
        response = c.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
    except Exception as e:
        return f"[LLM explanation unavailable: {e}]"


def batch_explain(texts: list, labels: list, confidences: list = None, max_samples: int = 5) -> list:
    """Explain predictions for a batch of samples (default: first 5 positive predictions)."""
    results = []
    count = 0
    for i, (text, label) in enumerate(zip(texts, labels)):
        if label == 1 and count < max_samples:
            conf = confidences[i] if confidences else None
            explanation = explain_prediction(text, label, conf)
            results.append({
                "text": text[:300] + "..." if len(text) > 300 else text,
                "label": label,
                "explanation": explanation,
            })
            count += 1
            print(f"\n--- Sample {count} ---")
            print(f"Text: {text[:150]}...")
            print(f"Explanation:\n{explanation}")
    return results


if __name__ == "__main__":
    # Quick test
    sample_text = (
        "I can't take it anymore. Every day feels like a battle I'm losing. "
        "I've been thinking that everyone would be better off without me."
    )
    print("Testing LLM explainer...")
    explanation = explain_prediction(sample_text, predicted_label=1, confidence=0.92)
    print(explanation)
