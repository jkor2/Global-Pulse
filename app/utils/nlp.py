# app/utils/nlp.py

import re
from transformers import pipeline, AutoTokenizer


MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    tokenizer=tokenizer
)

def clean_text(text: str) -> str:
    """Remove URLs + normalize whitespace."""
    if not text:
        return ""
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def truncate_text(text: str, max_tokens: int = 512) -> str:
    """Trim text to model max length safely."""
    try:
        tokens = tokenizer.encode(
            text,
            truncation=True,
            max_length=max_tokens
        )
        return tokenizer.decode(tokens, skip_special_tokens=True)
    except Exception:
        return text[:2000]

def analyze_sentiment(text: str) -> dict:
    """
    Run DistilBERT and convert the binary output into:
    - positive
    - negative
    - neutral (custom threshold)
    """

    cleaned = clean_text(text)

    if cleaned == "":
        return {
            "label": "neutral",
            "score": 0.0,
            "cleaned_text": ""
        }

    safe_text = truncate_text(cleaned)

    try:
        result = sentiment_analyzer(safe_text)[0]
        raw_label = result["label"].lower()  # "positive" or "negative"
        score = float(result["score"])

        if 0.45 < score < 0.55:
            mapped_label = "neutral"
        else:
            mapped_label = raw_label

        return {
            "label": mapped_label,
            "score": round(score, 4),
            "cleaned_text": safe_text
        }

    except Exception as e:
        return {
            "label": "error",
            "score": 0.0,
            "cleaned_text": safe_text,
            "error": str(e)
        }