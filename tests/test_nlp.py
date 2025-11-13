import time
import pytest
from unittest.mock import patch
from transformers.pipelines import Pipeline
from app.utils.nlp import (
    analyze_sentiment,
    clean_text,
    sentiment_analyzer,
)

# ----------------------------
# CLEAN TEXT TESTS
# ----------------------------

def test_clean_text_removes_urls():
    text = "Check this out http://example.com"
    cleaned = clean_text(text)
    assert "http" not in cleaned
    assert cleaned == "Check this out"

def test_clean_text_normalizes_spaces():
    text = "This   has   weird   spacing"
    cleaned = clean_text(text)
    assert cleaned == "This has weird spacing"

def test_clean_text_empty():
    cleaned = clean_text("")
    assert cleaned == ""

def test_clean_text_none():
    cleaned = clean_text(None)
    assert cleaned == ""


# ----------------------------
# SENTIMENT TESTS (REAL MODEL)
# ----------------------------

def test_positive_sentiment():
    result = analyze_sentiment("I absolutely love this!")
    assert result["label"] == "positive"
    assert result["score"] > 0.5

def test_negative_sentiment():
    result = analyze_sentiment("This is terrible.")
    assert result["label"] == "negative"
    assert result["score"] > 0.5

def test_neutral_for_empty():
    result = analyze_sentiment("")
    assert result["label"] == "neutral"
    assert result["score"] == 0.0


# ----------------------------
# MODEL LOADING TEST
# ----------------------------

def test_model_is_loaded():
    assert isinstance(sentiment_analyzer, Pipeline)


# ----------------------------
# PERFORMANCE TEST
# ----------------------------

def test_sentiment_speed():
    start = time.time()
    _ = analyze_sentiment("Weather is nice.")
    elapsed = time.time() - start
    assert elapsed < 1.2  # reasonable on CPU-only Docker


# ----------------------------
# MOCKED FAST TEST (CI SAFE)
# ----------------------------

@patch("app.utils.nlp.sentiment_analyzer")
def test_mocked_sentiment(mock_model):
    mock_model.return_value = [{"label": "POSITIVE", "score": 0.99}]
    result = analyze_sentiment("Mock test")
    assert result["label"] == "positive"
    assert result["score"] == 0.99