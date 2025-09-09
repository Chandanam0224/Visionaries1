# models.py
from transformers import pipeline
import os

# Sentiment pipeline
sentiment_pipe = pipeline("sentiment-analysis", device=-1)  # CPU

# Zero-shot classification for intent detection
zero_shot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=-1)

def predict_priority(text):
    txt = text.lower()
    if any(w in txt for w in ["refund", "fraud", "unauthorised", "security", "breach"]):
        return "P1"
    if any(w in txt for w in ["urgent", "immediately", "asap", "can't access", "cannot access", "unable"]):
        return "P2"
    return "P3"

def predict_intent(text, candidate_labels=None):
    if candidate_labels is None:
        candidate_labels = ["billing", "technical issue", "account access", "shipping", "general enquiry"]
    out = zero_shot(text, candidate_labels)
    return out["labels"][0], float(out["scores"][0])
