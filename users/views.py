import os
import json
import joblib
import base64
from io import BytesIO
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from .forms import UserRegistrationForm
from .models import UserRegistrationModel

MODEL_PATH_BEST = os.path.join(settings.MEDIA_ROOT, 'best_model.pkl')
TFIDF_PATH = os.path.join(settings.MEDIA_ROOT, 'tfidf_vectorizer.pkl')
ENCODERS_PATH = os.path.join(settings.MEDIA_ROOT, 'encoder_urgency.pkl')
DATASET_PATH = os.path.join(settings.MEDIA_ROOT, 'caller_statements_long.csv')
METRICS_PATH = os.path.join(settings.MEDIA_ROOT, 'model_metrics.json')

URGENCY_MAPPING = {
    'low': 0, 'medium': 1, 'high': 2, 'alert': 3, 'severe': 4,
    'critical': 5, 'immediate': 6, 'emergency': 7, 'life-threatening': 8,
}


def load_data():
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder

    df = pd.read_csv(DATASET_PATH)
    df['Caller Statement'] = df['Caller Statement'].str.strip().str.lower()
    df['Urgency Level'] = df['Urgency Level'].str.strip().str.lower()
    df['Urgency Level'] = df['Urgency Level'].map(URGENCY_MAPPING).fillna(0).astype(int)
    return df, LabelEncoder().fit(df['Urgency Level'].unique())


# ---------------------------------------------------------------------------
# User Registration and Login
# ---------------------------------------------------------------------------
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        messages.error(request, 'Email or Mobile Already Existed')
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            if check.status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                return render(request, 'users/UserHomePage.html', {})
            messages.error(request, 'Your Account Not activated')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'Invalid Login id or password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})


# ---------------------------------------------------------------------------
# Dataset View
# ---------------------------------------------------------------------------
def DatasetView(request):
    import pandas as pd

    df = pd.read_csv(DATASET_PATH)
    return render(request, 'users/DatasetView.html', {'d': df.head(300)})


# ---------------------------------------------------------------------------
# Model Training and Evaluation
# ---------------------------------------------------------------------------
def train_model(request):
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                                 f1_score, roc_auc_score)
    from imblearn.over_sampling import SMOTE
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam

    df, le_urgency = load_data()
    tfidf = TfidfVectorizer(max_features=5000)
    X = tfidf.fit_transform(df['Caller Statement'])
    y = df['Urgency Level']
    X_resampled, y_resampled = SMOTE(random_state=42).fit_resample(X, y)

    X_train, X_test, y_train, y_test = train_test_split(
        X_resampled, y_resampled, test_size=0.2, stratify=y_resampled, random_state=42
    )

    rf_model = RandomForestClassifier(n_estimators=200, max_depth=20,
                                      min_samples_split=5, class_weight='balanced',
                                      random_state=42)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)

    svm_model = SVC(probability=True, kernel='rbf', C=1.5, gamma='scale',
                    class_weight='balanced', random_state=42)
    svm_model.fit(X_train, y_train)
    svm_preds = svm_model.predict(X_test)

    ann_model = Sequential([
        Dense(256, activation='relu', input_shape=(X_train.shape[1],)),
        BatchNormalization(),
        Dropout(0.6),
        Dense(128, activation='relu'),
        BatchNormalization(),
        Dropout(0.4),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(len(set(y_train)), activation='softmax'),
    ])
    ann_model.compile(optimizer=Adam(learning_rate=0.001),
                      loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    ann_model.fit(X_train.toarray(), y_train, epochs=50, batch_size=64,
                  validation_split=0.2, verbose=0)
    ann_preds = np.argmax(ann_model.predict(X_test.toarray(), verbose=0), axis=1)

    def evaluate(name, model, preds, proba):
        return {
            'Accuracy': round(accuracy_score(y_test, preds), 4),
            'Precision': round(precision_score(y_test, preds, average='weighted', zero_division=0), 4),
            'Recall': round(recall_score(y_test, preds, average='weighted', zero_division=0), 4),
            'F1_Score': round(f1_score(y_test, preds, average='weighted', zero_division=0), 4),
            'AUC_ROC': round(roc_auc_score(y_test, proba, multi_class='ovr', average='weighted'), 4)
            if proba is not None else None,
        }

    metrics = {
        'Random Forest': evaluate('rf', rf_model, rf_preds,
                                  rf_model.predict_proba(X_test)),
        'SVM': evaluate('svm', svm_model, svm_preds, svm_model.predict_proba(X_test)),
        'ANN': evaluate('ann', ann_model, ann_preds,
                        np.asarray(ann_model.predict(X_test.toarray(), verbose=0))),
    }

    best_name, best_acc = max(metrics.items(), key=lambda kv: kv[1]['Accuracy'])
    best_model = {'Random Forest': rf_model, 'SVM': svm_model, 'ANN': ann_model}[best_name]

    joblib.dump(best_model, MODEL_PATH_BEST)
    joblib.dump(tfidf, TFIDF_PATH)
    joblib.dump(le_urgency, ENCODERS_PATH)
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f)

    context = {'metrics': metrics, 'best_model': best_name}
    return render(request, 'users/train.html', context)


