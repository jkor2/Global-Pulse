from transformers import pipeline
import re

# Load model once when the container starts (fast for repeated inference)
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

def clean_text(text: str) -> str:
    """
    Basic text cleaning:
    - Remove URLs
    - Remove extra whitespace
    - Normalize spacing
    """
    if not text:
        return ""

    text = re.sub(r"http\S+|www\.\S+", "", text)  # remove URLs
    text = re.sub(r"\s+", " ", text).strip()      # normalize whitespace
    return text


def analyze_sentiment(text: str) -> dict:
    """
    Run sentiment analysis using DistilBERT.

    Returns:
    {
        "label": "positive" or "negative",
        "score": 0.9812,
        "cleaned_text": "..."
    }
    """
    cleaned = clean_text(text)

    if cleaned == "":
        return {
            "label": "neutral",
            "score": 0.0,
            "cleaned_text": "",
        }

    try:
        result = sentiment_analyzer(cleaned)[0]
        return {
            "label": result["label"].lower(),
            "score": round(float(result["score"]), 4),
            "cleaned_text": cleaned,
        }
    except Exception as e:
        return {
            "label": "error",
            "score": 0.0,
            "cleaned_text": cleaned,
            "error": str(e),
        }


