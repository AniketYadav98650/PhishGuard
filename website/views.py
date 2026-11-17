from django.db.models import Count
import phonenumbers
import pycountry

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .models import PhoneNumber, PhoneReport, SMSAnalysis
from phishguard.url_analysis import analyze_urls


def get_country_codes():
    countries = []

    for region in sorted(phonenumbers.SUPPORTED_REGIONS):
        calling_code = phonenumbers.country_code_for_region(region)

        if not calling_code:
            continue

        country = pycountry.countries.get(alpha_2=region)
        country_name = country.name if country else region

        countries.append({
            "region": region,
            "name": country_name,
            "code": calling_code,
        })

    return sorted(countries, key=lambda item: item["name"])



@require_http_methods(["GET", "POST"])
def home(request):
    countries = get_country_codes()

    context = {
        "countries": countries,
        "selected_region": "US",
        "searched": False,
        "phone_number": "",
        "number_found": False,
        "error": "",
    }

    if request.method == "POST":
        phone_number = request.POST.get("phone_number", "").strip()
        selected_region = request.POST.get("country_code", "US").strip()

        if selected_region not in phonenumbers.SUPPORTED_REGIONS:
            context["error"] = "Please select a valid country."

        else:
            context["selected_region"] = selected_region

            try:
                parsed_number = phonenumbers.parse(
                    phone_number, selected_region
                )

                if not phonenumbers.is_possible_number(parsed_number):
                    raise phonenumbers.NumberParseException(
                        0, "Invalid phone number length."
                    )

                if not phonenumbers.is_valid_number(parsed_number):
                    raise phonenumbers.NumberParseException(
                        0, "Invalid phone number."
                    )

                international_number = phonenumbers.format_number(
                    parsed_number,
                    phonenumbers.PhoneNumberFormat.E164,
                )

                context["searched"] = True
                context["phone_number"] = phonenumbers.national_significant_number(
                    parsed_number
                )

                record = PhoneNumber.objects.filter(
                    number=international_number
                ).first()

                if record:
                    reports = record.reports.all()

                    context["number_found"] = True
                    context["report_count"] = record.report_count

                    # Count distinct community reporters.
                    context["unique_reporters"] = (
                        reports.values("user_id").distinct().count()
                    )

                    # Show the five most recent reports.
                    context["recent_reports"] = reports.order_by(
                        "-created_at"
                    )[:5]

                    # Count reports by scam category.
                    category_counts = (
                        reports.values("scam_category")
                        .annotate(total=Count("id"))
                        .order_by("-total")
                    )

                    category_labels = dict(
                        PhoneReport.SCAM_CATEGORY_CHOICES
                    )

                    context["scam_categories"] = [
                        {
                            "label": category_labels.get(
                                item["scam_category"],
                                "Other",
                            ),
                            "count": item["total"],
                        }
                        for item in category_counts
                    ]

                    # Only retrieve messages explicitly approved for sharing.
                    context["shared_messages"] = (
                        reports.filter(
                            share_message=True
                        )
                        .exclude(message="")
                        .order_by("-created_at")[:5]
                    )

            except phonenumbers.NumberParseException:
                context["error"] = (
                    "Please enter a valid phone number for the selected country."
                )
                context["phone_number"] = phone_number

    return render(request, "website/home.html", context)



