#Author: Carly Shearer
#Purpose: Uses FastAPI to connect with database
#and front-end. 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rates import train_rate_model
from dotenv import load_dotenv
from google import genai
from ml import get_btc_history, train_crypto_model
from models import (
    Holding,
    ETFHolding,
    Portfolio,
    SessionLocal,
)
import os

#Load APIs and dependencies

load_dotenv()

gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

class GoalRequest(BaseModel):
    goal: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HoldingCreate(BaseModel):
    portfolio_id: int
    ticker: str
    asset_type: str
    value: float
    apy: float | None = None
    maturity_date: str | None = None

@app.get("/")
def home():
    return {"message": "Portfolio Analyzer API working"}

@app.post("/holdings")
def create_holding(holding: HoldingCreate):
    db = SessionLocal()

    new_holding = Holding(
        portfolio_id=holding.portfolio_id,
        ticker=holding.ticker.upper(),
        asset_type=holding.asset_type,
        value=holding.value,
        apy=holding.apy,
        maturity_date=holding.maturity_date,
    )

    db.add(new_holding)
    db.commit()
    db.refresh(new_holding)
    db.close()

    return new_holding

@app.get("/holdings")
def get_holdings():
    db = SessionLocal()

    holdings = db.query(Holding).all()

    db.close()

    return holdings

@app.get("/portfolio/summary")
def portfolio_summary():
    db = SessionLocal()

    holdings = db.query(Holding).filter(
        Holding.portfolio_id == 1
    ).all()

    db.close()

    total_value = sum(
        holding.value for holding in holdings
    )

    if total_value == 0:
        return {
            "total_value": 0,
            "asset_allocation": {},
            "holdings": [],
            "largest_holding": None,
        }

    asset_allocation = {}

    for holding in holdings:
        asset_type = holding.asset_type

        if asset_type not in asset_allocation:
            asset_allocation[asset_type] = 0

        asset_allocation[asset_type] += holding.value

    for asset_type in asset_allocation:
        asset_allocation[asset_type] = round(
            asset_allocation[asset_type] / total_value * 100,
            2,
        )

    holding_summary = []

    for holding in holdings:
        percentage = (
            holding.value / total_value * 100
        )

        holding_summary.append(
            {
                "id": holding.id,
                "ticker": holding.ticker,
                "asset_type": holding.asset_type,
                "value": holding.value,
                "percentage": round(percentage, 2),
                "apy": holding.apy,
                "maturity_date": holding.maturity_date,
            }
        )

    largest_holding = max(
        holdings,
        key=lambda holding: holding.value
    )

    return {
        "total_value": round(total_value, 2),
        "asset_allocation": asset_allocation,
        "holdings": holding_summary,
        "largest_holding": largest_holding.ticker,
    }

@app.get("/portfolio/overlap")
def portfolio_overlap():
    db = SessionLocal()

    holdings = db.query(Holding).filter(
        Holding.portfolio_id == 1,
        Holding.asset_type == "ETF",
    ).all()

    etf_tickers = [holding.ticker for holding in holdings]

    etf_holdings = db.query(ETFHolding).filter(
        ETFHolding.etf_ticker.in_(etf_tickers)
    ).all()

    db.close()

    overlap = {}

    for holding in etf_holdings:
        if holding.holding_ticker not in overlap:
            overlap[holding.holding_ticker] = {}

        overlap[holding.holding_ticker][holding.etf_ticker] = holding.weight

    result = []

    for ticker, etfs in overlap.items():
        if len(etfs) > 1:
            result.append(
                {
                    "ticker": ticker,
                    "etfs": etfs,
                }
            )

    return result

@app.get("/portfolio/exposure")
def portfolio_exposure():
    db = SessionLocal()

    holdings = db.query(Holding).filter(
        Holding.portfolio_id == 1,
        Holding.asset_type == "ETF",
    ).all()

    etf_tickers = [holding.ticker for holding in holdings]

    etf_holdings = db.query(ETFHolding).filter(
        ETFHolding.etf_ticker.in_(etf_tickers)
    ).all()

    total_portfolio_value = sum(
        holding.value
        for holding in db.query(Holding).filter(
            Holding.portfolio_id == 1
        ).all()
    )

    db.close()

    exposure = {}

    for etf_holding in etf_holdings:
        matching_etf = next(
            (
                holding
                for holding in holdings
                if holding.ticker == etf_holding.etf_ticker
            ),
            None,
        )

        if matching_etf is None:
            continue

        dollar_exposure = (
            matching_etf.value * etf_holding.weight / 100
        )

        if etf_holding.holding_ticker not in exposure:
            exposure[etf_holding.holding_ticker] = 0

        exposure[etf_holding.holding_ticker] += dollar_exposure

    result = []

    for ticker, dollar_value in exposure.items():
        percentage = (
            dollar_value / total_portfolio_value * 100
            if total_portfolio_value > 0
            else 0
        )

        result.append(
            {
                "ticker": ticker,
                "estimated_value": round(dollar_value, 2),
                "portfolio_percentage": round(percentage, 2),
            }
        )

    result.sort(
        key=lambda item: item["portfolio_percentage"],
        reverse=True,
    )

    return result

