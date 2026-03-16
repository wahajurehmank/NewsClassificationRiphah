from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
import re
import requests
from dotenv import load_dotenv
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import feedparser
from newspaper import Article
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus

# --- Configuration ---
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "test")
NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"
# --- Initialization ---
app = FastAPI(
    title="News Classification API",
    description="API for semantic news classification using a pre-trained LinearSVC model.",
    version="0.1.0"
)

# --- NLTK Setup ---
def setup_nltk():
    for res in ['punkt', 'stopwords', 'wordnet', 'omw-1.4', 'punkt_tab']:
        nltk.download(res, quiet=True)
    return {
        'lemmatizer': WordNetLemmatizer(),
        'stop_words': set(stopwords.words('english')),
        'tokenize': word_tokenize
    }

NLP = setup_nltk()

# --- Model Loading ---
# Note: In the new structure, model is in backend/
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'news_classifier_model.joblib')
if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"Model file {MODEL_PATH} not found.")

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load model: {e}")

# --- Mappings ---
from constants import MAPPING

# --- Logic Engine ---
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = NLP['tokenize'](text)
    tokens = [word for word in tokens if word not in NLP['stop_words']]
    tokens = [NLP['lemmatizer'].lemmatize(word) for word in tokens]
    return ' '.join(tokens)

# --- Schemas ---
class NewsInput(BaseModel):
    headline: str = ""
    description: str = ""

class BulkNewsInput(BaseModel):
    texts: list[str]

class CategoryScore(BaseModel):
    category: str
    confidence: float

class PredictionOutput(BaseModel):
    category: str
    confidence: float
    top_3: list[CategoryScore]

class NewsArticle(BaseModel):
    headline: str
    description: str
    url: str
    publication_date: str
    thumbnail: str = ""
    category: str = "PENDING"
    confidence: float = 0.0
    full_text: str = ""

class LiveNewsOutput(BaseModel):
    source: str
    query: str
    total_results: int
    articles: list[NewsArticle]

# --- Endpoints ---
@app.get("/")
async def root():
    return {"message": "News Classification API is online", "status": "healthy"}

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: NewsInput):
    if not input_data.headline.strip() and not input_data.description.strip():
        raise HTTPException(status_code=400, detail="Input signal required (headline or description).")
    
    raw_text = f"{input_data.headline} {input_data.description}".strip()
    processed_text = clean_text(raw_text)
    
    try:
        # Predict category
        prediction_id = model.predict([processed_text])[0]
        category = MAPPING.get(prediction_id, "General")
        
        # Calculate confidence scores
        scores = model.decision_function([processed_text])[0]
        exp_s = np.exp(scores - np.max(scores))
        probs = exp_s / exp_s.sum()
        
        # Get top 3 categories
        top_indices = np.argsort(probs)[-3:][::-1]
        top_3 = []
        for idx in top_indices:
            top_3.append({
                "category": MAPPING.get(idx, "Other"),
                "confidence": float(probs[idx])
            })
            
        confidence = float(np.max(probs))
        
        return PredictionOutput(
            category=category,
            confidence=confidence,
            top_3=top_3
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/bulk-predict")
async def bulk_predict(input_data: BulkNewsInput):
    """Predict categories for multiple texts at once, handling empty/short signals."""
    if not input_data.texts:
        return {"predictions": []}
    
    results = []
    texts_to_predict = []
    predict_indices = []

    for i, text in enumerate(input_data.texts):
        cleaned = clean_text(text)
        # If less than 2 words after cleaning, it's insufficient data
        if len(cleaned.split()) < 2:
            results.append("Insufficient Data")
        else:
            # Placeholder for prediction
            results.append(None)
            texts_to_predict.append(cleaned)
            predict_indices.append(i)
    
    try:
        if texts_to_predict:
            predictions = model.predict(texts_to_predict)
            for i, pred_id in enumerate(predictions):
                results[predict_indices[i]] = MAPPING.get(pred_id, "General")
        
        return {"predictions": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk prediction error: {str(e)}")

@app.get("/clean-text")
async def api_clean_text(text: str):
    """Clean text using the same logic as the labels."""
    return {"cleaned": clean_text(text)}

@app.get("/fetch-live-news", response_model=LiveNewsOutput)
async def fetch_live_news(query: str = "latest", page_size: int = 10, api_source: str = "google-rss"):
    """Fetch live news from Google RSS or NewsAPI and classify them."""
    articles = []
    total = 0
    
    print(f"--- Fetching News ({api_source}) --- Query: {query}")
    
    try:
        if api_source.lower() == "google-rss":
            encoded_query = quote_plus(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}"
            feed = feedparser.parse(rss_url)
            total = len(feed.entries)
            
            # Use small pool to avoid CPU spikes on dual-core
            def process_entry(entry):
                try:
                    # Article handles redirects automatically
                    article = Article(entry.link)
                    article.download()
                    article.parse()
                    
                    headline = entry.title
                    if " - " in headline:
                        headline = " - ".join(headline.split(" - ")[:-1])
                        
                    return {
                        "headline": headline,
                        "description": entry.summary[:200] + "...",
                        "url": entry.link,
                        "publication_date": entry.published if 'published' in entry else "",
                        "full_text": article.text
                    }
                except Exception as e:
                    print(f"Scrape error for {entry.link}: {e}")
                    return {
                        "headline": entry.title,
                        "description": entry.summary[:200] + "...",
                        "url": entry.link,
                        "publication_date": entry.published if 'published' in entry else "",
                        "full_text": ""
                    }

            entries_to_process = feed.entries[:page_size]
            with ThreadPoolExecutor(max_workers=3) as executor:
                articles = list(executor.map(process_entry, entries_to_process))

        elif api_source.lower() == "newsapi":
            params = {
                "q": query, "apiKey": NEWS_API_KEY, "pageSize": page_size,
                "sortBy": "publishedAt", "language": "en"
            }
            response = requests.get(NEWS_API_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get("articles", [])
            total = data.get("totalResults", 0)
            for res in results:
                articles.append({
                    "headline": res.get("title") or "Untitled",
                    "description": res.get("description") or "",
                    "url": res.get("url") or "#",
                    "publication_date": res.get("publishedAt") or "",
                    "full_text": ""
                })
        else:
            raise HTTPException(status_code=400, detail="Invalid api_source.")

        # Classify articles
        classified_articles = []
        for art in articles:
            # Predict
            signal = f"{art['headline']} {art['description']} {art['full_text'][:500]}".strip()
            proc = clean_text(signal)
            try:
                pred_id = model.predict([proc])[0]
                category = MAPPING.get(pred_id, "General")
                
                scores = model.decision_function([proc])[0]
                exp_s = np.exp(scores - np.max(scores))
                probs = exp_s / exp_s.sum()
                confidence = float(np.max(probs))
            except:
                category, confidence = "General", 0.0
            
            complete_art = {**art, "category": category, "confidence": confidence}
            classified_articles.append(NewsArticle(**complete_art))
            
        return LiveNewsOutput(
            source=api_source,
            query=query,
            total_results=total,
            articles=classified_articles
        )
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
