#Author: Carly Shearer
#Purpose: Uses real data and machine learning
#to analyze risk of investing in cryptocurrencies.

import pandas as pd
import numpy as np
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

#Get real cryptocurrency history data from CoinGecko
def get_btc_history():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"

    params = {
        "vs_currency": "usd",
        "days": "365",
        "interval": "daily",
    }

    response = requests.get(
        url,
        params=params,
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    return [
        [timestamp, price]
        for timestamp, price in data["prices"]
    ]

#Calculate historic cryptocurrency risk
def calculate_features(prices):
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["return_7d"] = df["price"].pct_change(7)
    df["return_30d"] = df["price"].pct_change(30)
    df["volatility_30d"] = (
        df["price"]
        .pct_change()
        .rolling(30)
        .std()
    )
    df["moving_average_30"] = (
        df["price"]
        .rolling(30)
        .mean()
    )
    df["price_vs_ma"] = (
        df["price"] /
        df["moving_average_30"]
    )
    rolling_high = (
        df["price"]
        .rolling(30)
        .max()
    )
    df["drawdown"] = (
        df["price"] / rolling_high - 1
    )
    df["future_return"] = ( #future return in 7 days
        df["price"].shift(-7) /
        df["price"] - 1
    )
    df["downside"] = (
        df["future_return"] <= -0.10 #1 = substantial decline, 0 = not substantial decline
    ).astype(int)

    df = df.dropna()

    return df

#Train ML model to predict risk of cryptocurrency
def train_crypto_model(prices):
    df = calculate_features(prices)

    features = [
        "return_7d",
        "return_30d",
        "volatility_30d",
        "price_vs_ma",
        "drawdown",
    ]

    X = df[features]
    y = df["downside"]

    if len(df) < 100:
        raise ValueError(
            "Not enough historical data to train model."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        shuffle=False,
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    latest_features = X.iloc[[-1]]

    probability = model.predict_proba(
        latest_features
    )[0][1]

    if probability >= 0.60:
        risk = "HIGH"
    elif probability >= 0.35:
        risk = "MODERATE"
    else:
        risk = "LOW"

    return {
        "risk": risk,
        "downside_probability": round(
            float(probability),
            3,
        ),
        "model_accuracy": round(
            float(accuracy),
            3,
        ),
        "training_samples": len(X_train),
        "features": {
            key: round(
                float(value),
                4,
            )
            for key, value
            in latest_features.iloc[0].items()
        },
    }