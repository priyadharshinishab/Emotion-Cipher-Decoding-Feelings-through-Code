# emotion_detector.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

class EmotionDetector:
    def __init__(self, classifier_model="bhadresh-savani/distilbert-base-uncased-emotion"):
        # ✅ Load Hugging Face model and tokenizer
        self.clf_tokenizer = AutoTokenizer.from_pretrained(classifier_model)
        self.clf_model = AutoModelForSequenceClassification.from_pretrained(classifier_model)

        # Labels depend on the model used
        self.labels = ["anger", "fear", "joy", "love", "sadness", "surprise"]

    def detect_emotion(self, text):
        inputs = self.clf_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.clf_model(**inputs)
            scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
        scores = scores[0].numpy()

        # Rank emotions
        ranked = sorted(zip(self.labels, scores), key=lambda x: x[1], reverse=True)
        top_2 = [r[0] for r in ranked[:2]]  # top 2 emotions
        return top_2
