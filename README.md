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

Use a Python version compatible with the packages listed in `requirements.txt`.

## 7. Installation and Setup

Follow these steps to download and run PhishGuard on your computer.

### Step 1: Clone the GitHub repository

```bash
git clone https://github.com/AniketYadav98650/PhishGuard.git
```

### Step 2: Navigate to the project directory

```bash
cd PhishGuard
```

### Step 3: Create a virtual environment

For Windows PowerShell:

```powershell
python -m venv .venv
```

### Step 4: Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, you can use Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

### Step 5: Install the required dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs the Python packages required by the application.

### Step 6: Set up the database

Run the following command:

```powershell
python manage.py migrate
```

Django will create the local SQLite database and apply the required database migrations.

### Step 7: Start the application

```powershell
python manage.py runserver
```

Open your browser and visit:

http://127.0.0.1:8000/

The PhishGuard homepage should now appear.

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

To execute the website test suite, run:

```powershell
python manage.py test website
```

The current project test suite contains **22 automated tests**, covering unit-level and component-level functionality.

### Additional Django checks

To check the application for configuration issues:

```powershell
python manage.py check
```

To check whether database model changes require new migrations:

```powershell
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

```powershell
python manage.py migrate
```

The local database file is not included in the GitHub repository