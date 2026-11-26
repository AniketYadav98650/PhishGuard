
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class URLAnalysisComponentTests(TestCase):

    def setUp(self):
        self.api_url = reverse("extension_analyze")

        self.mock_prediction = {
            "prediction": 1,
            "label": "Spam",
            "confidence": 0.95,
        }

    @patch(
        "phishguard.lime_explanations.summarize_lime_explanation",
        return_value="Test explanation."
    )
    @patch(
        "phishguard.lime_explanations.explain_prediction",
        return_value=[]
    )
    @patch(
        "website.extension_api.analyze_sms"
    )
    def test_suspicious_url_indicators_are_returned(
        self,
        mock_analyze_sms,
        mock_explain,
        mock_summary
    ):
        mock_analyze_sms.return_value = self.mock_prediction

        response = self.client.post(
            self.api_url,
            data={
                "message": "Claim your prize at http://bit.ly/claim"
            },
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()
        url_analysis = result["url_analysis"]

        self.assertTrue(url_analysis["urls_found"])
        self.assertEqual(
            url_analysis["risk_level"],
            "Suspicious indicators found"
        )
        self.assertTrue(
            any("shortened URL" in finding
                for finding in url_analysis["findings"])
        )
        self.assertTrue(
            any("HTTP" in finding
                for finding in url_analysis["findings"])
        )

    @patch(
        "phishguard.lime_explanations.summarize_lime_explanation",
        return_value="Test explanation."
    )
    @patch(
        "phishguard.lime_explanations.explain_prediction",
        return_value=[]
    )
    @patch(
        "website.extension_api.analyze_sms"
    )
    def test_ordinary_https_url_has_no_obvious_indicators(
        self,
        mock_analyze_sms,
        mock_explain,
        mock_summary
    ):
        mock_analyze_sms.return_value = self.mock_prediction

        response = self.client.post(
            self.api_url,
            data={
                "message": "Visit https://example.com for information."
            },
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()
        url_analysis = result["url_analysis"]

        self.assertTrue(url_analysis["urls_found"])
        self.assertEqual(
            url_analysis["risk_level"],
            "No obvious URL indicators found"
        )
        self.assertEqual(url_analysis["findings"], [])

    @patch(
        "phishguard.lime_explanations.summarize_lime_explanation",
        return_value="Test explanation."
    )
    @patch(
        "phishguard.lime_explanations.explain_prediction",
        return_value=[]
    )
    @patch(
        "website.extension_api.analyze_sms"
    )
    def test_message_without_url_returns_no_url_detected(
        self,
        mock_analyze_sms,
        mock_explain,
        mock_summary
    ):
        mock_analyze_sms.return_value = self.mock_prediction

        response = self.client.post(
            self.api_url,
            data={
                "message": "Hello, are we meeting tomorrow?"
            },
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()
        url_analysis = result["url_analysis"]

        self.assertFalse(url_analysis["urls_found"])
        self.assertEqual(
            url_analysis["risk_level"],
            "No URL detected"
        )
        self.assertEqual(url_analysis["findings"], [])
