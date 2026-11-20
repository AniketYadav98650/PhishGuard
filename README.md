# PhishGuard – Intelligent Spam Message Detection

## 1. Project Overview

PhishGuard is a web application developed using Python and Django to help users identify potentially fraudulent, spam, and phishing-related text messages.

The application uses machine learning to analyze SMS messages and classify them as either **Spam** or **Not Spam**. It also provides features that allow users to look up phone numbers and share information about suspicious activities through community scam reporting.

The main goal of this project is to make it easier for users to recognize suspicious messages and become more aware of potential scams.

## 2. Project Objectives

The main objectives of PhishGuard are:

- Develop a web-based application for SMS spam detection.
- Use machine learning to classify suspicious text messages.
- Provide information about potentially reported scam phone numbers.
- Allow users to submit and view community scam reports.
- Provide a simple interface for users to interact with the application.
- Test the application's functionality through automated unit and component tests.

## 3. Main Features

### SMS Analysis
Users can enter a text message and submit it for analysis. The application processes the message and predicts whether it is spam or not spam.

### Machine Learning Classification
The application uses a trained machine learning model and TF-IDF vectorization to classify SMS messages.

### Confidence Score
The application displays a confidence score associated with the classification result.

### Phone Number Lookup
Users can check available information about phone numbers through the application's lookup functionality.

### Community Scam Reporting
Users can submit reports about suspicious phone numbers and messages. Available reports can be viewed through the community reporting functionality.

### User Authentication
The application supports user registration and login.

### Automated Testing
The project includes automated tests to verify important application functions and interactions between application components.

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Django | Web application framework |
| SQLite | Database |
| HTML | Web page structure |
| CSS | Website styling |
| JavaScript | Frontend interactions |
| Scikit-learn | Machine learning |
| NLTK | Text preprocessing |
| TF-IDF | Text feature extraction |
| Pickle | Saving and loading trained model files |

## 5. Project Structure

```text
Intelligent-Spam-Message-Detection/
│
├── accounts/                   # User registration and login
│
├── config/                     # Django project configuration
│
├── phishguard/                 # Supporting project functionality
│
├── research/                   # Machine learning research files
│   ├── Model_Generator.ipynb
│   └── spam.csv
│
├── website/                    # Main application functionality
│   ├── services/               # Application service functions
│   ├── static/                 # CSS, JavaScript, and images
│   ├── templates/              # HTML templates
│   └── tests/                  # Automated tests
│
├── model.pkl                   # Trained machine learning model
├── vectorizer.pkl              # Trained TF-IDF vectorizer
├── sms_classifier.py           # SMS preprocessing and prediction
│
├── manage.py                   # Django management script
├── requirements.txt            # Required Python packages
├── .gitignore                  # Files excluded from GitHub
└── README.md                   # Project documentation
```

## 6. Requirements

Before running the project, make sure you have installed:

- Python
- pip (Python package installer)
- Git

Python compatibility: Use Python 3.12 or newer, with a version supported by all packages in requirements.txt. The application and complete 22-test suite were successfully executed on Windows using Python 3.14.

Git is required for cloning the repository but is optional when downloading the project as a ZIP file.

## 7. Installation and Setup

Follow these steps to download and run PhishGuard on your computer.

### Step 1: Clone the GitHub repository

```
git clone https://github.com/AniketYadav98650/PhishGuard.git
```

### Step 2: Navigate to the project directory

```
cd PhishGuard
```

### Step 3: Create a virtual environment

For Windows PowerShell:

```
python -m venv .venv
```

### Step 4: Activate the virtual environment

Windows: 

