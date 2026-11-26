
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from website.models import PhoneNumber, PhoneReport


class PhoneLookupComponentTests(TestCase):

    def setUp(self):
        self.lookup_url = reverse("home")

        self.user = User.objects.create_user(
            username="lookup_tester",
            password="testpassword123"
        )

    def test_existing_phone_number_displays_community_reports(self):
        phone = PhoneNumber.objects.create(
            number="+12025550125",
            report_count=1
        )

        PhoneReport.objects.create(
            phone_number=phone,
            user=self.user,
            message="Suspicious bank verification message.",
            scam_category="bank_impersonation",
            share_message=True
        )

        response = self.client.post(
            self.lookup_url,
            {
                "phone_number": "2025550125",
                "country_code": "US"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["searched"])
        self.assertTrue(response.context["number_found"])
        self.assertEqual(response.context["report_count"], 1)
        self.assertEqual(response.context["unique_reporters"], 1)

        self.assertEqual(
            len(response.context["shared_messages"]),
            1
        )

    def test_unknown_valid_phone_number_shows_no_reports(self):
        response = self.client.post(
            self.lookup_url,
            {
                "phone_number": "2025550126",
                "country_code": "US"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["searched"])
        self.assertFalse(response.context["number_found"])
        self.assertEqual(response.context["error"], "")

        self.assertEqual(PhoneNumber.objects.count(), 0)

    def test_invalid_phone_number_displays_validation_error(self):
        response = self.client.post(
            self.lookup_url,
            {
                "phone_number": "123",
                "country_code": "US"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["searched"])
        self.assertFalse(response.context["number_found"])

        self.assertIn(
            "valid phone number",
            response.context["error"].lower()
        )

        self.assertEqual(PhoneNumber.objects.count(), 0)
