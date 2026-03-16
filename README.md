# News Intelligence System 📰

A complete system for news classification and analysis, featuring a FastAPI backend and a Streamlit dashboard.

## 🏗️ Project Structure

- `backend/`: FastAPI service for text cleaning and news classification.
- `frontend/`: Streamlit dashboard for visualizing news data and interacting with the backend.

## 🛠️ Prerequisites

- [Python](https://www.python.org/) 3.10+
- [uv](https://github.com/astral-sh/uv) (Highly recommended for dependency management)

## 🚀 Quick Start

### 1. Set up the Backend
```bash
cd backend
uv sync
# Copy .env.example to .env and add your News API Key
cp .env.example .env
# Run the server
uv run python main.py
```

### 2. Set up the Frontend
```bash
cd frontend
uv sync
# Run the dashboard
uv run streamlit run app.py
```

## 🔑 Environment Variables

The backend requires a `NEWS_API_KEY`. Create a `.env` file in the `backend/` directory based on `backend/.env.example`.

## 📦 Core Dependencies

- **Backend**: FastAPI, uvicorn, scikit-learn, nltk, newspaper3k.
- **Frontend**: Streamlit, pandas, plotly, fpdf2.