@login_required(login_url="login")
def analyze_sms_view(request):
    from sms_classifier import analyze_sms

    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        sender_phone = request.POST.get("sender_phone", "").strip()

        sender_identity = request.POST.get(
            "sender_identity", "unknown"
        ).strip()

        expected_message = request.POST.get(
            "expected_message", "not_sure"
        ).strip()

        result = None
        error = ""

        if sender_identity not in {
            "known_contact",
            "recognized_organization",
            "unknown",
        }:
            error = "Please select a valid sender identity."

        elif expected_message not in {
            "yes",
            "no",
            "not_sure",
        }:
            error = "Please select whether you expected this message."

        # Validate the optional sender phone number.
        if sender_phone:
            try:
                parsed_phone = phonenumbers.parse(sender_phone, "US")

                if not phonenumbers.is_valid_number(parsed_phone):
                    error = "Please enter a valid sender phone number."

            except phonenumbers.NumberParseException:
                error = "Please enter a valid sender phone number."

        # Validate and analyze the SMS.
        if not error:
            if not message:
                error = "Please enter an SMS message."
            else:

                try:
                    result = analyze_sms(message)

                    # Analyze URLs separately from the ML prediction.
                    result["url_analysis"] = analyze_urls(message)

                    # Build contextual indicators separately from the ML prediction.
                    context_findings = []

                    # 1. Evaluate sender identity.
                    if sender_identity == "known_contact":
                        sender_identity_label = "Known contact"
                        context_findings.append(
                            "You identified the sender as a known contact."
                        )

                    elif sender_identity == "recognized_organization":
                        sender_identity_label = "Recognized organization"
                        context_findings.append(
                            "You identified the sender as a recognized organization. "
                            "Its identity has not been independently verified."
                        )

                    else:
                        sender_identity_label = "Unknown sender"
                        context_findings.append(
                            "The sender is unknown. Verify the sender independently."
                        )

                    # 2. Evaluate whether the message was expected.
                    if expected_message == "yes":
                        expected_message_label = "Yes"
                        context_findings.append(
                            "You indicated that you were expecting this message."
                        )

                    elif expected_message == "no":
                        expected_message_label = "No"
                        context_findings.append(
                            "You indicated that you were not expecting this message."
                        )

                    else:
                        expected_message_label = "Not sure"
                        context_findings.append(
                            "You are unsure whether this message was expected."
                        )

                    # 3. Include URL inspection findings.
                    url_analysis = result["url_analysis"]

                    if url_analysis["urls_found"]:
                        if url_analysis["findings"]:
                            context_findings.extend(url_analysis["findings"])
                        else:
                            context_findings.append(
                                "No obvious suspicious URL indicators were detected. "
                                "This does not guarantee that the link is safe."
                            )
                    else:
                        context_findings.append(
                            "No URL was detected in this message."
                        )

                    # 4. Calculate a simple contextual caution level.
                    caution_count = 0

                    if sender_identity == "unknown":
                        caution_count += 1

                    if expected_message == "no":
                        caution_count += 1

                    if expected_message == "not_sure":
                        caution_count += 1

                    if url_analysis["findings"]:
                        caution_count += len(url_analysis["findings"])

                    if caution_count >= 2:
                        context_level = "Additional caution recommended"
                    elif caution_count == 1:
                        context_level = "Some caution recommended"
                    else:
                        context_level = "No additional context concerns identified"

                    # 5. Store contextual results separately from ML results.
                    result["context_analysis"] = {
                        "sender_identity_label": sender_identity_label,
                        "expected_message_label": expected_message_label,
                        "findings": context_findings,
                        "level": context_level,
                    }

                    result["confidence_percent"] = round(
                        result["confidence"] * 100, 1
                    )

                    # Generate a LIME explanation without changing
                    # the original ML prediction.
                    try:
                        from phishguard.lime_explanations import (
                            explain_prediction,
                            summarize_lime_explanation,
                        )

                        features = explain_prediction(
                            message,
                            result["prediction"],
                        )

                        result["lime_features"] = [
                            {
                                "word": word,
                                "weight": round(float(weight), 4),
                                "direction": (
                                    "supports"
                                    if weight > 0
                                    else "opposes"
                                    if weight < 0
                                    else "neutral"
                                ),
                            }
                            for word, weight in features
                        ]

                        result["lime_summary"] = summarize_lime_explanation(
                            features,
                            result["prediction"],
                        )

                    except Exception:
                        # An explanation failure must not prevent
                        # the original ML prediction from being displayed.
                        result["lime_features"] = []
                        result["lime_summary"] = (
                            "The prediction was generated, but its explanation "
                            "could not be generated at this time."
                        )
                    # Save the successful SMS analysis to the user's history.
                    SMSAnalysis.objects.create(
                        user=request.user,
                        message=message,
                        prediction=(
                            "spam"
                            if result["prediction"] == 1
                            else "not_spam"
                        ),
                        confidence=result["confidence_percent"],
                        sender_identity=sender_identity,
                        expected_message=expected_message,
                    )
                except ValueError as exc:
                    error = str(exc)

        # Store the result and associated form data for one GET request.
        request.session["sms_analysis_result"] = result
        request.session["sms_analysis_error"] = error
        request.session["sms_analysis_message"] = message
        request.session["sms_analysis_sender_phone"] = sender_phone
        request.session["sms_analysis_sender_identity"] = sender_identity
        request.session["sms_analysis_expected_message"] = expected_message

        return redirect("analyze_sms")

    # Retrieve and remove the saved values so a refresh won't repeat them.
    result = request.session.pop("sms_analysis_result", None)
    error = request.session.pop("sms_analysis_error", "")
    message = request.session.pop("sms_analysis_message", "")
    sender_phone = request.session.pop("sms_analysis_sender_phone", "")
    sender_identity = request.session.pop(
        "sms_analysis_sender_identity", "unknown"
    )

    expected_message = request.session.pop(
        "sms_analysis_expected_message", "not_sure"
    )

    return render(
        request,
        "website/analyze_sms.html",
        {
            "result": result,
            "error": error,
            "message": message,
            "sender_phone": sender_phone,
            "sender_identity": sender_identity,
            "expected_message": expected_message,
        },
    )


