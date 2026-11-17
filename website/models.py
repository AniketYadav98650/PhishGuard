
from django.conf import settings
from django.db import models


class PhoneNumber(models.Model):
    number = models.CharField(max_length=20, unique=True, db_index=True)
    report_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.number



class PhoneReport(models.Model):

    SCAM_CATEGORY_CHOICES = [
        ("bank_impersonation", "Bank impersonation"),
        ("prize_lottery", "Prize or lottery scam"),
        ("phishing", "Phishing or suspicious link"),
        ("payment_financial", "Payment or financial scam"),
        ("delivery_package", "Delivery or package scam"),
        ("other", "Other"),
    ]

    phone_number = models.ForeignKey(
        PhoneNumber,
        on_delete=models.CASCADE,
        related_name="reports",
    )

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
    )

    message = models.TextField(blank=True, default="")

    scam_category = models.CharField(
        max_length=30,
        choices=SCAM_CATEGORY_CHOICES,
        default="other",
    )

    share_message = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["phone_number", "user"],
                name="unique_phone_report_per_user",
            )
        ]

    def __str__(self):
        return f"{self.phone_number.number} reported by {self.user.username}"

# Stores the history of successful SMS analyses.
class SMSAnalysis(models.Model):

    PREDICTION_CHOICES = [
        ("spam", "Spam"),
        ("not_spam", "Not Spam"),
    ]

    SENDER_IDENTITY_CHOICES = [
        ("known_contact", "Known contact"),
        ("recognized_organization", "Recognized organization"),
        ("unknown", "Unknown sender"),
    ]

    EXPECTED_MESSAGE_CHOICES = [
        ("yes", "Yes"),
        ("no", "No"),
        ("not_sure", "Not sure"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sms_analyses",
    )

    message = models.TextField()

    prediction = models.CharField(
        max_length=10,
        choices=PREDICTION_CHOICES,
    )

    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    sender_identity = models.CharField(
        max_length=30,
        choices=SENDER_IDENTITY_CHOICES,
        default="unknown",
    )

    expected_message = models.CharField(
        max_length=10,
        choices=EXPECTED_MESSAGE_CHOICES,
        default="not_sure",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.get_prediction_display()}"


# Stores user feedback about an SMS prediction.
class PredictionFeedback(models.Model):

    analysis = models.ForeignKey(
        SMSAnalysis,
        on_delete=models.CASCADE,
        related_name="feedback",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="prediction_feedback",
    )

    is_correct = models.BooleanField()

    comments = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["analysis", "user"],
                name="unique_feedback_per_user_per_analysis",
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback by {self.user.username}"
