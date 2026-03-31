import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from fpdf import FPDF
from fpdf.enums import XPos, YPos
try:
    import trafilatura
except ImportError:
    trafilatura = None

from pdf_reports import NewsReportGenerator
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Shared Constants Injection ---
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
try:
    from constants import (
        MAPPING, ICONS, CATEGORY_THEMES, MASTER_CATEGORY_MAPPING, 
        STAKEHOLDER_INSIGHTS, FAMOUS_SOURCES_UI, STAKEHOLDER_INSIGHTS_UR
    )
    from translations import TRANSLATIONS
except ImportError:
    # Fallback to avoid complete crash if constants are missing
    MAPPING, ICONS, CATEGORY_THEMES = {}, {}, {}
    MASTER_CATEGORY_MAPPING, STAKEHOLDER_INSIGHTS = {}, {}
    FAMOUS_SOURCES_UI, STAKEHOLDER_INSIGHTS_UR = {}, {}
    TRANSLATIONS = {'en': {'categories': {}}, 'ur': {'categories': {}}}

# --- Default Language Code ---
L_CODE = 'en'

# --- Translation System Managed via Backend/Translations.py ---

# --- Translations System ---

# --- Translation Helpers ---
def tr(key):
    return TRANSLATIONS[L_CODE].get(key, key)

def tr_cat(cat):
    if not cat: return "General"
    val = TRANSLATIONS[L_CODE]['categories'].get(str(cat), str(cat))
    return str(val) if val is not None else "General"

def get_insights(cat):
    if L_CODE == 'ur':
        return STAKEHOLDER_INSIGHTS_UR.get(cat, STAKEHOLDER_INSIGHTS_UR['General'])
    return STAKEHOLDER_INSIGHTS.get(cat, STAKEHOLDER_INSIGHTS['General'])

# --- Load Environment Variables ---
# Looking for .env in the backend folder
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

