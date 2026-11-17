
from django.test import SimpleTestCase

from website.services.reporting import normalize_phone_number
from website.services.reporting import validate_scam_category
from website.services.reporting import is_message_shareable
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from website.models import PhoneNumber, PhoneReport
from django.test import SimpleTestCase, TestCase


class PhoneNumberValidationTests(SimpleTestCase):

    def test_valid_us_phone_number(self):
        result = normalize_phone_number("2025550125")

        self.assertEqual(result, "+12025550125")

    def test_empty_phone_number_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_phone_number("")

    def test_invalid_phone_number_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_phone_number("123")

class ScamCategoryValidationTests(SimpleTestCase):

        def test_valid_scam_category(self):
            result = validate_scam_category("phishing")

            self.assertEqual(result, "phishing")

        def test_invalid_scam_category(self):
            with self.assertRaises(ValueError):
                validate_scam_category("fake_category")

        def test_empty_scam_category(self):
            with self.assertRaises(ValueError):
                validate_scam_category("")


class MessageSharingTests(SimpleTestCase):

    def test_message_shared_with_user_consent(self):
        result = is_message_shareable(
            True,
            "This number sent a suspicious message."
        )

        self.assertTrue(result)

    def test_message_not_shared_without_consent(self):
        result = is_message_shareable(
            False,
            "This number sent a suspicious message."
        )

        self.assertFalse(result)

    def test_empty_message_is_not_shareable(self):
        result = is_message_shareable(True, "   ")

        self.assertFalse(result)

class DuplicateReportProtectionTests(TestCase):

    def test_same_user_cannot_report_same_number_twice(self):
        user = User.objects.create_user(
            username="user_one",
            password="testpassword123"
        )

        phone = PhoneNumber.objects.create(
            number="+12025550125"
        )

        PhoneReport.objects.create(
            phone_number=phone,
            user=user,
            scam_category="phishing"
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PhoneReport.objects.create(
                    phone_number=phone,
                    user=user,
                    scam_category="phishing"
                )

        self.assertEqual(
            PhoneReport.objects.filter(
                phone_number=phone,
                user=user
            ).count(),
            1
        )

    def test_different_users_can_report_same_number(self):
        user_one = User.objects.create_user(
            username="user_one",
            password="testpassword123"
        )

        user_two = User.objects.create_user(
            username="user_two",
            password="testpassword123"
        )

        phone = PhoneNumber.objects.create(
            number="+12025550125"
        )

        PhoneReport.objects.create(
            phone_number=phone,
            user=user_one
        )

        PhoneReport.objects.create(
            phone_number=phone,
            user=user_two
        )

        self.assertEqual(
            PhoneReport.objects.filter(
                phone_number=phone
            ).count(),
            2
        )

    def test_same_user_can_report_different_numbers(self):
        user = User.objects.create_user(
            username="user_one",
            password="testpassword123"
        )

        phone_one = PhoneNumber.objects.create(
            number="+12025550125"
        )

        phone_two = PhoneNumber.objects.create(
            number="+12025550126"
        )

        PhoneReport.objects.create(
            phone_number=phone_one,
            user=user
        )

        PhoneReport.objects.create(
            phone_number=phone_two,
            user=user
        )

        self.assertEqual(
            PhoneReport.objects.filter(user=user).count(),
            2
        )
