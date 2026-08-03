# Sentiment Analysis in Emergency Calls

A Django web application that analyzes the sentiment of emergency calls in real time to classify the urgency level of a caller's statement. The system helps emergency dispatch services prioritize and respond faster by detecting emotional cues through NLP.

## Features

- **User registration & login** with admin approval workflow
- **Dataset viewer** — browse the labeled emergency-call dataset with search
- **Model training** — trains and compares Random Forest, SVM, and ANN classifiers, saves the best model
- **Accuracy comparison** — bar chart comparing model performance (served from cached training results)
- **Urgency prediction** — enter a caller statement and get a predicted urgency level (low → life-threatening) with confidence score
- **Admin panel** — view registered users and activate their accounts

## Tech Stack

- Django 4.2 (Python 3.8)
- scikit-learn (Random Forest, SVM, TF-IDF)
- TensorFlow/Keras (ANN)
- imbalanced-learn (SMOTE)
- pandas, numpy, matplotlib, joblib
- SQLite database

## Project Structure

```
sentiment_analysis_in_emergency_calls/   # Django project (settings, urls, root views)
├── admins/                              # Admin app (login, user management)
├── users/                               # User app (auth, dataset, training, prediction)
├── templates/                           # HTML templates
├── media/                               # Dataset, trained models, vectorizer, encoder
├── manage.py
└── requirements.txt
```

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Linux/macOS
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

4. Run the server:

   ```bash
   python manage.py runserver
   ```

5. Open `http://127.0.0.1:8000/` in your browser.

## Usage

| Page | URL | Description |
| --- | --- | --- |
| Home | `/` | Landing page |
| Admin login | `/AdminLogin/` | Default credentials: `admin` / `admin` |
| User register | `/UserRegister/` | Create a user account |
| User login | `/UserLogin/` | Sign in (account must be activated by admin) |
| Dataset view | `/DatasetView/` | Browse the labeled dataset |
| Train | `/training/` | Train and evaluate models |
| Graph | `/graph/` | Model accuracy comparison chart |
| Prediction | `/prediction/` | Predict urgency of a caller statement |

## Notes

- A pre-trained model (`best_model.pkl`), TF-IDF vectorizer, and label encoder are included in `media/`, so prediction works out of the box.
- Re-run `/training/` to retrain and regenerate the model artifacts and the accuracy chart.
- The model performance chart (`/graph/`) reads the cached results from the last training run for fast page loads.