@app.get("/portfolio/crypto-risk")
def crypto_risk():
    db = SessionLocal()

    holdings = db.query(Holding).filter(
        Holding.portfolio_id == 1
    ).all()

    db.close()

    total_value = sum(
        holding.value for holding in holdings
    )

    crypto_holdings = [
        holding
        for holding in holdings
        if holding.asset_type.upper() == "CRYPTO"
    ]

    crypto_value = sum(
        holding.value
        for holding in crypto_holdings
    )

    if total_value == 0:
        return {
            "crypto_value": 0,
            "crypto_percentage": 0,
            "crypto_holdings": [],
            "scenarios": [],
        }

    crypto_percentage = (
        crypto_value / total_value * 100
    )

    scenarios = []

    for decline in [25, 50, 75]:
        portfolio_loss = (
            crypto_value * decline / 100
        )

        portfolio_percentage_loss = (
            portfolio_loss / total_value * 100
        )

        scenarios.append(
            {
                "crypto_decline": decline,
                "portfolio_loss_dollars": round(
                    portfolio_loss,
                    2,
                ),
                "portfolio_loss_percentage": round(
                    portfolio_percentage_loss,
                    2,
                ),
            }
        )

    return {
        "crypto_value": round(crypto_value, 2),
        "crypto_percentage": round(
            crypto_percentage,
            2,
        ),
        "crypto_holdings": [
            {
                "ticker": holding.ticker,
                "value": holding.value,
            }
            for holding in crypto_holdings
        ],
        "scenarios": scenarios,
    }

@app.post("/portfolio/analyze")
def analyze_portfolio(request: GoalRequest):
    db = SessionLocal()

    holdings = db.query(Holding).filter(
        Holding.portfolio_id == 1
    ).all()

    etf_holdings = db.query(ETFHolding).all()

    db.close()

    total_value = sum(
        holding.value for holding in holdings
    )

    crypto_value = sum(
        holding.value
        for holding in holdings
        if holding.asset_type.lower() == "crypto"
    )

    crypto_percentage = (
        crypto_value / total_value * 100
        if total_value > 0
        else 0
    )

    largest_holding = (
        max(holdings, key=lambda holding: holding.value)
        if holdings
        else None
    )

    #Calculate ETF overlap
    etf_tickers = [
        holding.ticker
        for holding in holdings
        if holding.asset_type.lower() == "etf"
    ]

    overlap = {}

    for item in etf_holdings:
        if item.etf_ticker in etf_tickers:
            if item.holding_ticker not in overlap:
                overlap[item.holding_ticker] = []

            overlap[item.holding_ticker].append(
                item.etf_ticker
            )

    overlapping_stocks = {
        ticker: etfs
        for ticker, etfs in overlap.items()
        if len(etfs) > 1
    }

    portfolio_context = {
        "goal": request.goal,
        "portfolio_value": round(total_value, 2),
        "crypto_value": round(crypto_value, 2),
        "crypto_percentage": round(crypto_percentage, 2),
        "largest_holding": (
            largest_holding.ticker
            if largest_holding
            else None
        ),
        "holdings": [
            {
                "ticker": holding.ticker,
                "asset_type": holding.asset_type,
                "value": holding.value,
            }
            for holding in holdings
        ],
        "etf_overlap": overlapping_stocks,
    }

    prompt = f"""
    You are a financial education assistant helping a beginner
    understand their investment portfolio.

    The user has provided a financial goal and their portfolio
    data.

    PORTFOLIO DATA:
    {portfolio_context}

    USER GOAL:
    {request.goal}

    Analyze the portfolio in plain, beginner-friendly language.

    Return exactly these sections:

    SUMMARY
    Give a short explanation of what the portfolio currently
    looks like.

    WHAT YOU MAY NOT REALIZE
    Explain important concentration, ETF overlap, hidden
    exposure, or crypto exposure.

    AREAS TO EXPLORE
    Give 3 different educational portfolio strategies or areas
    the user could research.

    For each area include:
    - Name
    - What it would change
    - Potential benefit
    - Potential tradeoff

    GOAL ALIGNMENT
    Explain which characteristics of the current portfolio may
    or may not be relevant to the user's stated goal.

    RULES:
    - Do not tell the user what they should buy or sell.
    - Do not give personalized buy/sell instructions.
    - Do not guarantee returns.
    - Do not invent portfolio facts.
    - Use the calculated portfolio data provided above.
    - Clearly distinguish portfolio facts from general education.
    - Keep the entire response under 300 words.
    """

    response = gemini_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    return {
        "goal": request.goal,
        "portfolio": portfolio_context,
        "ai_analysis": response.text,
    }

