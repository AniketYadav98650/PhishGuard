
from django.urls import path
from . import views
from . import extension_api

urlpatterns = [
    path("", views.home, name="home"),
    path("analyze-sms/", views.analyze_sms_view, name="analyze_sms"),
    path("report-number/", views.report_number_view, name="report_number"),

    # Browser extension API
    path(
        "api/extension/analyze/",
        extension_api.extension_analyze,
        name="extension_analyze"
    ),
]
