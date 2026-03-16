# Student Management - Backend

This is the FastAPI-based news classification service.

## 🚀 How to Activate

### 1. Initialize/Sync Environment
Ensure you are in the `backend` directory and sync dependencies:
```bash
uv sync
```

### 2. Activate Virtual Environment
```bash
source .venv/bin/activate
```

### 3. Run the API
You can run the API in reload mode (for development):
```bash
uv run uvicorn main:app --reload --port 8000
```
Or run it directly via the script:
```bash
uv run python main.py
```

---
**Note:** If `uvicorn` fails to spawn, ensure you have run `uv sync` while in this directory.
