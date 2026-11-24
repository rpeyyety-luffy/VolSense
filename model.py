"""
model.py - Person 2 (ML)

Job: train a model that predicts if VIX will rise (1) or fall (0) in 5 trading days.

CONTRACT: predict_today() returns a dictionary with keys
    date, vix, nifty, direction ("rise"/"fall"), confidence (0-1),
    test_accuracy (0-1), baseline_accuracy (0-1)

Right now predict_today() is a FAKE VERSION so the app can run today.
"""

from features import get_data, FEATURE_COLUMNS

TEST_START = "2023-01-01"   # train on data before this date, test on data after
MODEL_PATH = "model.pkl"


def split_by_time(df):
    """Split into train (before TEST_START) and test (from TEST_START). Never random!"""
    train = df[df.index < TEST_START]
    test = df[df.index >= TEST_START]
    return train, test


def train():
    """Train the model and save it to MODEL_PATH."""
    # TODO(Person 2), step by step:
    #   1. df = get_data(); train, test = split_by_time(df)
    #   2. Baseline: accuracy of always guessing the most common target in test
    #   3. Train LogisticRegression on train[FEATURE_COLUMNS] -> train["target"]
    #   4. Train RandomForestClassifier, compare test accuracy with step 2 and 3
    #   5. Save the best one with joblib.dump(model, MODEL_PATH)
    raise NotImplementedError("Person 2: build train() step by step")


def predict_today():
    """FAKE VERSION - returns made-up numbers in the contract shape."""
    # TODO(Person 2): load model.pkl with joblib, take the last row of get_data(),
    # use model.predict_proba() for confidence, and fill in the real accuracies.
    df = get_data()
    last = df.iloc[-1]
    return {
        "date": str(df.index[-1].date()),
        "vix": round(float(last["VIX"]), 2),
        "nifty": round(float(last["Nifty"]), 2),
        "direction": "rise",
        "confidence": 0.64,
        "test_accuracy": 0.61,
        "baseline_accuracy": 0.54,
    }


if __name__ == "__main__":
    print(predict_today())
