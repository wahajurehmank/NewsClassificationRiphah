# News Intelligence System 📰

A complete system for news classification and analysis, featuring a FastAPI backend and a Streamlit dashboard.

---

## 🚀 Setup Guide (Chronological)

Follow these steps in order to get the project running on your machine.

### 1. Clone the Repository
Open your terminal and clone the project:
```bash
git clone https://github.com/wahajurehmank/NewsClassificationRiphah.git
cd NewsClassificationRiphah
```

### 2. API Key Setup (Optional)
The core classification logic works offline. However, if you want to use the **Live News Feed** feature:
1. Get a free key from [NewsAPI.org](https://newsapi.org/).
2. Go to the `backend/` folder.
3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` and paste your key: `NEWS_API_KEY=your_key_here`

### 3. Install `uv` (Optional but Recommended)
If you don't have `uv` installed, run the appropriate command for your OS:

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 4. Start the Backend (FastAPI)
You can choose either **Option A (Faster)** or **Option B (Standard)**.

#### Option A: Using `uv` (Recommended)
```bash
cd backend
uv sync
uv run python main.py
```

#### Option B: Using `pip`
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
*The backend will be live at http://localhost:8000*

### 5. Start the Frontend (Streamlit)
Open a **new terminal** window, navigate to the project root, and then:

#### Option A: Using `uv` (Recommended)
```bash
cd frontend
uv sync
uv run streamlit run app.py
```

#### Option B: Using `pip`
```bash
cd frontend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 🏗️ Project Architecture
- `backend/`: FastAPI service. Handles NLTK processing, text cleaning, and model prediction.
- `frontend/`: Streamlit UI. Provides the dashboard, file upload (CSV/Excel), and live news interface.

## 📦 Core Dependencies
- **Backend**: FastAPI, uvicorn, scikit-learn, joblib, nltk, newspaper3k.
- **Frontend**: Streamlit, pandas, plotly, matplotlib, fpdf2.