# ---------------------------------------------------------------------------
# Graph Section (reuses cached training results for speed)
# ---------------------------------------------------------------------------
def graph_section(request):
    if not os.path.exists(METRICS_PATH):
        return render(request, 'users/GraphSection.html',
                      {'error': 'Please run Model Training first to generate the accuracy chart.'})

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    with open(METRICS_PATH) as f:
        metrics = json.load(f)

    model_names = list(metrics.keys())
    accuracy_values = [metrics[n]['Accuracy'] for n in model_names]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(model_names, accuracy_values, color=['#2563eb', '#06b6d4', '#10b981'])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel('Accuracy')
    for bar, val in zip(bars, accuracy_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.2f}", ha='center')

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    chart_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close(fig)

    return render(request, 'users/GraphSection.html', {'combined_accuracy_chart': chart_url})


# ---------------------------------------------------------------------------
# Urgency Prediction
# ---------------------------------------------------------------------------
def predict_urgency(request):
    import numpy as np
    from tensorflow.keras.models import Sequential

    if request.method == 'POST':
        caller_statement = request.POST.get('callerStatement', '').strip()
        if not caller_statement:
            return render(request, 'users/ML.html', {'error': 'Please enter a valid caller statement'})

        try:
            if len(caller_statement) < 15:
                return render(request, 'users/ML.html',
                              {'error': 'Statement too short (min 15 characters)'})

            if not all(os.path.exists(p) for p in [MODEL_PATH_BEST, TFIDF_PATH, ENCODERS_PATH]):
                raise FileNotFoundError('Required model files are missing. Please run Model Training first.')

            best_model = joblib.load(MODEL_PATH_BEST)
            tfidf = joblib.load(TFIDF_PATH)
            le_urgency = joblib.load(ENCODERS_PATH)

            cleaned_statement = ' '.join(caller_statement.strip().lower().split())
            statement_tfidf = tfidf.transform([cleaned_statement])

            if isinstance(best_model, Sequential):
                pred_proba = best_model.predict(statement_tfidf.toarray(), verbose=0)
                predicted_urgency = np.argmax(pred_proba, axis=1)
                confidence = float(np.max(pred_proba))
            else:
                predicted_urgency = best_model.predict(statement_tfidf)
                confidence = float(np.max(best_model.predict_proba(statement_tfidf)))

            predicted_label = int(le_urgency.inverse_transform(predicted_urgency)[0])
            predicted_class = {v: k for k, v in URGENCY_MAPPING.items()}.get(
                predicted_label, str(predicted_label))

            return render(request, 'users/ML.html', {
                'predicted_urgency': predicted_class,
                'confidence': f"{confidence:.1%}" if confidence is not None else None,
            })

        except Exception as e:
            return render(request, 'users/ML.html', {'error': f'Error processing request: {str(e)}'})

    return render(request, 'users/ML.html')
