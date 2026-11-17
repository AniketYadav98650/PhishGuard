
from lime.lime_text import LimeTextExplainer

from sms_classifier import model, tfidf, transform_text


# Initialize LIME using the existing model's class labels.
explainer = LimeTextExplainer(
    class_names=["Not Spam", "Spam"],
    random_state=42,
)


def predict_probabilities(messages):
    """
    Return class probabilities using the existing
    SMS preprocessing, TF-IDF vectorizer, and ML model.
    """

    processed = [transform_text(message) for message in messages]

    # Prevent empty processed messages from causing issues.
    processed = [
        text if text.strip() else "emptymessage"
        for text in processed
    ]

    vectors = tfidf.transform(processed).toarray()

    return model.predict_proba(vectors)


def explain_prediction(message, prediction):
    """
    Generate a LIME explanation for the existing ML prediction.
    """

    explanation = explainer.explain_instance(
        message,
        predict_probabilities,
        labels=(int(prediction),),
        num_features=8,
        num_samples=1000,
    )

    return explanation.as_list(label=int(prediction))


def summarize_lime_explanation(features, prediction):
    """
    Convert LIME feature weights into a readable explanation.
    """

    label = "spam" if int(prediction) == 1 else "not spam"

    supporting = sorted(
        [
            (word, weight)
            for word, weight in features
            if weight > 0
        ],
        key=lambda item: item[1],
        reverse=True,
    )

    opposing = sorted(
        [
            (word, weight)
            for word, weight in features
            if weight < 0
        ],
        key=lambda item: item[1],
    )

    parts = []

    if supporting:
        words = ", ".join(
            word for word, weight in supporting[:4]
        )
        parts.append(
            f"Words supporting the {label} prediction include: {words}."
        )

    if opposing:
        words = ", ".join(
            word for word, weight in opposing[:4]
        )
        parts.append(
            f"Words opposing the {label} prediction include: {words}."
        )

    if not parts:
        parts.append(
            "LIME did not identify strong influential words."
        )

    parts.append(
        "These words explain the model's behavior; "
        "they do not prove whether a message is malicious."
    )

    return " ".join(parts)
