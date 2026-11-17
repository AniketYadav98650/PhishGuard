import pickle
import string
from pathlib import Path

import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer


BASE_DIR = Path(__file__).resolve().parent

# Automatically download required NLTK resources if missing
def download_nltk_resources():
    resources = {
        "tokenizers/punkt": "punkt",
        "tokenizers/punkt_tab": "punkt_tab",
        "corpora/stopwords": "stopwords",
    }

    for resource_path, package_name in resources.items():
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(package_name, quiet=True)
            nltk.data.find(resource_path)


download_nltk_resources()

with open(BASE_DIR / "vectorizer.pkl", "rb") as file:
    tfidf = pickle.load(file)

with open(BASE_DIR / "model.pkl", "rb") as file:
    model = pickle.load(file)

stemmer = PorterStemmer()
STOP_WORDS = set(stopwords.words("english"))


def transform_text(text):
    tokens = nltk.word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalnum()]
    tokens = [
        word for word in tokens
        if word not in STOP_WORDS
        and word not in string.punctuation
    ]
    return " ".join(stemmer.stem(word) for word in tokens)


def analyze_sms(message):
    processed = transform_text(message)

    if not processed.strip():
        raise ValueError(
            "Please enter a message containing usable words."
        )

    vector = tfidf.transform([processed]).toarray()

    prediction = int(model.predict(vector)[0])
    probabilities = model.predict_proba(vector)[0]
    confidence = float(probabilities[prediction])

    return {
        "prediction": prediction,
        "label": "Spam" if prediction == 1 else "Not Spam",
        "confidence": confidence,
    }