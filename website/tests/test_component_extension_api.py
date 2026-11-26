
import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class ExtensionAPIComponentTests(TestCase):

    def setUp(self):
        self.api_url = reverse("extension_analyze")

        self.mock_prediction = {
            "prediction": 1,
            "label": "Spam",
            "confidence": 0.885,
        }

    @patch(
        "phishguard.lime_explanations.summarize_lime_explanation",
        return_value="The words prize and claim support the Spam prediction."
    )
    @patch(
        "phishguard.lime_explanations.explain_prediction",
        return_value=[("prize", 0.75), ("claim", 0.45)]
    )
    @patch("website.extension_api.analyze_sms")
    def test_valid_message_returns_complete_analysis(
        self,
        mock_analyze_sms,
        mock_explain,
        mock_summary
    ):
        mock_analyze_sms.return_value = self.mock_prediction

        response = self.client.post(
            self.api_url,
            data=json.dumps({
                "message": "Congratulations! Claim your free prize."
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()

        self.assertEqual(result["prediction"], 1)
        self.assertEqual(result["label"], "Spam")
        self.assertEqual(result["confidence_percent"], 88.5)

        self.assertIn("url_analysis", result)
        self.assertIn("lime_features", result)
        self.assertIn("lime_summary", result)

        self.assertEqual(len(result["lime_features"]), 2)

        mock_analyze_sms.assert_called_once()

    def test_empty_message_returns_validation_error(self):
        response = self.client.post(
            self.api_url,
            data=json.dumps({"message": ""}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.json()["error"],
            "Please provide a message to analyze."
        )

    def test_malformed_json_returns_error(self):
        response = self.client.post(
            self.api_url,
            data='{"message": ',
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.json()["error"],
            "Invalid JSON request."
        )
    def test_non_string_message_returns_validation_error(self):
        response = self.client.post(
            self.api_url,
            data=json.dumps({"message": 123}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.json()["error"],
            "Please provide a message to analyze."
        )