```
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, you can use Command Prompt instead:

```
.venv\Scripts\activate.bat
```

Once activated, you should see (.venv) at the beginning of your terminal prompt.

### Step 5: Install the required dependencies

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs the Python packages required by the application.

### Step 6: Set up the database

Run the following command:

```
python manage.py migrate
```

Django will create the local SQLite database and apply the required database migrations.

### Step 7: Start the application

```
python manage.py runserver
```

Open your browser and visit:

http://127.0.0.1:8000/

The PhishGuard homepage should now appear.

**Alternative Development Server Port**

If port 8000 is unavailable or access is denied, run:

```bash
python manage.py runserver 127.0.0.1:8080
```

Then open http://127.0.0.1:8080/ in your browser.

To stop the development server, press Ctrl + C in the terminal.

## 8. NLTK Resource Setup

PhishGuard uses NLTK for SMS text preprocessing.

The application automatically checks for the required NLTK resources:

- Punkt tokenizer
- Punkt tab tokenizer
- English stopwords

If any required resources are missing, the application attempts to download them automatically.

**Important:** An internet connection is required the first time missing NLTK resources are downloaded. Once downloaded, the resources are stored locally and can be reused.

No separate manual NLTK download command is required.

## 9. Running Automated Tests

PhishGuard includes automated tests for important application functionality.

The current project test suite contains **22 automated tests**, covering unit-level and component-level functionality.
The 22 automated tests are organized into three test modules. Each module can be executed independently to verify a specific testing category.

### Test Summary

| Test Type | Test Module | Number of Tests |
|---|---|---:|
| Unit Testing | `test_unit_reporting` | 12 |
| Component Testing – Community Reporting | `test_component_reporting` | 6 |
| Component Testing – SMS Analysis | `test_component_sms_analysis` | 4 |
| **Total** | | **22** |

All 22 automated tests were successfully executed together on Windows using Python 3.14.

## Unit Testing

Run the following command to execute the 12 unit tests:

```
python manage.py test website.tests.test_unit_reporting -v 2
```

These tests cover phone number normalization, validation rules, consent handling, and database uniqueness constraints.

## Component Testing — Community Reporting

Run the following command to execute the 6 community reporting component tests:

```
python manage.py test website.tests.test_component_reporting -v 2
```

These tests verify interactions within the community scam reporting workflow.

## Component Testing — SMS Analysis

Run the following command to execute the 4 SMS analysis component tests:

```
python manage.py test website.tests.test_component_sms_analysis -v 2
```

These tests verify interactions within the SMS analysis workflow.

## Complete Test Suite

To execute all 22 tests together:

```
python manage.py test website
```

### Additional Django checks

To check the application for configuration issues:

```
python manage.py check
```

To check whether database model changes require new migrations:

```
python manage.py makemigrations --check --dry-run
```

Django creates a temporary test database while running automated tests and removes it after the tests finish.

## 10. Test Coverage

The automated tests cover the following areas:

### Unit Tests

Unit tests verify individual functions and application logic, including:

- Phone number normalization.
- Scam category validation.
- Message-sharing consent validation.
- Database uniqueness constraints.

### Component Tests

Component tests verify how different parts of the application work together, including:

- Community scam report submission.
- Duplicate report handling.
- Invalid report handling.
- Public and private report visibility.
- SMS analysis and database integration.
- Authentication requirements.
- Handling failures in optional SMS explanations.

## 11. Machine Learning Model

PhishGuard uses a trained machine learning model to classify SMS messages.

The classification process includes:

1. Converting the message to lowercase.
2. Tokenizing the text.
3. Removing unnecessary words and punctuation.
4. Removing English stopwords.
5. Applying stemming.
6. Converting the processed text into numerical features using TF-IDF.
7. Passing the features to the trained classification model.
8. Returning the prediction and confidence score.

The following files are required for SMS classification:

- `model.pkl` – Contains the trained machine learning model.
- `vectorizer.pkl` – Contains the trained TF-IDF vectorizer.
- `sms_classifier.py` – Contains the text preprocessing and prediction logic.

**Important:** Keep `model.pkl` and `vectorizer.pkl` in the main project directory alongside `sms_classifier.py`. The application needs these files to perform SMS analysis.

The `research/` directory contains the supporting machine learning notebook and dataset.

## 12. Database Information

PhishGuard uses SQLite as its default database.

The database is created locally when the following command is executed:

```
python manage.py migrate
```

The local database file is not included in the GitHub repository
