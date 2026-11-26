
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from sms_classifier import analyze_sms
from phishguard.url_analysis import analyze_urls


@csrf_exempt
@require_POST
def extension_analyze(request):
    try:
        data = json.loads(request.body)

        message = data.get("message", "")

        if not isinstance(message, str) or not message.strip():
            return JsonResponse(
                {"error": "Please provide a message to analyze."},
                status=400
            )

        message = message.strip()

        if len(message) > 10000:
            return JsonResponse(
                {"error": "Message is too long. Maximum length is 10,000 characters."},
                status=400
            )

        # Use the existing PhishGuard ML classifier.
        result = analyze_sms(message)

        # Inspect URLs separately from the ML prediction.
        try:
            url_analysis = analyze_urls(message)
        except Exception:
            url_analysis = {
                "urls_found": False,
                "findings": [
                    "URL analysis could not be completed."
                ]
            }

        # Generate the existing LIME explanation.
        try:
            from phishguard.lime_explanations import (
                explain_prediction,
                summarize_lime_explanation,
            )

            features = explain_prediction(
                message,
                result["prediction"]
            )

            lime_features = [
                {
                    "word": word,
                    "weight": round(float(weight), 4),
                    "direction": (
                        "supports" if weight > 0
                        else "opposes" if weight < 0
                        else "neutral"
                    )
                }
                for word, weight in features
            ]

            lime_summary = summarize_lime_explanation(
                features,
                result["prediction"]
            )

        except Exception:
            lime_features = []
            lime_summary = (
                "The prediction was generated, but its explanation "
                "could not be generated at this time."
            )

        return JsonResponse({
            "prediction": result["prediction"],
            "label": result["label"],
            "confidence_percent": round(
                result["confidence"] * 100, 1
            ),
            "url_analysis": url_analysis,
            "lime_features": lime_features,
            "lime_summary": lime_summary,
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON request."},
            status=400
        )

    except ValueError as exc:
        return JsonResponse(
            {"error": str(exc)},
            status=400
        )
