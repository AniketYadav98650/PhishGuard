# PhishGuard – Intelligent Spam Message Detection

PhishGuard is a Django-based web application designed to identify suspicious SMS messages and URLs. It provides spam classification, prediction confidence scores, LIME-based explanations, phone-number lookup, and community scam reporting. A Chrome browser extension also allows users to submit message text for analysis through the PhishGuard API.

**Repository:** [PhishGuard – GitHub](https://github.com/AniketYadav98650/PhishGuard)  
**Branch:** `main`  
**Team Members:** Aniket Kumar Yadav and Sahana Puri

---

## 1. Project Features

- **SMS Classification:** Classifies submitted messages as Spam or Not Spam and provides a confidence score.
- **URL Analysis:** Analyzes URLs found in submitted messages.
- **Prediction Explanations:** Uses LIME to explain supported model predictions.
- **Phone-Number Lookup:** Provides lookup functionality for suspicious phone numbers.
- **Community Scam Reporting:** Allows users to submit scam reports.
- **User Authentication:** Supports user registration and login.
- **Chrome Browser Extension:** Provides an additional interface for submitting message text to the PhishGuard analysis API.

## 2. Technologies Used

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Machine Learning:** scikit-learn, TF-IDF
- **Natural Language Processing:** NLTK
- **Explainable AI:** LIME
- **Database:** SQLite
- **Browser Extension:** Chrome Extension APIs

## 3. Project Structure

```text
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

The trained `model.pkl` and `vectorizer.pkl` files are required for SMS classification. They should remain in the project root alongside `sms_classifier.py`.

## 4. Requirements

- Python installed on your system
- pip package manager
- Google Chrome (for the browser extension)
- Git (to clone the repository)

## 5. Installation and Setup

The following instructions use Windows PowerShell. Run the commands from the project directory containing `manage.py`.

### Step 1: Clone the repository

```powershell
git clone https://github.com/AniketYadav98650/PhishGuard.git
cd PhishGuard
```

### Step 2: Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

### Step 3: Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Prepare the database

```powershell
python manage.py migrate
```

### Step 5: Start the development server

```powershell
python manage.py runserver
```

Open the application in your browser:

http://127.0.0.1:8000/

To stop the development server, press `Ctrl + C` in the terminal.

## 6. Chrome Browser Extension Setup

1. Start the PhishGuard Django application.
2. Open Google Chrome.
3. Navigate to `chrome://extensions/`.
4. Enable **Developer mode**.
5. Click **Load unpacked**.
6. Select the `browser_extension` folder from the cloned repository.
7. Open the PhishGuard extension and submit message text for analysis.

**Note:** Keep the Django development server running while using the extension.

## 7. Automated Testing

The automated test suite is organized into three testing levels:

- Unit testing
- Component testing
- System testing

The latest recorded full-suite execution passed **40 tests**, consisting of 12 unit tests, 24 component tests, and 4 system workflow tests.

Run the following commands from the project directory with the virtual environment activated.

### 7.1 Unit Tests – 12 Tests

These tests cover individual functions and business rules, including phone-number normalization, validation, consent handling, and duplicate-report protection.

```powershell
python manage.py test website.tests.test_unit_reporting -v 2
```

### 7.2 Component Tests – 24 Tests

Component tests verify the interaction of related parts within individual application features.

| Component | Tests | Command |
|---|---:|---|
| Authentication | 3 | `python manage.py test website.tests.test_component_authentication -v 2` |
| Browser Extension Analysis API | 4 | `python manage.py test website.tests.test_component_extension_api -v 2` |
| Phone-Number Lookup | 3 | `python manage.py test website.tests.test_component_phone_lookup -v 2` |
| Community Reporting | 6 | `python manage.py test website.tests.test_component_reporting -v 2` |
| SMS Analysis | 5 | `python manage.py test website.tests.test_component_sms_analysis -v 2` |
| URL Analysis | 3 | `python manage.py test website.tests.test_component_url_analysis -v 2` |
| **Total** | **24** | |

### 7.3 System Tests – 4 Workflow Tests

These tests exercise complete application workflows, including:

- SMS analysis workflow.
- Community reporting and phone-number lookup workflow.
- Invalid and duplicate report handling.
- Browser-extension analysis API workflow.

Run the system tests:

```powershell
python manage.py test website.tests.test_system_workflows -v 2
```

### 7.4 Run the Complete Test Suite

To execute all unit, component, and system tests:

```powershell
python manage.py test -v 2
```

The latest recorded result was:

```text
Ran 40 tests
OK
```

### 7.5 Additional Django Checks

Check the Django project configuration:

```powershell
python manage.py check
```

**Testing Limitation:** Some system workflow tests mock services or component boundaries. Passing automated tests verify the tested code paths; they do not measure live machine-learning accuracy or replace manual testing of the Chrome extension in a browser.

## 8. Machine Learning Model Files

The application uses the following files for SMS classification:

- `model.pkl` – Trained machine-learning model.
- `vectorizer.pkl` – Fitted TF-IDF vectorizer.
- `sms_classifier.py` – Python module responsible for SMS classification.

Ensure these files are available in the project root before running the application.

## 9. Database Information

PhishGuard uses SQLite as its development database. Django migrations create and update the database schema.

Run the following command whenever database migrations need to be applied:

```powershell
python manage.py migrate
```

## 10. Additional Notes

- Run Django management commands from the directory containing `manage.py`.
- Activate the virtual environment before installing dependencies or running the application.
- An internet connection may be required if necessary NLTK resources are not already installed.
- Do not commit virtual environments, passwords, secret keys, or machine-specific local database files to the public repository.
