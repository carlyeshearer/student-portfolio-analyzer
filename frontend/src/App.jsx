//Author: Carly Shearer
//Purpose: Front-end UI developed using React

import { useEffect, useState } from "react";
import "./App.css";
import ReactMarkdown from 'react-markdown';

const API = "http://127.0.0.1:8000";

function App() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  //const [showStarter, setShowStarter] = useState(false);
  const [showAddInvestment, setShowAddInvestment] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [starterLoading, setStarterLoading] = useState(false);
  const [starterAnalysis, setStarterAnalysis] = useState("");
  const [newInvestment, setNewInvestment] = useState({
    ticker: "",
    asset_type: "ETF",
    value: "",
    apy: "",
    maturity_date: "",
  });
  const [starter, setStarter] = useState({
    goal: "",
    time_horizon_years: "",
    risk_tolerance: "Moderate",
  });
  const [addingInvestment, setAddingInvestment] = useState(false);

  //Load portfolio

  const loadAnalysis = async () => {
    setLoading(true);

    try {
      const response = await fetch(`${API}/portfolio/analysis`);

      if (!response.ok) {
        throw new Error("Failed to load portfolio");
      }

      const data = await response.json();
      setAnalysis(data);
    } 
    catch (error) {
      console.error(error);
    } 
    finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalysis();
  }, []);

  //Portfolio analysis using Gemini

  const explainPortfolio = async () => {
    setAiLoading(true);

    try {
      const response = await fetch(`${API}/portfolio/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          goal: "Understand my portfolio and improve my financial knowledge",
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to analyze portfolio"
        );
      }

      setAiAnalysis(data.ai_analysis);
    } 
    catch (error) {
      console.error(error);
      setAiAnalysis(
        "Unable to analyze the portfolio right now. Make sure the backend is running. " +
        "Gemini API may be unavailable due to high demand."
      );
    } 
    finally {
      setAiLoading(false);
    }
  };

  //Start screen

  const getStarterAdvice = async (event) => {
    event.preventDefault();
    setStarterLoading(true);
    setStarterAnalysis("");

    try {
      const response = await fetch(`${API}/portfolio/starter`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          goal: starter.goal,
          time_horizon_years: Number(
            starter.time_horizon_years
          ),
          risk_tolerance: starter.risk_tolerance,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to create starter guide"
        );
      }

      setStarterAnalysis(
        data.recommendations || data.analysis || ""
      );
    } 
    catch (error) {
      console.error(error);
      setStarterAnalysis(
        "We couldn't create your guide right now. Please make sure the backend is running. " +
        "Gemini API may be unavailable due to high demand."
      );
    } 
    finally {
      setStarterLoading(false);
    }
  };

  //Add an investment

  const addInvestment = async (event) => {
    event.preventDefault();
    setAddingInvestment(true);

    try {
      const response = await fetch(`${API}/holdings`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          portfolio_id: 1,
          ticker: newInvestment.ticker,
          asset_type: newInvestment.asset_type,
          value: Number(newInvestment.value),
          apy: newInvestment.apy
            ? Number(newInvestment.apy)
            : null,
          maturity_date:
            newInvestment.maturity_date || null,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(
          data.detail || "Failed to add investment"
        );
      }

      setNewInvestment({
        ticker: "",
        asset_type: "ETF",
        value: "",
        apy: "",
        maturity_date: "",
      });

      setShowAddInvestment(false);
      await loadAnalysis();

    } 
    catch (error) {
      console.error(error);
      alert("Could not add investment.");
    } 
    finally {
      setAddingInvestment(false);
    }
  };

  //Reset demo

  const resetDemo = async () => {
    try {
      const response = await fetch(`${API}/portfolio/reset`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Failed to reset demo");
      }

      //setShowStarter(false);
      setShowAddInvestment(false);
      setAiAnalysis("");
      setStarterAnalysis("");

      setNewInvestment({
        ticker: "",
        asset_type: "ETF",
        value: "",
      });

      setStarter({
        goal: "",
        time_horizon_years: "",
        risk_tolerance: "Moderate",
      });

      await loadAnalysis();
    } 
    catch (error) {
      console.error(error);
      alert("Could not reset the demo.");
    }
  };

  //Loading screen

  if (loading) {
    return (
      <div className="loading-screen">
      <div className="loading-card">
          <h1>Student Portfolio Analyzer</h1>
          <p>Understanding your investments...</p>
          <div className="loader"></div>
        </div>
      </div>
    );
  }

  //Financial data

  const totalValue = analysis?.total_value || 0;
  const allocation = analysis?.asset_allocation || {};
  const holdings = analysis?.holdings || [];
  const crypto = analysis?.crypto_ml;
  const etfOverlap = analysis?.etf_overlap_percentage ?? 0;
  const rates = analysis?.rate_ml;
  const hasInvestments = holdings.length > 0;

  //Empty portfolio (start screen)

  if (!hasInvestments) {
    return (
      <div className="app">
      <header className="navbar">
        <div className="brand">
          <div>
            <h1>Student Portfolio Analyzer</h1>
          </div>
        </div>
      </header>
        <main className="container">
          <section className="starter">
            <div className="starter-intro">
              <p className="eyebrow">
                WELCOME TO YOUR PORTFOLIO ANALYZER
              </p>
              <h2>
                You don't need investments to get started.
              </h2>
              <p>
                Tell us what you're working
                toward and we'll help you
                understand different
                investment categories that may
                be right for you.
              </p>
              <p>
                Once you add your first
                investment, we'll
                turn your portfolio into
                a dashboard.
              </p>
            </div>
            <form className="starter-form" onSubmit={getStarterAdvice}>
              <div className="field">
                <label>
                  What's your goal?
                </label>
                <input
                  value={starter.goal}
                  onChange={(event) =>
                    setStarter({
                      ...starter,
                      goal: event.target.value,
                    })
                  }
                  placeholder="Save for a car..."
                  required
                />
              </div>
              <div className="field">
                <label>
                  What's your timeframe?
                </label>
                <select
                  value={starter.time_horizon_years}
                  onChange={(event) =>
                    setStarter({
                      ...starter,
                      time_horizon_years:
                        event.target.value,
                    })
                  }
                  required
                >
                  <option value="">
                    Select a timeframe
                  </option>
                  <option value="1">
                    Less than 1 year
                  </option>
                  <option value="3">
                    1–3 years
                  </option>
                  <option value="5">
                    3–5 years
                  </option>
                  <option value="10">
                    5–10 years
                  </option>
                  <option value="20">
                    10+ years
                  </option>
                </select>
              </div>
              <div className="field">
                <label>
                  How comfortable are you with
                  investment risk?
                </label>
                <select
                  value={starter.risk_tolerance}
                  onChange={(event) =>
                    setStarter({
                      ...starter,
                      risk_tolerance:
                        event.target.value,
                    })
                  }
                >
                  <option value="Conservative">
                    I want stability
                  </option>
                  <option value="Moderate">
                    Some ups and downs are okay
                  </option>
                  <option value="Aggressive">
                    I'm comfortable taking risks
                  </option>
                </select>
              </div>
              <button
                className="primary-button"
                type="submit"
                disabled={starterLoading}
              >
                {starterLoading
                  ? "Building Your Guide..."
                  : "Explore My Options"}
              </button>
            </form>
            {starterAnalysis && (
              <div className="starter-result">
                <p className="eyebrow">
                  YOUR INVESTING GUIDE
                </p>
                <div className="ai-text" style={{ padding: "15px" }}>
                  {starterAnalysis}
                </div>
                <button
                  className="ai-button"
                  type="button"
                  onClick={() =>
                    setShowAddInvestment(true)
                  }
                >
                  Add My First Investment
                </button>
              </div>
            )}
          </section>
        </main>

        {showAddInvestment && (
          <AddInvestmentModal
            newInvestment={newInvestment}
            setNewInvestment={setNewInvestment}
            addInvestment={addInvestment}
            addingInvestment={addingInvestment}
            onClose={() =>
              setShowAddInvestment(false)
            }
          />
        )}
      </div>
    );
  }

  //Main dashboard

  return (
  <div className="app">
  <header className="navbar">
  <div className="brand">
  <h1>Student Portfolio Analyzer</h1>
    </div>
      <div className="nav-actions">
        <button
          className="add-investment-button"
          onClick={() =>
            setShowAddInvestment(true)
          }
        >
          Add Investment
        </button>
        <button
          className="reset-button"
          onClick={resetDemo}
        >
          Reset Demo
        </button>
      </div>
    </header>
    <main className="container">
      <section className="hero">
        <div>
          <h2 style={{ color: "white" }}>
            Your Portfolio
          </h2>
        </div>
        <div className="value-card">
          <span>
            Total Portfolio Value
          </span>
          <strong>
            $
            {totalValue.toLocaleString(
              undefined,
              {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }
            )}
          </strong>
        </div>
      </section>
      <section className="dashboard-grid">
        <div className="panel allocation-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                BREAKDOWN
              </p>
              <h3>
                What you own
              </h3>
            </div>
          </div>
          <div className="allocation">
            {Object.entries(
              allocation
            ).map(
              ([type, percentage]) => (
                <div
                  className="allocation-row"
                  key={type}
                >
                  <div className="allocation-label">
                    <span
                      className={`dot ${type.toLowerCase()}`}
                    ></span>
                    <span>
                      {type}
                    </span>
                  </div>
                  <strong>
                    {percentage}%
                  </strong>
                  <div className="bar">
                    <div
                      className={`bar-fill ${type.toLowerCase()}`}
                      style={{
                        width: `${percentage}%`,
                      }}
                    ></div>
                  </div>
                </div>
              )
            )}
          </div>
        </div>
        <div className="panel insights-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                SIGNALS
              </p>
              <h3>
                Things to understand
              </h3>
            </div>
          </div>
          <div className="signal">
            <div className="signal-icon orange">
              ◈
            </div>
            <div>
              <strong>
                Crypto risk
              </strong>
              <p>
                {crypto
                  ? `${crypto.risk} historical downside signal`
                  : "No crypto detected"}
              </p>
            </div>
          </div>
          <div className="signal">
            <div className="signal-icon purple">
              ◉
            </div>
            <div>
              <strong>
                ETF overlap
              </strong>
              <p>
                {etfOverlap > 0
                  ? `${etfOverlap}% of ETF holdings overlap`
                  : "No ETF overlap detected"}
              </p>
            </div>
          </div>
          <div className="signal">
            <div className="signal-icon blue">
              %
            </div>
            <div>
              <strong>
                Rate environment
              </strong>
              <p>
                {rates
                  ? rates.direction.replace(
                      "_",
                      " "
                    )
                  : "No interest-bearing assets"}
              </p>
            </div>
          </div>
          <div className="signal">
            <div className="signal-icon green">
              ✓
            </div>
            <div>
              <strong>
                Holdings
              </strong>
              <p>
                {holdings.length} investments
                tracked
              </p>
            </div>
          </div>
        </div>
      </section>
      <section className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">
              YOUR MONEY
            </p>
            <h3>
              Investments
            </h3>
          </div>
          <span className="count">
            {holdings.length} holdings
          </span>
        </div>
        <div className="holdings-table">
          <div className="table-header">
            <span>Investment</span>
            <span>Type</span>
            <span>Value</span>
            <span>Portfolio</span>
          </div>
          {holdings.map(
            (holding) => (
              <div
                className="table-row"
                key={holding.id}
              >
                <strong>
                  {holding.ticker}
                </strong>
                <span className="type-pill">
                  {holding.asset_type}
                </span>
                <span>
                  $
                  {Number(
                    holding.value
                  ).toLocaleString()}
                </span>
                <span>
                  {holding.percentage}%
                </span>
              </div>
            )
          )}
        </div>
      </section>
      <section className="ai-card">
        <div className="ai-header">
          <div>
            <p className="eyebrow" style={{ textAlign: "center" }}>
              AI PORTFOLIO GUIDE
            </p>
            <h3>
              Want to understand your
              portfolio?
            </h3>
          </div>
        </div>
        <p>
          Ask Gemini to explain your
          portfolio, including concentration,
          diversification, and areas you
          could research.
        </p>
        <button
          className="ai-button"
          onClick={explainPortfolio}
          disabled={aiLoading}
        >
          {aiLoading
            ? "Analyzing Portfolio..."
            : "Explain My Portfolio"}
        </button>
        {aiAnalysis && (
          <div className="ai-response">
            <div className="ai-response-label">
              ✦ GEMINI ANALYSIS
            </div>
            <div className="ai-text">
              <ReactMarkdown>{aiAnalysis}</ReactMarkdown>
            </div>
          </div>
        )}
      </section>
    </main>

    {showAddInvestment && (
      <AddInvestmentModal
        newInvestment={newInvestment}
        setNewInvestment={setNewInvestment}
        addInvestment={addInvestment}
        addingInvestment={addingInvestment}
        onClose={() =>
          setShowAddInvestment(false)
        }
      />
      )}
    </div>
    );
  }

  //Add investment modal

  function AddInvestmentModal({
    newInvestment,
    setNewInvestment,
    addInvestment,
    addingInvestment,
    onClose,
  }) 

  {
  return (
    <div className="modal-overlay">
    <div className="investment-modal">
    <div className="modal-header">
    <div>
      <p className="eyebrow">
        PORTFOLIO
      </p>
      <h2>
        Add Investment
      </h2>
      </div>
        <button
          className="close-button"
          onClick={onClose}
        >
          ×
        </button>
      </div>
      <form onSubmit={addInvestment}>
        <label>
          Investment
          <input
            type="text"
            placeholder="e.g. VOO, BTC, Savings"
            value={newInvestment.ticker}
            onChange={(event) =>
              setNewInvestment({
              ...newInvestment,
              ticker:
                event.target.value,
              })
            }
            required
            />
          </label>
          <label>
            Investment Type
            <select
              value={newInvestment.asset_type}
              onChange={(event) =>
                setNewInvestment({
                  ...newInvestment,
                  asset_type:
                    event.target.value,
                })
              }
            >
              <option value="ETF">
                ETF
              </option>
              <option value="Stock">
                Stock
              </option>
              <option value="Crypto">
                Crypto
              </option>
              <option value="CD">
                CD
              </option>
              <option value="Savings">
                Savings Account
              </option>
              <option value="Bond">
                Bond
              </option>
              <option value="Cash">
                Cash
              </option>
              <option value="Other">
                Other
              </option>
            </select>
          </label>
          <label>
            Current Value
            <input
              type="number"
              min="0"
              step="0.01"
              placeholder="5000"
              value={newInvestment.value}
              onChange={(event) =>
                setNewInvestment({
                  ...newInvestment,
                  value:
                    event.target.value,
                })
              }
              required
            />
          </label>
          {(
            newInvestment.asset_type === "CD" ||
            newInvestment.asset_type === "Savings" ||
            newInvestment.asset_type === "Bond"
          ) && (
            <label>
              APY / Yield (%)
              <input
                type="number"
                min="0"
                step="0.01"
                placeholder="4.25"
                value={newInvestment.apy}
                onChange={(event) =>
                  setNewInvestment({
                    ...newInvestment,
                    apy: event.target.value,
                  })
                }
              />
            </label>
          )}
          {newInvestment.asset_type === "CD" && (
            <label>
              Maturity Date
              <input
                type="date"
                value={newInvestment.maturity_date}
                onChange={(event) =>
                  setNewInvestment({
                    ...newInvestment,
                    maturity_date: event.target.value,
                  })
                }
              />
            </label>
          )}
          <button
            type="submit"
            className="ai-button"
            disabled={addingInvestment}
          >
            {addingInvestment
              ? "Adding..."
              : "Add Investment"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;