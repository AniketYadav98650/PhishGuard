
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from website.models import PhoneNumber, PhoneReport


class CommunityReportingComponentTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reporter",
            password="testpassword123"
        )

        self.client.force_login(self.user)

        self.report_url = reverse("report_number")

        self.valid_data = {
            "sender_phone": "2025550125",
            "message": "Your bank account needs verification.",
            "scam_category": "bank_impersonation",
        }

    @patch("sms_classifier.analyze_sms")
    def test_valid_spam_report_is_saved(self, mock_analyze):
        mock_analyze.return_value = {
            "prediction": 1,
            "confidence": 0.98,
        }

        response = self.client.post(
            self.report_url,
            self.valid_data
        )

        self.assertRedirects(response, reverse("home"))

        self.assertEqual(PhoneNumber.objects.count(), 1)
        self.assertEqual(PhoneReport.objects.count(), 1)

        phone = PhoneNumber.objects.get(number="+12025550125")

        self.assertEqual(phone.report_count, 1)

        report = PhoneReport.objects.get(phone_number=phone)

        self.assertEqual(
            report.scam_category,
            "bank_impersonation"
        )

    @patch("sms_classifier.analyze_sms")
    def test_duplicate_report_is_not_saved_twice(self, mock_analyze):
        mock_analyze.return_value = {
            "prediction": 1,
            "confidence": 0.98,
        }

        self.client.post(self.report_url, self.valid_data)
        response = self.client.post(self.report_url, self.valid_data)

        self.assertRedirects(response, reverse("home"))

        self.assertEqual(PhoneReport.objects.count(), 1)

        phone = PhoneNumber.objects.get(number="+12025550125")

        self.assertEqual(phone.report_count, 1)

    @patch("sms_classifier.analyze_sms")
    def test_not_spam_message_cannot_be_reported(self, mock_analyze):
        mock_analyze.return_value = {
            "prediction": 0,
            "confidence": 0.95,
        }

        response = self.client.post(
            self.report_url,
            self.valid_data
        )

        self.assertRedirects(response, reverse("analyze_sms"))
        self.assertEqual(PhoneReport.objects.count(), 0)
        self.assertEqual(PhoneNumber.objects.count(), 0)

    @patch("sms_classifier.analyze_sms")
    def test_invalid_phone_number_is_rejected(self, mock_analyze):
        mock_analyze.return_value = {
            "prediction": 1,
            "confidence": 0.98,
        }

        invalid_data = self.valid_data.copy()
        invalid_data["sender_phone"] = "123"

        response = self.client.post(
            self.report_url,
            invalid_data
        )

        self.assertRedirects(response, reverse("analyze_sms"))
        self.assertEqual(PhoneReport.objects.count(), 0)
        self.assertEqual(PhoneNumber.objects.count(), 0)

    def test_private_report_message_is_hidden_from_public_lookup(self):
        phone = PhoneNumber.objects.create(
            number="+12025550125",
            report_count=1
        )

        PhoneReport.objects.create(
            phone_number=phone,
            user=self.user,
            message="Private suspicious message",
            scam_category="phishing",
            share_message=False
        )

        response = self.client.post(
            reverse("home"),
            {
                "phone_number": "2025550125",
                "country_code": "US",
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["shared_messages"]),
            []
        )

        self.assertEqual(response.context["report_count"], 1)

    def test_consented_report_message_appears_in_public_lookup(self):
        phone = PhoneNumber.objects.create(
            number="+12025550125",
            report_count=1
        )

        PhoneReport.objects.create(
            phone_number=phone,
            user=self.user,
            message="Suspicious delivery payment message",
            scam_category="delivery_package",
            share_message=True
        )

        response = self.client.post(
            reverse("home"),
            {
                "phone_number": "2025550125",
                "country_code": "US",
            }
        )

        self.assertEqual(response.status_code, 200)

        shared_messages = list(response.context["shared_messages"])

        self.assertEqual(len(shared_messages), 1)
        self.assertEqual(
            shared_messages[0].message,
            "Suspicious delivery payment message"
        )
