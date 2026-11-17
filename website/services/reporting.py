
import phonenumbers
from phonenumbers import PhoneNumberFormat
from website.models import PhoneReport


def normalize_phone_number(phone_number, region="US"):
    """
    Validate a phone number and return its normalized
    international E.164 representation.
    """

    if not isinstance(phone_number, str):
        raise ValueError("Phone number must be text.")

    phone_number = phone_number.strip()

    if not phone_number:
        raise ValueError("Phone number cannot be empty.")

    try:
        parsed_number = phonenumbers.parse(
            phone_number,
            region
        )

        if not phonenumbers.is_possible_number(parsed_number):
            raise ValueError("Phone number has an invalid length.")

        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError("Phone number is not valid.")

        return phonenumbers.format_number(
            parsed_number,
            PhoneNumberFormat.E164
        )

    except phonenumbers.NumberParseException as exc:
        raise ValueError("Unable to parse phone number.") from exc



def validate_scam_category(category):
        """
        Validate a scam category against the categories
        defined by the PhoneReport model.

        Returns the validated category or raises ValueError.
        """

        if not isinstance(category, str) or not category.strip():
            raise ValueError("Scam category is required.")

        valid_categories = {
            choice[0]
            for choice in PhoneReport.SCAM_CATEGORY_CHOICES
        }

        if category not in valid_categories:
            raise ValueError("Invalid scam category.")

        return category


def is_message_shareable(share_message, message):
    """
    Determine whether a reported message is eligible
    for public display.

    A message can be shared only when the user has
    consented and the message is not empty.
    """

    return bool(share_message and message and message.strip())


