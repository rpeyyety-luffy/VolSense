"""
model.py - Stage 3 of VolSense.

Question: will India VIX be HIGHER 5 trading days from now? (1 = yes, 0 = no)
Trains on 2015-2022, tests on 2023-2026, compares 3 approaches, predicts today.

Run it with:  python3 model.py
"""

import os
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

from features import FEATURE_COLS, DAYS_AHEAD  # same 7 clues + same "5 days" as Stage 2

FEATURES_CSV = os.path.join("data", "features.csv")
TRAIN_END = "2022-12-31"   # train on 2015-2022 (the past)
TEST_START = "2023-01-01"  # test on 2023-2026 (the "future" the model never saw)


def load_features():
    """Return (labelled rows for train/test, the latest row for predict_today)."""
    data = pd.read_csv(FEATURES_CSV, index_col="Date", parse_dates=True)
    labelled = data.dropna(subset=["target"])  # only days where we KNOW the answer
    latest = data.tail(1)                       # today's row: features known, answer not
    return labelled, latest


def time_split(labelled):
    """Split by date: past = train, future = test. Never shuffle."""
    train = labelled[labelled.index <= TRAIN_END]
    test = labelled[labelled.index >= TEST_START]

    # WHY: the last 5 training days' targets use VIX from early Jan 2023 (test time).
    # Dropping them is a small "gap" so no test-period info leaks into training.
    train = train.iloc[:-DAYS_AHEAD]  # iloc[:-5] = every row except the last 5

    # X = the questions (features), y = the answers (target as whole numbers 0/1)
    X_train, y_train = train[FEATURE_COLS], train["target"].astype(int)
    X_test, y_test = test[FEATURE_COLS], test["target"].astype(int)
    return X_train, y_train, X_test, y_test


def baseline_accuracy(y_train, y_test):
    """Always guess the most common answer FROM TRAINING. How often is that right on test?"""
    most_common = y_train.mode()[0]  # mode() = the value that appears most often
    # (y_test == most_common) gives True/False per day; mean() = share of True
    return (y_test == most_common).mean()


def train_logistic(X_train, y_train):
    """Scale features, then Logistic Regression (the 'scorecard with weights')."""
    # WHY a pipeline: the scaler learns ONLY from training data inside fit(),
    # and is applied the same way automatically to test data and today's row.
    model = make_pipeline(StandardScaler(), LogisticRegression())
    model.fit(X_train, y_train)  # fit = training: find the best weights
    return model


def train_random_forest(X_train, y_train):
    """300 small decision trees that vote."""
    model = RandomForestClassifier(
        n_estimators=300,      # number of trees voting
        max_depth=5,           # max 5 questions per tree - stops memorising
        min_samples_leaf=20,   # each final answer must rest on 20+ days, not lucky 1-2
        random_state=42,       # same randomness every run -> same result in the demo
    )
    model.fit(X_train, y_train)
    return model


def evaluate(name, model, X_test, y_test):
    """Score a trained model on the test years (days it has never seen)."""
    predictions = model.predict(X_test)  # 0 or 1 for each test day
    # predict_proba gives 2 columns: [chance of 0, chance of 1]. [:, 1] = all rows, column 1.
    prob_up = model.predict_proba(X_test)[:, 1]
    return {
        "model": name,
        "accuracy": accuracy_score(y_test, predictions),  # share guessed right
        "roc_auc": roc_auc_score(y_test, prob_up),       # 0.5 = random, 1.0 = perfect
    }


def compare_models(show=True):
    """Train + test all approaches, print a table, return the name of the best model."""
    labelled, latest = load_features()
    X_train, y_train, X_test, y_test = time_split(labelled)

    baseline = {"model": "Baseline (most common)",
                "accuracy": baseline_accuracy(y_train, y_test),
                "roc_auc": 0.5}  # always the same guess = no ranking skill = 0.5
    logistic = evaluate("Logistic Regression", train_logistic(X_train, y_train), X_test, y_test)
    forest = evaluate("Random Forest", train_random_forest(X_train, y_train), X_test, y_test)

    # WHY AUC to pick: accuracy can look OK just by guessing the common answer.
    if forest["roc_auc"] > logistic["roc_auc"]:
        best_name = "Random Forest"
    else:
        best_name = "Logistic Regression"

    if show:
        print(f"Train: {len(X_train)} rows ({X_train.index[0].date()} to {X_train.index[-1].date()})")
        print(f"Test:  {len(X_test)} rows ({X_test.index[0].date()} to {X_test.index[-1].date()})")
        print(f"VIX went UP in train: {y_train.mean():.1%}   in test: {y_test.mean():.1%}\n")
        table = pd.DataFrame([baseline, logistic, forest])  # list of dicts -> table
        print(table.round(3).to_string(index=False))
        print(f"\nBest model (by ROC-AUC): {best_name}")
    return best_name


def predict_today(model_name=None):
    """Retrain the chosen model on ALL labelled days, then predict the latest day."""
    if model_name is None:
        model_name = compare_models(show=False)  # pick the best quietly

    labelled, latest = load_features()
    X_all, y_all = labelled[FEATURE_COLS], labelled["target"].astype(int)

    # WHY retrain on everything: the test split was only for an honest score.
    # For the real prediction, learn from all history incl. the most recent weeks.
    if model_name == "Random Forest":
        model = train_random_forest(X_all, y_all)
    else:
        model = train_logistic(X_all, y_all)

    prob_up = model.predict_proba(latest[FEATURE_COLS])[0, 1]  # row 0, column 1
    return {
        "date": str(latest.index[0].date()),
        "prediction": "UP" if prob_up >= 0.5 else "DOWN",
        "probability_up": round(float(prob_up), 3),  # float(): plain number, JSON-friendly
        "model": model_name,
    }


if __name__ == "__main__":
    best = compare_models()
    print("\nToday's prediction:", predict_today(best))
