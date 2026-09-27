# Student Portfolio Analyzer

An AI investment portfolio analysis tool built for hackUMBC 2026.

## Overview

This application allows users to input their investment portfolio data and 
generates an interactive dashboard that provides a clear view of their investments. 
The dashboard shows portfolio allocation and provides additional insights into areas 
such as cryptocurrency risk, ETF overlap, interest rate conditions, and interest-bearing assets.

The application addresses the challenge of understanding investment portfolios through 
traditional financial platforms, which often provide information without clearly 
explaining what it means for an individual investor. This can be especially challenging 
for students and first-time investors who are still learning how different investment options 
work and how they contribute to an overall portfolio.

The application is intended for students and individuals who are beginning to invest and 
want a clearer understanding of their portfolio and the investment options available to them. 
By bringing portfolio information and analysis into one dashboard, the application helps 
users better understand what they own and the factors that may affect their investments.

## Features
- Dashboard to visualize investment portfolio
- Cryptocurrency risk analysis
- ETF overlap analysis
- Interest rate yeild analysis
- Portfolio insights explained by Gemini

## Tech Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite

### Data Analysis / Machine Learning
- Pandas
- Numpy
- scikit-learn

### Datasets 
- CoinGecko API for cryptocurrency: https://www.coingecko.com/en/api
- FRED data for interest rates: https://fred.stlouisfed.org/

## How to Run

### Prerequisites

Make sure you have the following installed:
- Node.js
- Python 3.x
- Git

1. Clone the Repository

git clone <your-repository-url>
cd <your-repository-name>

2. Set Up the Backend

Create and activate a Python virtual environment:

python -m venv venv

Windows:

venv\Scripts\activate

macOS/Linux:

source venv/bin/activate

Install the Python dependencies:

pip install -r requirements.txt

3. Configure Environment Variables

Create a .env file in the backend directory and add the required environment variables.

GEMINI_API_KEY=your_api_key

If you do not have a Gemini API key, you can get one here: https://aistudio.google.com/api-keys

4. Start the Backend

From the backend directory, run:

uvicorn main:app --reload

The FastAPI backend will be available at:

http://localhost:8000

5. Set Up the Frontend

Open a new terminal and navigate to the frontend directory:

cd frontend

Install the JavaScript dependencies:

npm install

Start the development server:

npm run dev

The React application will be available at the local URL provided by Vite:

http://localhost:5173

6. Use the Application

With both the frontend and backend running, open the frontend URL in your browser. 
The React application will communicate with the FastAPI backend to retrieve and 
analyze portfolio data.