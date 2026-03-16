# News Intelligence System 📰

A complete system for news classification and analysis, featuring a FastAPI backend and a Streamlit dashboard.

---

## 🏗️ Project Structure

- `backend/`: FastAPI service for text cleaning and news classification.
- `frontend/`: Streamlit dashboard for visualizing news data and interacting with the backend.

---

## 🔑 API Key (Optional)

The core classification features work **without** an API key. However, if you want to use the **Live News Feed** feature:
1. Get a free key from [NewsAPI.org](https://newsapi.org/).
2. Navigate to the `backend/` folder.
3. Rename the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Open `.env` and paste your key:
   ```env
   NEWS_API_KEY=your_actual_key_here
   ```

---

## 🚀 Installation & Setup

### Option A: Using `uv` (Recommended - Faster & Easier)

If you don't have `uv` installed, run this first:
```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**1. Start the Backend:**
```bash
cd backend
uv sync
uv run python main.py
```

**2. Start the Frontend (New Terminal):**
```bash
cd frontend
uv sync
uv run streamlit run app.py
```

---

### Option B: Using Standard `pip` (The Traditional Way)

**1. Start the Backend:**
```bash
cd backend
python -m venv .venv
# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**2. Start the Frontend (New Terminal):**
```bash
cd frontend
python -m venv .venv
# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 📦 Core Dependencies

- **Backend**: FastAPI, uvicorn, scikit-learn, joblib, nltk, newspaper3k.
- **Frontend**: Streamlit, pandas, plotly, matplotlib, fpdf2.
