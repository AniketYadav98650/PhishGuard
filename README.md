# PhishGuard -- Intelligent Spam Message Detection

PhishGuard is a Django web application for analyzing suspicious SMS
messages and URLs, explaining predictions, and supporting community
reporting and lookup of suspicious phone numbers. A Chrome browser
extension provides an additional way to submit message text for
analysis.

**Repository:** https://github.com/AniketYadav98650/PhishGuard\
**Branch:** `main`\
**Team:** Aniket Kumar Yadav and Sahana Puri

## Features

-   SMS classification as **Spam** or **Not Spam**, with a confidence
    score.
-   URL analysis for links found in submitted messages.
-   LIME-based explanations of supported predictions.
-   Phone-number lookup and community scam reporting.
-   User registration and login.
-   Chrome extension for submitting message text to the PhishGuard
    analysis API.

## Technologies

Python · Django · SQLite · HTML · CSS · JavaScript · scikit-learn ·
TF-IDF · NLTK · LIME

## Project Structure

``` text
PhishGuard/
├── accounts/
├── config/
├── phishguard/
├── website/
│   └── tests/
├── browser_extension/
├── model.pkl
├── vectorizer.pkl
├── sms_classifier.py
├── manage.py
└── requirements.txt
```

The trained `model.pkl` and `vectorizer.pkl` files are required for SMS
classification and should be located in the project root alongside
`sms_classifier.py`.

## Installation and Run Instructions

The following commands use Windows PowerShell. Run them from the project
directory containing `manage.py`.

### 1. Clone the repository

``` powershell
git clone https://github.com/AniketYadav98650/PhishGuard.git
cd PhishGuard
```

### 2. Create and activate a virtual environment

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

``` bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies and prepare the database

``` powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
```

### 4. Start the application

``` powershell
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser. Press `Ctrl + C` in the
terminal to stop the server.

## Chrome Browser Extension

1.  Start the PhishGuard Django application.
2.  Open Chrome and navigate to `chrome://extensions/`.
3.  Enable **Developer mode**.
4.  Select **Load unpacked**.
5.  Choose the `browser_extension` folder in the cloned repository.
6.  Open the PhishGuard extension popup and submit message text for
    analysis.

Keep the Django application running while using the extension.

## Automated Testing

PhishGuard's automated tests are organized into three levels. The latest
recorded full-suite run passed **40 tests**: 12 unit tests, 24 component
tests, and 4 system workflow tests.

Run commands from the directory containing `manage.py`, with the virtual
environment activated.

### Unit tests --- 12 tests

These tests check individual functions and business rules, including
phone-number normalization, validation, consent handling, and
duplicate-report protection.

``` powershell
python manage.py test website.tests.test_unit_reporting -v 2
```

### Component tests --- 24 tests across 6 components

Component tests verify how related parts of each feature work together.

  -----------------------------------------------------------------------------------------------------------------------------
  Component                                    Tests Command
  --------------------- ---------------------------- --------------------------------------------------------------------------
  Authentication                                   3 `python manage.py test website.tests.test_component_authentication -v 2`

  Browser extension                                4 `python manage.py test website.tests.test_component_extension_api -v 2`
  analysis API                                       

  Phone-number lookup                              3 `python manage.py test website.tests.test_component_phone_lookup -v 2`

  Community reporting                              6 `python manage.py test website.tests.test_component_reporting -v 2`

  SMS analysis                                     5 `python manage.py test website.tests.test_component_sms_analysis -v 2`

  URL analysis                                     3 `python manage.py test website.tests.test_component_url_analysis -v 2`
  -----------------------------------------------------------------------------------------------------------------------------

### System tests --- 4 workflow tests

These tests exercise complete workflows, including SMS analysis,
community reporting and lookup, invalid or duplicate reports, and the
browser-extension analysis API.

``` powershell
python manage.py test website.tests.test_system_workflows -v 2
```

### Run the complete test suite

Run all unit, component, and system tests together:

``` powershell
python manage.py test -v 2
```

The latest recorded result was:

``` text
Ran 40 tests
OK
```

To check the Django project configuration:

``` powershell
python manage.py check
```

**Testing limitation:** Some system workflow tests mock services or
component boundaries. Passing tests verify the tested code paths; they
do not measure live model accuracy or replace manual testing of the
Chrome extension in a browser.

## Notes

-   Run Django commands from the directory containing `manage.py`.
-   Keep the virtual environment activated when installing dependencies
    or running the project.
-   An internet connection may be needed if required NLTK resources are
    not already installed.
-   Do not commit virtual environments, secrets, or machine-specific
    local database files.