@app.get("/portfolio/analysis")
def portfolio_analysis():
    db = SessionLocal()

    holdings = db.query(Holding).filter(
        Holding.portfolio_id == 1
    ).all()

    db.close()

    total_value = sum(
        holding.value for holding in holdings
    )

    if total_value == 0:
        return {
            "total_value": 0,
            "asset_allocation": {},
            "risk_indicators": {},
            "interest_bearing_assets": [],
        }

    allocation = {}

    for holding in holdings:
        asset_type = holding.asset_type.upper()

        allocation[asset_type] = (
            allocation.get(asset_type, 0)
            + holding.value
        )

    allocation_percent = {
        asset_type: round(
            value / total_value * 100,
            2,
        )
        for asset_type, value in allocation.items()
    }

    crypto_value = sum(
        holding.value
        for holding in holdings
        if holding.asset_type.upper() == "CRYPTO"
    )

    crypto_percentage = (
        crypto_value / total_value * 100
    )

    interest_assets = [
        {
            "ticker": holding.ticker,
            "asset_type": holding.asset_type,
            "value": holding.value,
            "apy": holding.apy,
            "maturity_date": holding.maturity_date,
        }
        for holding in holdings
        if holding.apy is not None
    ]

    largest_holding = max(
        holdings,
        key=lambda holding: holding.value,
    ) if holdings else None

    largest_percentage = (
        largest_holding.value / total_value * 100
        if largest_holding
        else 0
    )

    risk_indicators = {
        "crypto_percentage": round(
            crypto_percentage,
            2,
        ),
        "largest_holding_percentage": round(
            largest_percentage,
            2,
        ),
        "number_of_holdings": len(holdings),
    }

    crypto_ml = None

    if crypto_value > 0:
        try:
            btc_history = get_btc_history()
            crypto_ml = train_crypto_model(
                btc_history
            )
        except Exception as error:
            crypto_ml = {
                "error": str(error)
            }

    rate_ml = None

    if interest_assets:
        try:
            rate_ml = train_rate_model()
        except Exception as error:
            rate_ml = {
                "error": str(error)
            }

    return {
        "total_value": round(total_value, 2),
        "asset_allocation": allocation_percent,
        "risk_indicators": risk_indicators,
        "interest_bearing_assets": interest_assets,
        "crypto_ml": crypto_ml,
        "rate_ml": rate_ml,
        "holdings": [
            {
                "ticker": holding.ticker,
                "asset_type": holding.asset_type,
                "value": holding.value,
                "percentage": round(
                    holding.value / total_value * 100,
                    2,
                ),
            }
            for holding in holdings
        ],
    }

class StarterRequest(BaseModel):
    goal: str
    time_horizon_years: int
    risk_tolerance: str

#Give Gemini API data about user profile
#for it to translate to understandable language.

#For user with investment portfolio
@app.post("/portfolio/starter")
def portfolio_starter(request: StarterRequest):
    prompt = f"""
    You are a financial education assistant helping someone
    who is completely new to investing.

    Their goal is:
    {request.goal}

    Their time horizon is:
    {request.time_horizon_years} years.

    Their risk tolerance is:
    {request.risk_tolerance}

    Explain the major investment categories they could
    research, including:

    - Savings accounts
    - CDs
    - Bonds
    - ETFs
    - Stocks
    - Cryptocurrency

    For each relevant category explain:
    - What it is
    - Why someone might research it
    - Main risks
    - How accessible or liquid it generally is

    Do not tell the user exactly what to buy or sell,
    guarantee returns, or make predictions.
    Keep this educational and beginner-friendly.

    Keep the response under 300 words.
    """

    response = gemini_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    return {
        "goal": request.goal,
        "time_horizon_years": request.time_horizon_years,
        "risk_tolerance": request.risk_tolerance,
        "recommendations": response.text,
    }

#For user without investment portfolio
@app.post("/starter/analyze")
def starter_analyze(request: StarterRequest):
    prompt = f"""
    You are a financial education assistant.

    A person is new to investing and currently has no
    investments.

    Their goal:
    {request.goal}

    Their time horizon:
    {request.years} years

    Their risk comfort:
    {request.risk}

    Explain the major investment categories they could
    research based on these characteristics.

    Discuss categories such as:
    - savings accounts
    - CDs
    - bonds
    - ETFs
    - stocks
    - cryptocurrency

    For each relevant category explain:
    - What it is
    - Why someone might research it
    - Main risk
    - How accessible/liquid it generally is

    Do not tell the person exactly what to buy,
    guarantee returns, or make predictions.
    This is educational information, not personalized
    financial advice.

    Use beginner-friendly language.

    Keep the response under 300 words.
    """

    response = gemini_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    return {
        "goal": request.goal,
        "years": request.years,
        "risk": request.risk,
        "analysis": response.text,
    }

#Reset function for demo purposes. Clears database
#of user portfolios and returns to start screen.
@app.post("/portfolio/reset")
def reset_portfolio():
    db = SessionLocal()

    try:
        db.query(Holding).filter(
            Holding.portfolio_id == 1
        ).delete(synchronize_session=False)

        db.commit()

        return {
            "message": "Portfolio reset successfully",
            "portfolio_id": 1,
        }

    except Exception as error:
        db.rollback()
        raise error

    finally:
        db.close()