# --- App Configuration ---
st.set_page_config(
    page_title="Streamlined News Classification",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

def is_quality_content(text):
    """
    Ultra-strict heuristic to prune out symbol-heavy, sparse, or junk content.
    """
    if not text: return False
    text = text.strip()
    
    # 1. Clean characters check (ignoring whitespace)
    actual_chars = "".join(text.split())
    if len(actual_chars) < 400: return False
    
    # 2. Real Word Check
    # We define 'real words' as strings of 3+ letters
    words = [w for w in text.split() if len(w) >= 3 and any(c.isalpha() for c in w)]
    if len(words) < 40: return False
    
    # 3. Average Word Length (Real articles have average 4.5 - 8 chars per word)
    avg_len = sum(len(w) for w in words) / len(words)
    if avg_len < 4.5 or avg_len > 15: return False
    
    # 4. Symbol & Digit Density
    letters = sum(c.isalpha() for c in actual_chars)
    digits = sum(c.isdigit() for c in actual_chars)
    total_chars = len(actual_chars)
    
    # Financial tables and date-heavy noise usually have letters < 80%
    if letters < (total_chars * 0.85): return False
    # If digits are more than 8%, it's likely a list of prices or dates
    if digits > (total_chars * 0.08): return False
    
    return True

def fetch_full_content(url):
    """
    Fetch full article content from a direct URL (e.g. from a user's CSV).
    Uses requests with browser-like headers. No Google News involved.
    Trafilatura extracts clean text; falls back to newspaper3k.
    """
    if not url or pd.isna(url):
        return None

    SCRAPE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    raw_html = None
    try:
        resp = requests.get(url, headers=SCRAPE_HEADERS, timeout=6, allow_redirects=True)
        resp.raise_for_status()
        raw_html = resp.text
    except Exception:
        pass

    # Primary: trafilatura (best accuracy for news articles)
    if raw_html and trafilatura:
        try:
            content = trafilatura.extract(raw_html, include_comments=False,
                                          include_tables=False, favor_recall=True)
            if is_quality_content(content):
                return content.strip()
        except Exception:
            pass

    # Fallback: newspaper3k
    if raw_html:
        try:
            from newspaper import Article as NPArticle
            art = NPArticle(url)
            art.set_html(raw_html)
            art.parse()
            if is_quality_content(art.text):
                return art.text.strip()
        except Exception:
            pass

    return None

def create_pdf_report(df, h_col, filter_cat=None, deep_dive=False, url_col=None):
    # Filter by category if requested
    if filter_cat and filter_cat != tr('all_cats'):
        df = df[df['Predicted Category'] == filter_cat].copy()

    report_title = "INTELLIGENCE BRIEFING" if not deep_dive else "DEEP DIVE AUDIT"
    _meta = f"Domain: {filter_cat if filter_cat else 'Comprehensive Analysis'} | {datetime.now().strftime('%B %d, %Y')}"
    
    generator = NewsReportGenerator(title=report_title, subtitle=_meta)
    
    if deep_dive:
        return generator.generate_deep_dive_report(df, h_col, fetch_full_content, url_col=url_col)
    else:
        return generator.generate_summary_report(df, h_col, url_col=url_col, use_reliability=True)

# --- Backend URL Configuration ---
API_BASE = "http://localhost:8000"

# --- Mappings & Themes (Updated Super-Category Taxonomy) ---
# --- UI Themes & Insights Loaded from Shared Config ---

# --- Premium Dark UI Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono&family=Noto+Nastaliq+Urdu:wght@400;700&display=swap');

    .stApp {
        background-color: #05070a;
        font-family: 'Outfit', sans-serif;
        color: #e2e8f0;
    }

    [dir="rtl"] .stApp, [dir="rtl"] p, [dir="rtl"] span, [dir="rtl"] label, [dir="rtl"] div {
        font-family: 'Noto Nastaliq Urdu', serif !important;
        direction: rtl;
        text-align: right;
    }
    
    [dir="rtl"] .stMetric {
        text-align: right !important;
    }

    /* Adjust Sidebar for RTL */
    [dir="rtl"] [data-testid="stSidebar"] {
        border-right: none !important;
        border-left: 1px solid rgba(255,255,255,0.05);
    }

    [data-testid="stSidebar"] {
        background-color: #0a0d14 !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    /* Style for Containers with Border (Glass Card effect) */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background: rgba(17, 25, 40, 0.75) !important;
        backdrop-filter: blur(12px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }

    /* Input Field Polishing */
    .stTextArea textarea, .stTextInput input {
        background: rgba(31, 41, 55, 0.5) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        padding: 14px !important;
        transition: all 0.3s ease;
    }

    /* Metric Layout Fixes */
    [data-testid="stMetric"] {
        background: transparent !important;
        padding: 10px !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #2dd4bf 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        padding: 12px 24px !important;
        width: 100%;
        transition: all 0.4s ease !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
    }

    /* Premium Link Styling */
    .article-title-link {
        color: #60a5fa !important;
        text-decoration: none !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
        transition: all 0.3s ease !important;
        border-bottom: 1px solid transparent !important;
    }
    .article-title-link:hover {
        color: #93c5fd !important;
        border-bottom: 1px solid #93c5fd !important;
    }

    .prediction-reveal {
        padding: 50px 30px;
        border-radius: 24px;
        text-align: center;
        margin-top: 30px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }

    .flow-step {
        background: rgba(48, 54, 61, 0.3);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        font-size: 0.9rem;
    }

    .radar-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #94a3b8;
        margin-bottom: 5px;
    }

    .error-container {
        max-width: 600px;
        margin: 100px auto;
        padding: 40px;
        background: rgba(239, 68, 68, 0.05);
        border: 1px solid rgba(239, 68, 68, 0.5);
        border-radius: 24px;
        text-align: center;
    }
    
    /* Article Card Layout Helper */
    .article-card-flex {
        display: flex;
        gap: 25px;
        align-items: flex-start;
        padding: 5px 0;
    }
    .article-img-container {
        flex: 0 0 180px;
        max-width: 180px;
    }
    .article-content-container {
        flex: 1;
    }
    @media (max-width: 768px) {
        .article-card-flex {
            flex-direction: column;
        }
        .article-img-container {
            width: 100%;
            max-width: 100%;
            flex: none;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration (Language First) ---
with st.sidebar:
    language = st.selectbox("🌐 Language / زبان", ["English", "اردو"], index=0)
    L_CODE = 'en' if language == "English" else 'ur'
    
    # Inject RTL/LTR based on choice
    if L_CODE == 'ur':
        st.markdown('<script>document.body.dir = "rtl";</script>', unsafe_allow_html=True)
        st.markdown('<style>body { direction: rtl; text-align: right; }</style>', unsafe_allow_html=True)
    else:
        st.markdown('<script>document.body.dir = "ltr";</script>', unsafe_allow_html=True)
        st.markdown('<style>body { direction: ltr; text-align: left; }</style>', unsafe_allow_html=True)

# --- System Status Check ---
try:
    health_resp = requests.get(f"{API_BASE}/")
    is_online = health_resp.status_code == 200
except:
    is_online = False

if not is_online:
    st.markdown(f"""
        <div class="error-container">
            <h1 style="color: #ef4444; margin-top: 0;">{tr('error_sys_offline')}</h1>
            <p style="font-size: 1.2rem; margin-bottom: 2rem;">The News Intelligence Backend is not reachable.</p>
            <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 12px; font-family: monospace; font-size: 0.9rem; color: #f87171;">
                Ensure you have started the backend using: `uv run python main.py` in the backend folder.
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- Sidebar (Navigation) ---
with st.sidebar:
    st.markdown(f"### {TRANSLATIONS[L_CODE]['side_title']}")
    page = st.radio(TRANSLATIONS[L_CODE]['nav_label'], TRANSLATIONS[L_CODE]['nav_options'], label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"### {TRANSLATIONS[L_CODE]['status_label']}")
    st.info(TRANSLATIONS[L_CODE]['ai_ready'])
    st.success(TRANSLATIONS[L_CODE]['sys_online'])
    st.markdown("---")
    st.caption(TRANSLATIONS[L_CODE]['built_for'])

# --- Page: Classify News ---
if page == tr('nav_options')[0]:
    st.markdown(f"<h1 style='font-size: 3rem;'>{tr('main_title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #94a3b8; font-size: 1.1rem;'>{tr('main_sub')}</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs for Single vs Bulk
    tab1, tab2, tab3 = st.tabs(tr('tabs'))

    with tab1:
        col_input, col_radar = st.columns([1.6, 1])
        
        with col_input:
            with st.container(border=True):
                st.markdown(f"### {tr('paste_title')}")
                headline = st.text_input(tr('headline'), value="Olympic athletes break world record in 100m sprint finals", placeholder=tr('headline_placeholder'), key="single_headline")
                description = st.text_area(tr('desc'), value="Multiple athletes competed in the highly anticipated 100m sprint finals at the Olympics, with the winner shattering the previous world record by 0.03 seconds.", placeholder=tr('desc_placeholder'), height=200, key="single_desc")
                analyze = st.button(tr('analyze_btn'), key="single_analyze", width="stretch")

        with col_radar:
            with st.container(border=True):
                st.markdown(f"### {tr('ai_confidence')}")
                radar_container = st.empty()
                radar_container.info(tr('radar_info'))

        if analyze:
            if not headline.strip() and not description.strip():
                st.warning(tr('empty_warning'))
            else:
                with st.spinner(tr('analyzing')):
                    try:
                        resp = requests.post(f"{API_BASE}/predict", json={"headline": headline, "description": description}, timeout=10)
                        resp.raise_for_status()
                        data = resp.json()
                        # Persistent state for Single Analysis
                        st.session_state['single_prediction'] = {
                            "category": data['category'],
                            "top_3": data['top_3'],
                            "headline": headline,
                            "description": description
                        }
                    except Exception as e:
                        st.error(f"Prediction failed: {e}")
                        st.session_state['single_prediction'] = None

        if st.session_state.get('single_prediction'):
            pred = st.session_state['single_prediction']
            category = pred['category']
            top_3_data = pred['top_3']
            
            icon = ICONS.get(category, "🎭")
            theme = CATEGORY_THEMES.get(category, {'color': '#3b82f6', 'glow': 'rgba(255,255,255,0.2)'})
            
            with radar_container.container():
                st.markdown("<br>", unsafe_allow_html=True)
                for item in top_3_data:
                    c_name = item['category']
                    c_val = item['confidence']
                    
                    if c_val > 0.8: label = tr('highly_confident')
                    elif c_val > 0.5: label = tr('likely_match')
                    else: label = tr('possible_match')
                    
                    st.markdown(f'<div class="radar-label">{tr_cat(c_name)} — {label}</div>', unsafe_allow_html=True)
                    st.progress(float(c_val))

            # Main Reveal
            st.markdown(f"""
                <div class="prediction-reveal" style="background: radial-gradient(circle at center, {theme['color']}33 0%, #05070a 100%); border-color: {theme['color']}66; box-shadow: 0 0 30px {theme['glow']};">
                    <div style="font-size: 0.8rem; font-weight: 700; letter-spacing: 3px; color: rgba(255,255,255,0.7); margin-bottom: 15px;">{tr('article_about')}</div>
                    <div style="font-size: 5rem; margin-bottom: 10px;">{icon}</div>
                    <div style="font-size: 3.5rem; font-weight: 800; color: {theme['color']}; margin: 0;">{tr_cat(category)}</div>
                </div>
            """, unsafe_allow_html=True)

            # --- Plain English Explanation ---
            category_insights = get_insights(category)
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px 25px; margin-top: 20px; text-align: center;">
                    <p style="color: #e2e8f0; font-size: 1.1rem; line-height: 1.6; margin: 0;">{category_insights['Simple']}</p>
                </div>
            """, unsafe_allow_html=True)

            # --- Deeper Insights Section ---
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(tr('more_context'))
            s_col1, s_col2 = st.columns(2)
            
            with s_col1:
                with st.container(border=True):
                    st.markdown(f"<h4 style='color: {theme['color']};'>{tr('fun_fact')}</h4>", unsafe_allow_html=True)
                    st.write(category_insights['FunFact'])
                    
            with s_col2:
                with st.container(border=True):
                    st.markdown(f"<h4 style='color: {theme['color']};'>{tr('why_ai')}</h4>", unsafe_allow_html=True)
                    st.write(category_insights['Context'])

    with tab2:
        st.markdown(tr('bulk_title'))
        st.markdown(tr('bulk_sub'))
        
        uploaded_file = st.file_uploader(tr('upload_label'), type=["csv", "xlsx"])
        
        if not uploaded_file:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.15); border-radius: 16px; padding: 40px; text-align: center; margin-top: 10px;">
                <div style="font-size: 3rem; margin-bottom: 15px;">📄</div>
                <p style="color: #94a3b8; font-size: 1rem;">{tr('upload_info')}</p>
                <p style="color: #64748b; font-size: 0.85rem;">{tr('upload_sub')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Reset results if a different file is uploaded
                if 'bulk_filename' not in st.session_state or st.session_state['bulk_filename'] != uploaded_file.name:
                    st.session_state['bulk_results'] = None
                    st.session_state['bulk_filename'] = uploaded_file.name
                    st.session_state['bulk_h_col'] = None
                    # Clear generated reports
                    if 'bulk_pdf_bytes' in st.session_state: del st.session_state['bulk_pdf_bytes']
                
                # Smart Column Auto-detection
                cols = df.columns.tolist()
                def find_match(targets, candidates):
                    for t in targets:
                        for c in candidates:
                            if t.lower() in c.lower(): return c
                    return None # Return None if no clear match found

                detected_h = find_match(['headline', 'title', 'subject'], cols)
                detected_d = find_match(['description', 'summary', 'desc', 'short'], cols)
                detected_u = find_match(['url', 'link', 'source', 'href'], cols)

                # UI Warning if match not found
                if not detected_h:
                    st.warning(tr('col_err'))
                
                # Only show selectors
                with st.expander(tr('verify_cols'), expanded=(not detected_h)):
                    h_col = st.selectbox(tr('col_h'), cols, index=cols.index(detected_h) if detected_h else 0)
                    d_col = st.selectbox(tr('col_d'), cols, index=cols.index(detected_d) if detected_d else 0)
                    u_col = st.selectbox("URL Column (Optional)", ["None"] + cols, index=cols.index(detected_u) + 1 if detected_u else 0)
                
                if st.button(tr('classify_all'), type="primary"):
                    with st.status(tr('processing_bulk')) as status:
                        # 1. Collect texts for API
                        df['combined_text'] = (df[h_col].fillna('') + " " + df[d_col].fillna(''))
                        texts = df['combined_text'].tolist()
                        
                        # 2. Parallel Chunked Processing
                        CHUNK_SIZE = 50
                        chunks = [texts[i:i + CHUNK_SIZE] for i in range(0, len(texts), CHUNK_SIZE)]
                        results = [None] * len(texts)
                        
                        progress_bar = st.progress(0.0)
                        
                        def process_chunk(chunk_idx, chunk_data):
                            try:
                                resp = requests.post(f"{API_BASE}/bulk-predict", json={"texts": chunk_data}, timeout=30)
                                resp.raise_for_status()
                                return chunk_idx, resp.json()['predictions']
                            except Exception as e:
                                return chunk_idx, [f"Error: {str(e)}"] * len(chunk_data)

                        # Use ThreadPoolExecutor to prevent blocking the main heartbeat
                        with ThreadPoolExecutor(max_workers=4) as executor:
                            future_to_chunk = {executor.submit(process_chunk, i, chunk): i for i, chunk in enumerate(chunks)}
                            completed = 0
                            total_chunks = len(chunks)
                            
                            for future in as_completed(future_to_chunk):
                                try:
                                    chunk_idx, predictions = future.result()
                                    start_idx = chunk_idx * CHUNK_SIZE
                                    results[start_idx:start_idx + len(predictions)] = predictions
                                    completed += 1
                                    
                                    # Update UI elements from the main loop
                                    progress_bar.progress(completed / total_chunks)
                                    status.update(label=f"Analysis in progress... ({completed}/{total_chunks} batches)")
                                except Exception as e:
                                    st.error(f"Batch processing error: {e}")

                        df['Predicted Category'] = results
                        status.update(label="✅ Analysis Complete!", state="complete")
                        
                        # Store in session state for persistence
                        st.session_state['bulk_results'] = df
                        st.session_state['bulk_h_col'] = h_col
                        st.session_state['bulk_u_col'] = u_col if u_col != "None" else None
                        # Clear old PDFs as data has changed
                        if 'bulk_pdf_bytes' in st.session_state: del st.session_state['bulk_pdf_bytes']

                if st.session_state.get('bulk_results') is not None:
                    res_df = st.session_state['bulk_results']
                    res_h_col = st.session_state['bulk_h_col']
                    
                    # Results display
                    st.markdown("---")
                    st.markdown(tr('results_title'))
                    
                    # Summary metrics
                    counts = res_df['Predicted Category'].value_counts()
                    top_cat = counts.idxmax()
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric(tr('metric_classified'), len(res_df))
                    m2.metric(tr('metric_common'), tr_cat(top_cat))
                    m3.metric(tr('metric_topics'), len(counts))
                    
                    # Pie Chart
                    import plotly.express as px
                    # Translate index for the chart
                    counts_display = counts.copy()
                    counts_display.index = [tr_cat(c) for c in counts_display.index]
                    
                    fig = px.pie(
                        values=counts_display.values, 
                        names=counts_display.index,
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#e2e8f0',
                        legend=dict(font=dict(size=12)),
                        margin=dict(t=20, b=20, l=20, r=20),
                        height=350
                    )
                    fig.update_traces(textinfo='label+percent', textfont_size=12)
                    st.plotly_chart(fig, width="stretch")
                    
                    # Insights for Top Categories
                    st.markdown(tr('interesting_discoveries'))
                    st.info(tr('discovery_msg').format(tr_cat(top_cat)))
                    
                    b_col1, b_col2 = st.columns(2)
                    top_insights = get_insights(top_cat)
                    
                    with b_col1:
                        with st.container(border=True):
                            st.markdown(f"<h4>{tr('what_is_this')}</h4>", unsafe_allow_html=True)
                            st.write(top_insights['Simple'])
                            
                    with b_col2:
                        with st.container(border=True):
                            st.markdown(f"<h4>{tr('fun_fact')}</h4>", unsafe_allow_html=True)
                            st.write(top_insights['FunFact'])
                            
                    st.markdown(tr('explore_data'))
                    
                    display_cols = list(set([res_h_col, 'Predicted Category']))
                    # We can't easily translate values inside the dataframe without copying it
                    df_display = res_df[display_cols].copy()
                    df_display['Predicted Category'] = df_display['Predicted Category'].apply(tr_cat)
                    st.dataframe(df_display, width="stretch")
                    
                    # Downloads Section
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(tr('export_work'))
                    
                    with st.container(border=True):
                        e_col1, e_col2 = st.columns(2)
                        # Invalidate PDF if report filter or deep dive changes
                        raw_cats = res_df['Predicted Category'].unique().tolist()
                        available_cats = [tr('all_cats')] + sorted([str(c) for c in raw_cats])
                        report_filter = st.selectbox(tr('filter_report_cat'), available_cats, key='bulk_filter_sel')
                        
                        # Check if filter changed since last generation
                        if st.session_state.get('last_bulk_pdf_filter') != report_filter:
                            if 'bulk_pdf_bytes' in st.session_state: del st.session_state['bulk_pdf_bytes']
                            if 'bulk_deep_df' in st.session_state: del st.session_state['bulk_deep_df']
                            
                        with e_col2:
                            u_col_final = st.session_state.get('bulk_u_col')
                            is_deep = st.checkbox(tr('include_full_text'), disabled=(u_col_final is None), key='bulk_deep_chk')
                            if st.session_state.get('last_bulk_pdf_deep') != is_deep:
                                if 'bulk_pdf_bytes' in st.session_state: del st.session_state['bulk_pdf_bytes']
                                if 'bulk_deep_df' in st.session_state: del st.session_state['bulk_deep_df']
                            if u_col_final is None:
                                st.caption(tr('no_url_warn'))

                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Use a trigger to generate the PDF
                        if st.button("🛠️ " + tr('btn_pdf'), width="stretch", key='bulk_gen_pdf_btn'):
                            # Preview filter for logging/depth
                            f_df = res_df.copy()
                            if report_filter != tr('all_cats'):
                                f_df = f_df[f_df['Predicted Category'] == report_filter]
                            
                            limit_info = ""
                            if is_deep and len(f_df) > 50:
                                limit_info = " (Limited to first 50 articles)"
                                
                            with st.spinner(f"{tr('fetching_articles')}{limit_info}" if is_deep else "Generating Report..."):
                                report_bytes, filtered_df = create_pdf_report(res_df, res_h_col, filter_cat=report_filter, deep_dive=is_deep, url_col=u_col_final)
                                st.session_state['bulk_pdf_bytes'] = bytes(report_bytes)
                                st.session_state['bulk_pdf_name'] = f"Report_{report_filter}_{datetime.now().strftime('%H%M%S')}.pdf"
                                st.session_state['last_bulk_pdf_filter'] = report_filter
                                st.session_state['last_bulk_pdf_deep'] = is_deep
                                # Store the filtered DF for CSV export if deep dive was used
                                if is_deep:
                                    st.session_state['bulk_deep_df'] = filtered_df
                                else:
                                    if 'bulk_deep_df' in st.session_state: del st.session_state['bulk_deep_df']

                        if 'bulk_pdf_bytes' in st.session_state:
                            st.download_button(
                                "✅ " + tr('btn_pdf'),
                                st.session_state['bulk_pdf_bytes'],
                                st.session_state['bulk_pdf_name'],
                                "application/pdf",
                                width="stretch",
                                key='bulk_dl_pdf_btn'
                            )
                            
                        # CSV Export
                        csv_filter_df = res_df.copy()
                        if report_filter != tr('all_cats'):
                            csv_filter_df = csv_filter_df[csv_filter_df['Predicted Category'] == report_filter]
                        
                        # Use filtered deep dive results if available and requested
                        is_deep_active = st.session_state.get('bulk_deep_chk')
                        if is_deep_active and st.session_state.get('bulk_deep_df') is not None:
                            csv_filter_df = st.session_state['bulk_deep_df']
                        elif is_deep_active:
                            # If deep dive is checked but NOT yet generated, we should warn or limit to first 50
                            # but the user explicitly asked to "keep articles that are fetched".
                            # This implies they must click Generate first, or we do it here.
                            # To keep it fast, we'll just show a message if they try to download without generating.
                            pass

                        st.download_button(
                            tr('btn_csv'),
                            csv_filter_df.to_csv(index=False).encode('utf-8'),
                            f"Data_{report_filter}_{datetime.now().strftime('%Y%m%d')}.csv",
                            "text/csv",
                            key='bulk-csv-download-btn',
                            width="stretch",
                            help=tr('btn_csv_help') if is_deep_active and st.session_state.get('bulk_deep_df') is None else None
                        )
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                st.error(f"{tr('error_prefix')}: {e}")

    # --- TAB 3: LIVE NEWS ---
    with tab3:
        st.markdown(f"<h2 style='font-size: 2.2rem;'>{tr('live_title')}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #94a3b8;'>{tr('live_sub')}</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # News Source Configuration
        with st.container(border=True):
            query = st.text_input(tr('live_input'), placeholder=tr('live_placeholder'), key="live_query")
            
            with st.expander(tr('adv_settings')):
                lc1, lc2 = st.columns(2)
                with lc1:
                    news_source = st.selectbox(tr('news_provider'), [tr('google_news'), "NewsAPI"], key="live_source")
                with lc2:
                    default_count = 10
                    article_count = st.slider(tr('how_many'), 5, 50, default_count, key="live_count")
            
            st.markdown("<br>", unsafe_allow_html=True)
            fetch_btn = st.button(tr('show_news'), width="stretch")
        
        # --- Interest Filter ---
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(tr('filter_topic'))
            user_interests = st.multiselect(
                tr('filter_sub'),
                options=list(CATEGORY_THEMES.keys()),
                format_func=tr_cat,
                help=tr('filter_help'),
                key="user_interests_live"
            )

        if fetch_btn:
            source_map = {tr('google_news'): "google-rss", "NewsAPI": "newsapi"}
            selected_source = source_map[news_source]
            # API URL mapping
            api_url = f"http://localhost:8000/fetch-live-news"
            params = {
                "query": query if query else "latest",
                "page_size": article_count,
                "api_source": selected_source
            }
            
            with st.spinner(tr('fetching_msg').format(news_source)):
                try:
                    response = requests.get(api_url, params=params, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    st.session_state['live_results'] = data.get("articles", [])
                    # Invalidate PDF as data has changed
                    if 'live_pdf_bytes' in st.session_state: del st.session_state['live_pdf_bytes']
                except Exception as e:
                    st.error(f"Failed to fetch news: {str(e)}")

        # Display Logic (Works with session state to prevent lost data on UI interaction)
        if 'live_results' in st.session_state:
            results = st.session_state['live_results']
            
            # Apply Filter
            if user_interests:
                filtered_results = [a for a in results if a.get("category") in user_interests]
                display_msg = tr('recommended_msg').format(len(filtered_results), len(results))
            else:
                filtered_results = results
                display_msg = tr('latest_msg').format(len(results))

            if not filtered_results:
                st.info(tr('no_matches'))
            else:
                st.markdown(display_msg)
                
                for article in filtered_results:
                    h_text = article.get("headline", "Untitled")
                    d_text_clean = article.get("description", "") or ""
                    url = article.get("url", "#")
                    pub_date = article.get("publication_date", "")
                    cat = article.get("category", "General")
                    cat_icon = ICONS.get(cat, "🎭")
                    cat_theme = CATEGORY_THEMES.get(cat, {'color': '#3b82f6'})
                    
                    # Optimization: Always use Category Icon as the article picture
                    img_html = f'<div style="background: #111827; border: 1px solid {cat_theme["color"]}33; border-radius: 16px; width: 150px; height: 110px; display: flex; align-items: center; justify-content: center; font-size: 3.5rem; box-shadow: inset 0 0 30px {cat_theme["color"]}11;">{cat_icon}</div>'

                    # Date formatting
                    date_str = pub_date
                    try:
                        if "Z" in pub_date:
                            dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%SZ")
                            date_str = dt.strftime("%b %d, %Y - %H:%M")
                        elif "T" in pub_date:
                            dt = datetime.strptime(pub_date.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                            date_str = dt.strftime("%b %d, %Y - %H:%M")
                    except: pass

                    # Full Card using pure HTML with NO leading whitespace to avoid markdown parsing errors
                    card_html = f"""
<div style="display: flex; gap: 20px; align-items: flex-start;">
    <div style="flex: 0 0 150px;">
        {img_html}
    </div>
    <div style="flex: 1;">
        <div style="color: {cat_theme['color']}; font-weight: 800; font-size: 0.75rem; letter-spacing: 2px; margin-bottom: 8px;">
            {tr_cat(cat)} {cat_icon}
        </div>
        <div style="margin-bottom: 10px;">
            <a class="article-title-link" href="{url}" target="_blank" style="font-size: 1.3rem; line-height: 1.2;">{h_text}</a>
        </div>
        <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.5; margin-bottom: 15px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
            {d_text_clean}
        </p>
        <div style="color: #64748b; font-size: 0.8rem;">
            📡 {news_source} &nbsp;•&nbsp; 🗓️ {date_str}
        </div>
    </div>
</div>
"""
                    st.markdown(card_html, unsafe_allow_html=True)

                # --- Export Section for Live News ---
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(tr('export_work'))
                with st.container(border=True):
                    # Invalidate PDF if query or interests change
                    if st.session_state.get('last_live_pdf_query') != query or st.session_state.get('last_live_pdf_interests') != user_interests:
                        if 'live_pdf_bytes' in st.session_state: del st.session_state['live_pdf_bytes']

                    if st.button("🛠️ " + tr('btn_pdf'), key="live-gen-pdf", width="stretch"):
                        with st.spinner("Generating Report..."):
                            # Map results to a dataframe structure expected by the generator
                            live_df = pd.DataFrame([{
                                "Headline": a.get("headline", ""),
                                "Predicted Category": a.get("category", ""),
                                "URL": a.get("url", ""),
                            } for a in filtered_results])
                            
                            _meta = f"Signal: {query or 'latest'} | {news_source} | {datetime.now().strftime('%B %d, %Y')}"
                            generator = NewsReportGenerator(title="INTELLIGENCE REPORT", subtitle=_meta)
                            
                            final_pdf, _ = generator.generate_summary_report(live_df, "Headline", url_col="URL")
                            
                            st.session_state['live_pdf_bytes'] = bytes(final_pdf)
                            st.session_state['live_pdf_name'] = f"LiveNews_{query or 'latest'}_{datetime.now().strftime('%H%M%S')}.pdf"
                            st.session_state['last_live_pdf_query'] = query
                            st.session_state['last_live_pdf_interests'] = user_interests

                # --- Always Available Export Options ---
                if 'live_results' in st.session_state:
                    if 'live_pdf_bytes' in st.session_state:
                        st.download_button(
                            "✅ " + tr('btn_pdf'),
                            st.session_state['live_pdf_bytes'],
                            st.session_state['live_pdf_name'],
                            "application/pdf",
                            key='live-dl_pdf_btn',
                            width="stretch"
                        )

                    # CSV always available once fetched
                    live_csv_df = pd.DataFrame([{
                        "Headline": a.get("headline", ""),
                        "Category": a.get("category", ""),
                        "URL": a.get("url", ""),
                        "Published": a.get("publication_date", ""),
                        "Description": a.get("description", ""),
                    } for a in filtered_results])
                    st.download_button(
                        tr('btn_csv'),
                        live_csv_df.to_csv(index=False).encode('utf-8'),
                        f"LiveNews_{query or 'latest'}_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        key='live-dl-csv-btn',
                        width="stretch"
                    )

        # No more ghost alerts
        pass

# --- Page: About & FAQ ---
elif page == tr('nav_options')[1]:
    st.markdown(f"<h1 style='font-size: 3rem;'>{tr('about_title')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #94a3b8; font-size: 1.1rem;'>{tr('about_sub')}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown(tr('about_q1'))
            st.write(tr('about_a1'))
            
        with st.container(border=True):
            st.markdown(tr('about_q2'))
            st.write(tr('about_a2'))
            
    with col2:
        with st.container(border=True):
            st.markdown(tr('about_q3'))
            st.write(tr('about_a3'))
            
        with st.container(border=True):
            st.markdown(tr('about_q4'))
            st.write(tr('about_a4'))

    st.markdown("---")
    
    # 3. Interactive Text Scrubber
    st.markdown(tr('about_test'))
    st.write(tr('about_test_sub'))
    
    scrub_input = st.text_input(tr('about_test_input'), value=tr('about_test_val'))
    
    if scrub_input:
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown(f'<div class="radar-label">{tr("typed_label")}</div>', unsafe_allow_html=True)
            st.info(scrub_input)
        
        with sc2:
            st.markdown(f'<div class="radar-label">{tr("ai_view")}</div>', unsafe_allow_html=True)
            try:
                resp = requests.get(f"{API_BASE}/clean-text", params={"text": scrub_input})
                scrubbed = resp.json()['cleaned']
                st.success(f"`{scrubbed}`")
            except:
                st.error("Engine unavailable")
            st.caption(tr('ai_scrub_info'))

    st.markdown("---")
    st.caption(tr('built_for'))

# --- Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; padding: 30px 20px; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 40px;">
    <p style="color: #64748b; font-size: 0.85rem; margin-bottom: 5px;">{tr('footer_main')}</p>
    <p style="color: #475569; font-size: 0.75rem;">{tr('footer_sub')}</p>
</div>
""", unsafe_allow_html=True)