
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from website.models import SMSAnalysis


class SMSAnalysisComponentTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="sms_tester",
            password="testpassword123"
        )

        self.client.force_login(self.user)

        self.analysis_url = reverse("analyze_sms")

        self.valid_data = {
            "message": "Your bank account needs verification.",
            "sender_phone": "2025550125",
            "sender_identity": "unknown",
            "expected_message": "no",
        }

        self.mock_prediction = {
            "prediction": 1,
            "label": "Spam",
            "confidence": 0.98,
        }

        self.mock_url_result = {
            "urls_found": False,
            "findings": [],
        }

    # C2-T01: Successful SMS analysis and database persistence
    @patch("phishguard.lime_explanations.summarize_lime_explanation")
    @patch("phishguard.lime_explanations.explain_prediction")
    @patch("website.views.analyze_urls")
    @patch("sms_classifier.analyze_sms")
    def test_valid_sms_analysis_is_saved(
        self,
        mock_analyze_sms,
        mock_analyze_urls,
        mock_explain,
        mock_summary,
    ):
        mock_analyze_sms.return_value = self.mock_prediction
        mock_analyze_urls.return_value = self.mock_url_result
        mock_explain.return_value = [("bank", 0.75)]
        mock_summary.return_value = (
            "The word bank supports the Spam prediction."
        )

        response = self.client.post(
            self.analysis_url,
            self.valid_data
        )

        self.assertRedirects(response, self.analysis_url)

        self.assertEqual(SMSAnalysis.objects.count(), 1)

        analysis = SMSAnalysis.objects.get(user=self.user)

        self.assertEqual(analysis.prediction, "spam")
        self.assertEqual(
            analysis.message,
            self.valid_data["message"]
        )
        self.assertEqual(float(analysis.confidence), 98.0)

    # C2-T02: Empty SMS validation
    @patch("sms_classifier.analyze_sms")
    def test_empty_sms_is_rejected(self, mock_analyze_sms):
        invalid_data = self.valid_data.copy()
        invalid_data["message"] = ""

        response = self.client.post(
            self.analysis_url,
            invalid_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SMSAnalysis.objects.count(), 0)

        mock_analyze_sms.assert_not_called()

        self.assertEqual(
            response.context["error"],
            "Please enter an SMS message."
        )

    # C2-T03: Authentication protection
    def test_unauthenticated_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(self.analysis_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

        self.assertEqual(SMSAnalysis.objects.count(), 0)

    # C2-T04: LIME failure must not prevent the main prediction
    @patch("phishguard.lime_explanations.explain_prediction")
    @patch("website.views.analyze_urls")
    @patch("sms_classifier.analyze_sms")
    def test_lime_failure_does_not_prevent_prediction(
        self,
        mock_analyze_sms,
        mock_analyze_urls,
        mock_explain,
    ):
        mock_analyze_sms.return_value = self.mock_prediction
        mock_analyze_urls.return_value = self.mock_url_result

        mock_explain.side_effect = Exception(
            "LIME explanation unavailable"
        )

        response = self.client.post(
            self.analysis_url,
            self.valid_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(SMSAnalysis.objects.count(), 1)

        result = response.context["result"]

        self.assertEqual(result["prediction"], 1)
        self.assertEqual(result["lime_features"], [])

        self.assertIn(
            "could not be generated",
            result["lime_summary"]
        )