from django.contrib import messages
from django.db.models import F
from django.shortcuts import redirect
from django.views.decorators.http import require_POST


@login_required(login_url="login")
@require_POST
def report_number_view(request):
    from django.db import transaction

    sender_phone = request.POST.get("sender_phone", "").strip()
    message = request.POST.get("message", "").strip()

    # Read the scam category and sharing consent.
    scam_category = request.POST.get("scam_category", "other").strip()
    share_message = request.POST.get("share_message") == "on"

    if not sender_phone or not message:
        messages.error(
            request,
            "Please analyze an SMS and provide its sender's phone number."
        )
        return redirect("analyze_sms")

    # Validate the scam category against the model's allowed choices.
    valid_categories = {
        choice[0] for choice in PhoneReport.SCAM_CATEGORY_CHOICES
    }

    if scam_category not in valid_categories:
        messages.error(request, "Please select a valid scam category.")
        return redirect("analyze_sms")

    # Re-run the AI prediction on the server.
    from sms_classifier import analyze_sms

    try:
        result = analyze_sms(message)
    except ValueError:
        messages.error(request, "The SMS could not be analyzed.")
        return redirect("analyze_sms")

    if result["prediction"] != 1:
        messages.error(
            request,
            "Only messages classified as Spam can be reported."
        )
        return redirect("analyze_sms")

    # Validate and normalize the sender's phone number.
    try:
        parsed_phone = phonenumbers.parse(sender_phone, "US")

        if not phonenumbers.is_valid_number(parsed_phone):
            raise phonenumbers.NumberParseException(
                0, "Invalid phone number."
            )

        international_number = phonenumbers.format_number(
            parsed_phone,
            phonenumbers.PhoneNumberFormat.E164,
        )

    except phonenumbers.NumberParseException:
        messages.error(request, "Please enter a valid phone number.")
        return redirect("analyze_sms")

    # Save one report per user per phone number.
    with transaction.atomic():
        phone_record, _ = PhoneNumber.objects.get_or_create(
            number=international_number
        )

        report, created = PhoneReport.objects.get_or_create(
            phone_number=phone_record,
            user=request.user,
            defaults={
                "message": message,
                "scam_category": scam_category,
                "share_message": share_message,
            },
        )

        if created:
            PhoneNumber.objects.filter(pk=phone_record.pk).update(
                report_count=F("report_count") + 1
            )

    if created:
        messages.success(
            request,
            "Thank you. Your community report has been recorded."
        )
    else:
        messages.info(
            request,
            "You have already reported this phone number."
        )

    return redirect("home")
