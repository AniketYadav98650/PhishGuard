
import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from website.models import SMSAnalysis, PhoneNumber, PhoneReport


class SMSAnalysisSystemTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="system_tester",
            password="TestPassword123!"
        )

        self.client.force_login(self.user)

        self.analysis_url = reverse("analyze_sms")
        self.extension_url = reverse("extension_analyze")

        self.message = (
            "Your bank account is suspended. "
            "Verify your details immediately."
        )

        self.form_data = {
            "message": self.message,
            "sender_phone": "2025550125",
            "sender_identity": "unknown",
            "expected_message": "no",
        }

    @patch("phishguard.lime_explanations.summarize_lime_explanation")
    @patch("phishguard.lime_explanations.explain_prediction")
    @patch("website.views.analyze_urls")
    @patch("sms_classifier.analyze_sms")
    def test_complete_spam_analysis_workflow(
        self,
        mock_analyze_sms,
        mock_analyze_urls,
        mock_explain,
        mock_summary
    ):
        mock_analyze_sms.return_value = {
            "prediction": 1,
            "label": "Spam",
            "confidence": 0.98,
        }

        mock_analyze_urls.return_value = {
            "urls_found": False,
            "urls": [],
            "findings": [],
            "risk_level": "No URL detected",
        }

        mock_explain.return_value = [
            ("suspended", 0.75),
            ("verify", 0.45),
        ]

        mock_summary.return_value = (
            "The words suspended and verify support the Spam prediction."
        )

        response = self.client.post(
            self.analysis_url,
            self.form_data,
            follow=True
        )

        # Verify the complete request and redirect workflow.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.redirect_chain)

        # Verify the analysis result is displayed.
        result = response.context["result"]

        self.assertIsNotNone(result)
        self.assertEqual(result["prediction"], 1)
        self.assertEqual(result["label"], "Spam")
        self.assertEqual(result["confidence_percent"], 98.0)

        # Verify contextual analysis.
        self.assertIn("context_analysis", result)

        self.assertEqual(
            result["context_analysis"]["sender_identity_label"],
            "Unknown sender"
        )

        self.assertEqual(
            result["context_analysis"]["expected_message_label"],
            "No"
        )

        # Verify URL analysis.
        self.assertFalse(result["url_analysis"]["urls_found"])

        # Verify LIME explanation.
        self.assertEqual(len(result["lime_features"]), 2)

        self.assertIn(
            "supports",
            result["lime_features"][0]["direction"]
        )

        self.assertEqual(
            result["lime_summary"],
            "The words suspended and verify support the Spam prediction."
        )

        # Verify the analysis was saved to the database.
        self.assertEqual(SMSAnalysis.objects.count(), 1)

        analysis = SMSAnalysis.objects.get(user=self.user)

        self.assertEqual(analysis.message, self.message)
        self.assertEqual(analysis.prediction, "spam")
        self.assertEqual(float(analysis.confidence), 98.0)

        # Verify the ML classifier, URL analyzer, and LIME were called.
        mock_analyze_sms.assert_called_once_with(self.message)
        mock_analyze_urls.assert_called_once_with(self.message)

        mock_explain.assert_called_once_with(
            self.message,
            1
        )

        mock_summary.assert_called_once()

    def test_complete_community_reporting_and_lookup_workflow(self):

        spam_result = {
            "prediction": 1,
            "label": "Spam",
            "confidence": 0.98,
        }

        # Stage 1: Analyze the suspicious SMS.
        with patch(
            "sms_classifier.analyze_sms",
            return_value=spam_result
        ):
            analysis_response = self.client.post(
                self.analysis_url,
                self.form_data,
                follow=True
            )

        self.assertEqual(analysis_response.status_code, 200)

        self.assertEqual(
            analysis_response.context["result"]["label"],
            "Spam"
        )

        # Stage 2: Submit a community report.
        report_url = reverse("report_number")

        with patch(
            "sms_classifier.analyze_sms",
            return_value=spam_result
        ):
            report_response = self.client.post(
                report_url,
                {
                    "sender_phone": "2025550125",
                    "message": self.message,
                    "scam_category": "bank_impersonation",
                    "share_message": "on",
                },
                follow=True
            )

        self.assertEqual(report_response.status_code, 200)

        # Verify the phone number and report were saved.
        self.assertEqual(PhoneNumber.objects.count(), 1)
        self.assertEqual(PhoneReport.objects.count(), 1)

        phone = PhoneNumber.objects.get(
            number="+12025550125"
        )

        self.assertEqual(phone.report_count, 1)

        report = PhoneReport.objects.get(
            phone_number=phone
        )

        self.assertEqual(report.user, self.user)
        self.assertEqual(
            report.scam_category,
            "bank_impersonation"
        )
        self.assertTrue(report.share_message)
        self.assertEqual(report.message, self.message)

        # Stage 3: Search for the reported phone number.
        lookup_response = self.client.post(
            reverse("home"),
            {
                "phone_number": "2025550125",
                "country_code": "US",
            }
        )

        self.assertEqual(lookup_response.status_code, 200)

        self.assertTrue(lookup_response.context["searched"])
        self.assertTrue(lookup_response.context["number_found"])

        self.assertEqual(
            lookup_response.context["report_count"],
            1
        )

        self.assertEqual(
            lookup_response.context["unique_reporters"],
            1
        )

        shared_messages = lookup_response.context["shared_messages"]

        self.assertEqual(len(shared_messages), 1)

        self.assertEqual(
            shared_messages[0].message,
            self.message
        )

    def test_community_reporting_rejects_invalid_and_duplicate_reports(self):

        report_url = reverse("report_number")

        spam_result = {
            "prediction": 1,
            "label": "Spam",
            "confidence": 0.98,
        }

        not_spam_result = {
            "prediction": 0,
            "label": "Not Spam",
            "confidence": 0.97,
        }

        report_data = {
            "sender_phone": "2025550125",
            "message": self.message,
            "scam_category": "bank_impersonation",
        }

        # Case 1: Reject a message classified as Not Spam.
        with patch(
            "sms_classifier.analyze_sms",
            return_value=not_spam_result
        ):
            response = self.client.post(
                report_url,
                report_data
            )

        self.assertRedirects(
            response,
            self.analysis_url
        )

        self.assertEqual(PhoneNumber.objects.count(), 0)
        self.assertEqual(PhoneReport.objects.count(), 0)

        # Case 2: Reject an invalid phone number.
        invalid_data = report_data.copy()
        invalid_data["sender_phone"] = "123"

        with patch(
            "sms_classifier.analyze_sms",
            return_value=spam_result
        ):
            response = self.client.post(
                report_url,
                invalid_data
            )

        self.assertRedirects(
            response,
            self.analysis_url
        )

        self.assertEqual(PhoneNumber.objects.count(), 0)
        self.assertEqual(PhoneReport.objects.count(), 0)

        # Case 3: Accept the first report.
        with patch(
            "sms_classifier.analyze_sms",
            return_value=spam_result
        ):
            first_response = self.client.post(
                report_url,
                report_data
            )

        self.assertRedirects(
            first_response,
            reverse("home")
        )

        self.assertEqual(PhoneReport.objects.count(), 1)

        phone = PhoneNumber.objects.get(
            number="+12025550125"
        )

        self.assertEqual(phone.report_count, 1)

        # Case 4: Prevent a duplicate report.
        with patch(
            "sms_classifier.analyze_sms",
            return_value=spam_result
        ):
            duplicate_response = self.client.post(
                report_url,
                report_data
            )

        self.assertRedirects(
            duplicate_response,
            reverse("home")
        )

        self.assertEqual(PhoneReport.objects.count(), 1)
        self.assertEqual(phone.report_count, 1)

    def test_complete_browser_extension_analysis_workflow(self):

        extension_message = (
            "Your account is suspended. "
            "Click http://bit.ly/verify immediately."
        )

        mock_prediction = {
            "prediction": 1,
            "label": "Spam",
            "confidence": 0.885,
        }

        mock_url_analysis = {
            "urls_found": True,
            "urls": ["http://bit.ly/verify"],
            "findings": [
                "Uses an unencrypted HTTP connection.",
                "Uses a shortened URL that hides its destination.",
            ],
            "risk_level": "Suspicious indicators found",
        }

        mock_features = [
            ("suspended", 0.75),
            ("immediately", 0.45),
        ]

        mock_summary_text = (
            "The words suspended and immediately "
            "support the Spam prediction."
        )

        # Mock the services used by the actual extension API.
        with patch(
            "website.extension_api.analyze_sms",
            return_value=mock_prediction
        ) as mock_classifier, patch(
            "website.extension_api.analyze_urls",
            return_value=mock_url_analysis
        ) as mock_url_analyzer, patch(
            "phishguard.lime_explanations.explain_prediction",
            return_value=mock_features
        ) as mock_explainer, patch(
            "phishguard.lime_explanations.summarize_lime_explanation",
            return_value=mock_summary_text
        ) as mock_summarizer:

            # Send a JSON request to the browser extension endpoint.
            response = self.client.post(
                self.extension_url,
                data=json.dumps({
                    "message": extension_message
                }),
                content_type="application/json"
            )

        # Verify the extension API returned a successful response.
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response["Content-Type"].split(";")[0],
            "application/json"
        )

        result = response.json()

        # Verify the ML prediction and confidence score.
        self.assertEqual(result["prediction"], 1)
        self.assertEqual(result["label"], "Spam")
        self.assertEqual(result["confidence_percent"], 88.5)

        # Verify URL analysis.
        self.assertEqual(
            result["url_analysis"],
            mock_url_analysis
        )

        self.assertTrue(
            result["url_analysis"]["urls_found"]
        )

        self.assertEqual(
            result["url_analysis"]["urls"],
            ["http://bit.ly/verify"]
        )

        # Verify LIME features.
        self.assertEqual(
            result["lime_features"],
            [
                {
                    "word": "suspended",
                    "weight": 0.75,
                    "direction": "supports",
                },
                {
                    "word": "immediately",
                    "weight": 0.45,
                    "direction": "supports",
                },
            ]
        )

        # Verify the LIME summary.
        self.assertEqual(
            result["lime_summary"],
            mock_summary_text
        )

        # Verify all analysis services were called correctly.
        mock_classifier.assert_called_once_with(
            extension_message
        )

        mock_url_analyzer.assert_called_once_with(
            extension_message
        )

        mock_explainer.assert_called_once_with(
            extension_message,
            1
        )

        mock_summarizer.assert_called_once_with(
            mock_features,
            1
        )
