#Author: Carly Shearer
#Purpose: Uses real data and machine learning
#to analyze liklihood of increase/decrease in
#interest rates for certain investment accounts.

import requests
import pandas as pd
from io import StringIO
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

#Get real historic interest rate data from Federal Reserve Bank
FRED_URL = (
    "https://fred.stlouisfed.org/graph/"
    "fredgraph.csv?id=DFF"
)

def get_rate_history():
    response = requests.get(
        FRED_URL,
        timeout=10,
    )

    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text))

    df.columns = ["date", "rate"]
    df["date"] = pd.to_datetime(df["date"])
    df["rate"] = pd.to_numeric(
        df["rate"],
        errors="coerce",
    )
    df = df.dropna()
    df = (
        df.set_index("date")
        .resample("7D")
        .mean()
        .dropna()
        .reset_index()
    )

    return df

#Calculate historic interest rate
def build_rate_features(df):
    df = df.copy()
    df["change_4w"] = (
        df["rate"] -
        df["rate"].shift(4)
    )
    df["change_12w"] = (
        df["rate"] -
        df["rate"].shift(12)
    )
    df["moving_average_12w"] = (
        df["rate"]
        .rolling(12)
        .mean()
    )
    df["distance_from_average"] = (
        df["rate"] -
        df["moving_average_12w"]
    )
    df["future_rate"] = (
        df["rate"].shift(-4) #rate 4 weeks into future
    )
    df["rate_increase"] = (
        df["future_rate"] > df["rate"]
    ).astype(int)
    df = df.dropna()

    return df

#Train ML model to predict interest rates
def train_rate_model():
    df = get_rate_history()

    df = build_rate_features(df)

    features = [
        "rate",
        "change_4w",
        "change_12w",
        "distance_from_average",
    ]

    X = df[features]
    y = df["rate_increase"]

    if len(df) < 100:
        raise ValueError(
            "Not enough historical rate data."
        )

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.2,
            shuffle=False,
        )
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    latest = X.iloc[[-1]]

    probability = model.predict_proba(
        latest
    )[0][1]

    if probability >= 0.60:
        direction = "LIKELY_INCREASE"
    elif probability <= 0.40:
        direction = "LIKELY_DECREASE"
    else:
        direction = "UNCERTAIN"

    return {
        "direction": direction,
        "increase_probability": round(
            float(probability),
            3,
        ),
        "model_accuracy": round(
            float(accuracy),
            3,
        ),
        "training_samples": len(X_train),
        "current_rate": round(
            float(latest["rate"].iloc[0]),
            2,
        ),
    }