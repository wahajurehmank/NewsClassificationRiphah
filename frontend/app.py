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

# --- Shared Constants Injection ---
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
try:
    from constants import (
        MAPPING, ICONS, CATEGORY_THEMES, MASTER_CATEGORY_MAPPING, 
        STAKEHOLDER_INSIGHTS, FAMOUS_SOURCES_UI, STAKEHOLDER_INSIGHTS_UR
    )
except ImportError:
    # Fallback if constants.py is missing (should not happen in this task)
    MAPPING, ICONS, CATEGORY_THEMES = {}, {}, {}
    MASTER_CATEGORY_MAPPING, STAKEHOLDER_INSIGHTS = {}, {}
    FAMOUS_SOURCES_UI, STAKEHOLDER_INSIGHTS_UR = {}, {}

# --- Translation System ---
TRANSLATIONS = {
    'en': {
        'side_title': "🧠 Smart News Classifier",
        'nav_label': "NAVIGATION",
        'nav_options': ["🔍 Classify News", "❓ About & FAQ"],
        'status_label': "STATUS",
        'ai_ready': "✅ AI Engine: Ready",
        'sys_online': "🚀 All systems online",
        'built_for': "v0.3 • Built for everyone",
        'main_title': "Smart News Classifier",
        'main_sub': "Paste any news headline and our AI will tell you what category it belongs to — Sports, Tech, Crime, and more.",
        'tabs': ["🎯 Try It Out", "📦 Upload a File", "📡 Live News Feed"],
        'paste_title': "✍️ Paste Your News Article",
        'headline': "Headline",
        'headline_placeholder': "e.g. Tesla announces new self-driving update",
        'desc': "Description (optional)",
        'desc_placeholder': "Add more details for a better prediction...",
        'analyze_btn': "🔍 Classify This",
        'ai_confidence': "📊 AI Confidence",
        'radar_info': "Paste a headline and click **Classify This** to see results here.",
        'empty_warning': "Please enter a headline or description first.",
        'analyzing': "🧠 Our AI is reading your article...",
        'highly_confident': "Highly Confident",
        'likely_match': "Likely Match",
        'possible_match': "Possible Match",
        'confidence_err': "Confidence breakdown not available for this prediction.",
        'article_about': "YOUR ARTICLE IS ABOUT",
        'more_context': "### 📖 More Context",
        'fun_fact': "💡 Fun Fact",
        'why_ai': "🧪 Why the AI chose this?",
        'bulk_title': "### 📂 Classify Multiple Articles at Once",
        'bulk_sub': "Have a spreadsheet full of news? Upload it here and our AI will categorize every article automatically.",
        'upload_label': "Upload CSV/Excel",
        'upload_info': "Drag and drop your **.csv** or **.xlsx** file above to get started.",
        'upload_sub': "Your file should have at least two columns — one for headlines and one for descriptions.",
        'col_err': "⚠️ High Signal column (Headline/Title) not automatically detected. Please select it manually below.",
        'verify_cols': "📝 Verify Column Detection",
        'col_h': "Column for Headlines",
        'col_d': "Column for Descriptions",
        'classify_all': "🚀 Classify All Articles",
        'processing_bulk': "🧠 Reading and classifying your articles... this may take a moment.",
        'results_title': "### 📈 Your Results",
        'metric_classified': "Articles Classified",
        'metric_common': "Most Common Topic",
        'metric_topics': "Topics Found",
        'interesting_discoveries': "### 💡 Interesting Discoveries",
        'discovery_msg': "The most dominant topic in your file is **{}**!",
        'what_is_this': "❓ What is this?",
        'explore_data': "### 📝 Explore Your Processed Data",
        'export_work': "##### 📥 Export Your Processed Work",
        'btn_pdf': "📄 Download Summary Report (PDF)",
        'btn_csv': "📊 Download Classified Data (CSV)",
        'filter_report_cat': "Filter Report by Category",
        'all_cats': "All Categories",
        'include_full_text': "Deep Dive: Fetch Full Article Content (Requires URL)",
        'btn_deep_pdf': "📄 Download Deep Dive Report (PDF)",
        'fetching_articles': "🔍 Fetching full article contents... This may take a moment.",
        'scraping_err': "⚠️ Error fetching content for: {}",
        'no_url_warn': "⚠️ No URL column detected in CSV. Deep Dive is only available if a URL column exists.",
        'live_title': "Live News Feed",
        'live_sub': "Search for any topic and see the latest news articles, automatically categorized by our AI.",
        'live_input': "What news are you looking for?",
        'live_placeholder': "e.g. AI, Climate, Sports...",
        'adv_settings': "⚙️ Advanced Signal Settings",
        'news_provider': "News Source",
        'how_many': "How many stories?",
        'all_cats': "All Categories",
        'google_news': "Google News (RSS)",
        'show_news': "Show me the news",
        'filter_topic': "##### 🎯 Filter by Topic",
        'filter_sub': "Only show me articles about... (leave empty to see everything)",
        'filter_help': "Pick the topics you care about. We'll filter the rest out.",
        'fetching_msg': "🔍 Fetching the latest news from {}...",
        'recommended_msg': "#### 🎯 {} Recommended for You (Filtered from {})",
        'latest_msg': "#### 📰 Showing {} Latest Articles",
        'no_matches': "😕 None of the fetched articles match your selected topics. Try removing some filters or searching for something different.",
        'live_err': "⚠️ Could not load any news. Please make sure your {} API key is set up correctly in the settings.",
        'about_title': "About This Tool",
        'about_sub': "Everything you need to know about our Smart News Classifier.",
        'about_q1': "### ❓ What is this?",
        'about_a1': "This is an AI-powered tool that reads news headlines and automatically decides which category they belong to. It's designed to help you organize large amounts of news data or just explore what's happening in the world today.",
        'about_q2': "### 🎯 How accurate is it?",
        'about_a2': "Our AI (a Linear Support Vector Machine) is roughly **71% accurate**. While it's very good at spotting obvious patterns, it can sometimes get confused by clever headlines or news that fits into multiple categories.",
        'about_q3': "### 📂 Can I use my own files?",
        'about_a3': "Yes! In the **'Upload a File'** tab, you can drag in any Excel or CSV file. The tool will automatically find your headlines, categorize them, and give you a beautiful report to download.",
        'about_q4': "### 🌍 Where does live news come from?",
        'about_a4': "We connect to Google News RSS and NewsAPI to bring you real-time stories. You can search for anything from 'Global Warming' to 'Cricket' and our AI will filter the results based on your interests.",
        'about_test': "### 🔬 Test the AI Yourself",
        'about_test_sub': "Type any sentence below and watch how the AI cleans it up to understand the meaning.",
        'about_test_input': "Try typing a sentence",
        'about_test_val': "The S&P 500 reached an ALL-TIME high! #Economy #2026",
        'typed_label': "WHAT YOU TYPED",
        'ai_view': "HOW THE AI SEES IT",
        'ai_scrub_info': "The AI removes noise like symbols and numbers to focus on the keywords.",
        'footer_main': "Smart News Classifier • Built with Streamlit & Machine Learning",
        'footer_sub': "This tool uses AI to predict news categories. Results are automated and may not always be 100% accurate.",
        'error_prefix': "Error",
        'error_sys_offline': "System Core Offline",
        'categories': {
            'Crime': 'Crime', 'Culture': 'Culture', 'Education': 'Education', 'Family': 'Family',
            'Global News': 'Global News', 'Lifestyle': 'Lifestyle', 'Science & Tech': 'Science & Tech',
            'Society': 'Society', 'Sports': 'Sports', 'General': 'General', 'Insufficient Data': 'Insufficient Data'
        }
    },
    'ur': {
        'side_title': "🧠 سمارٹ نیوز کلاسیفائر",
        'nav_label': "نیویگیشن",
        'nav_options': ["🔍 خبروں کی درجہ بندی", "❓ بارے میں اور عمومی سوالات"],
        'status_label': "حالت",
        'ai_ready': "✅ اے آئی انجن: تیار ہے",
        'sys_online': "🚀 تمام سسٹم آن لائن ہیں",
        'built_for': "v0.3 • سب کے لیے بنایا گیا",
        'main_title': "سمارٹ نیوز کلاسیفائر",
        'main_sub': "نیوز کی کوئی بھی سرخی پیسٹ کریں اور ہماری اے آئی آپ کو بتائے گی کہ یہ کس زمرے سے تعلق رکھتی ہے — کھیل، ٹیک، جرم، اور بہت کچھ۔",
        'tabs': ["🎯 اسے آزمائیں", "📦 فائل اپ لوڈ کریں", "📡 لائیو نیوز فیڈ"],
        'paste_title': "✍️ اپنا نیوز آرٹیکل پیسٹ کریں",
        'headline': "سرخی",
        'headline_placeholder': "مثال کے طور پر: ٹیسلا نے خود سے چلنے والی نئی اپ ڈیٹ کا اعلان کیا",
        'desc': "تفصیل (اختیاری)",
        'desc_placeholder': "بہتر پیش گوئی کے لیے مزید تفصیلات شامل کریں...",
        'analyze_btn': "🔍 اس کی درجہ بندی کریں",
        'ai_confidence': "📊 اے آئی کا اعتماد",
        'radar_info': "سرخی پیسٹ کریں اور نتائج دیکھنے کے لیے 'اس کی درجہ بندی کریں' پر کلک کریں۔",
        'empty_warning': "براہ کرم پہلے سرخی یا تفصیل درج کریں۔",
        'analyzing': "🧠 ہماری اے آئی آپ کا مضمون پڑھ رہی ہے...",
        'highly_confident': "انتہائی پراعتماد",
        'likely_match': "ممکنہ میچ",
        'possible_match': "شاید میچ",
        'confidence_err': "اس پیش گوئی کے لیے اعتماد کی تفصیل دستیاب نہیں ہے۔",
        'article_about': "آپ کا مضمون اس بارے میں ہے",
        'more_context': "### 📖 مزید سیاق و سباق",
        'fun_fact': "💡 دلچسپ حقیقت",
        'why_ai': "🧪 اے آئی نے اس کا انتخاب کیوں کیا؟",
        'bulk_title': "### 📂 ایک ساتھ متعدد مضامین کی درجہ بندی کریں",
        'bulk_sub': "خبروں سے بھری اسپریڈ شیٹ ہے؟ اسے یہاں اپ لوڈ کریں اور ہمارا اے آئی ہر مضمون کو خود بخود زمرہ بندی کرے گا۔",
        'upload_label': "CSV/Excel اپ لوڈ کریں",
        'upload_info': "شروع کرنے کے لیے اپنی **.csv** یا **.xlsx** فائل اوپر ڈراپ کریں۔",
        'upload_sub': "آپ کی فائل میں کم از کم دو کالم ہونے چاہئیں — ایک سرخیوں کے لیے اور ایک تفصیل کے لیے۔",
        'col_err': "⚠️ ہائی سگنل کالم (سرخی/عنوان) خود بخود نہیں ملا۔ براہ کرم نیچے اسے دستی طور پر منتخب کریں۔",
        'verify_cols': "📝 کالم کی شناخت کی تصدیق کریں",
        'col_h': "سرخیوں کے لیے کالم",
        'col_d': "تفصیل کے لیے کالم",
        'classify_all': "🚀 تمام مضامین کی درجہ بندی کریں",
        'processing_bulk': "🧠 آپ کے مضامین کو پڑھا اور درجہ بندی کیا جا رہا ہے... اس میں تھوڑی دیر لگ سکتی ہے۔",
        'results_title': "### 📈 آپ کے نتائج",
        'metric_classified': "مضامین کی درجہ بندی کی گئی",
        'metric_common': "سب سے عام موضوع",
        'metric_topics': "ملنے والے موضوعات",
        'interesting_discoveries': "### 💡 دلچسپ دریافتیں",
        'discovery_msg': "آپ کی فائل میں سب سے زیادہ نمایاں موضوع **{}** ہے!",
        'what_is_this': "❓ یہ کیا ہے؟",
        'explore_data': "### 📝 اپنا پراسیس شدہ ڈیٹا دیکھیں",
        'export_work': "##### 📥 اپنا کام ایکسپورٹ کریں",
        'btn_pdf': "📄 خلاصہ رپورٹ ڈاؤن لوڈ کریں (PDF)",
        'btn_csv': "📊 درجہ بندی شدہ ڈیٹا ڈاؤن لوڈ کریں (CSV)",
        'filter_report_cat': "رپورٹ کو زمرے کے لحاظ سے فلٹر کریں",
        'all_cats': "تمام زمرے",
        'include_full_text': "ڈیپ ڈائیو: مضمون کا مکمل مواد حاصل کریں (URL درکار ہے)",
        'btn_deep_pdf': "📄 ڈیپ ڈائیو رپورٹ ڈاؤن لوڈ کریں (PDF)",
        'fetching_articles': "🔍 مضمون کا مکمل مواد حاصل کیا جا رہا ہے... اس میں تھوڑی دیر لگ سکتی ہے۔",
        'scraping_err': "⚠️ مواد حاصل کرنے میں خرابی: {}",
        'no_url_warn': "⚠️ CSV میں کوئی URL کالم نہیں ملا۔ ڈیپ ڈائیو صرف تب دستیاب ہے جب URL کالم موجود ہو۔",
        'live_title': "لائیو نیوز فیڈ",
        'live_sub': "کسی بھی موضوع کو تلاش کریں اور تازہ ترین خبریں دیکھیں، جو خود بخود ہمارے اے آئی کے ذریعہ درجہ بندی کی گئی ہیں۔",
        'live_input': "آپ کون سی خبریں تلاش کر رہے ہیں؟",
        'live_placeholder': "مثال کے طور پر: اے آئی، موسمیاتی تبدیلی، کھیل...",
        'adv_settings': "⚙️ ایڈوانس سیٹنگز",
        'news_provider': "نیوز فراہم کنندہ",
        'how_many': "کتنی کہانیاں؟",
        'show_news': "مجھے خبریں دکھائیں",
        'filter_topic': "##### 🎯 موضوع کے لحاظ سے فلٹر کریں",
        'filter_sub': "صرف ان کے بارے میں مضامین دکھائیں... (سب کچھ دیکھنے کے لیے اسے خالی چھوڑ دیں)",
        'filter_help': "وہ موضوعات منتخب کریں جن میں آپ کی دلچسپی ہے۔ ہم باقی کو فلٹر کر دیں گے۔",
        'fetching_msg': "🔍 {} سے تازہ ترین خبریں حاصل کی جا رہی ہیں...",
        'recommended_msg': "#### 🎯 {} آپ کے لیے تجویز کردہ (کل {} میں سے)",
        'latest_msg': "#### 📰 {} تازہ ترین مضامین دکھائے جا رہے ہیں",
        'no_matches': "😕 حاصل کردہ مضامین میں سے کوئی بھی آپ کے منتخب کردہ موضوعات سے مطابقت نہیں رکھتا۔ کچھ فلٹرز ہٹانے یا کچھ مختلف تلاش کرنے کی کوشش کریں۔",
        'live_err': "⚠️ کوئی خبر لوڈ نہیں ہو سکی۔ براہ کرم یقینی بنائیں کہ آپ کی {} API کلید درست طریقے سے سیٹ کی گئی ہے۔",
        'about_title': "اس ٹول کے بارے میں",
        'about_sub': "ہمارے سمارٹ نیوز کلاسیفائر کے بارے میں سب کچھ جو آپ کو جاننے کی ضرورت ہے۔",
        'about_q1': "### ❓ یہ کیا ہے؟",
        'about_a1': "یہ ایک اے آئی سے چلنے والا ٹول ہے جو خبروں کی سرخیوں کو پڑھتا ہے اور خود بخود فیصلہ کرتا ہے کہ وہ کس زمرے سے تعلق رکھتی ہیں۔ اسے آپ کو خبروں کے بڑے ڈیٹا کو ترتیب دینے یا آج کی دنیا میں کیا ہو رہا ہے اسے دریافت کرنے میں مدد کے لیے ڈیزائن کیا گیا ہے۔",
        'about_q2': "### 🎯 یہ کتنا درست ہے؟",
        'about_a2': "ہمارا اے آئی (ایک لکیری سپورٹ ویکٹر مشین) تقریباً **71% درست** ہے۔ اگرچہ یہ واضح نمونوں کو تلاش کرنے میں بہت اچھا ہے، لیکن یہ کبھی کبھی دلچسپ سرخیوں یا ایسی خبروں سے الجھ سکتا ہے جو ایک سے زیادہ زمروں میں فٹ بیٹھتی ہیں۔",
        'about_q3': "### 📂 کیا میں اپنی فائلیں استعمال کر سکتا ہوں؟",
        'about_a3': "جی ہاں! 'فائل اپ لوڈ کریں' ٹیب میں، آپ کسی بھی ایکسل یا CSV فائل کو لا سکتے ہیں۔ ٹول خود بخود آپ کی سرخیاں تلاش کرے گا، انہیں درجہ بندی کرے گا، اور آپ کو ڈاؤن لوڈ کرنے کے لیے ایک خوبصورت رپورٹ دے گا۔",
        'about_q4': "### 🌍 لائیو خبریں کہاں سے آتی ہیں؟",
        'about_a4': "ہم تازہ ترین خبریں لانے کے لیے گوگل نیوز آر ایس ایس (Google News RSS) اور نیوز اے پی آئی (NewsAPI) کا استعمال کرتے ہیں۔ آپ 'گلوبل وارمنگ' سے لے کر 'کرکٹ' تک کسی بھی چیز کو تلاش کر سکتے ہیں اور ہمارا اے آئی آپ کی دلچسپیوں کی بنیاد پر نتائج کو فلٹر کرے گا۔",
        'about_test': "### 🔬 اے آئی کو خود آزمائیں",
        'about_test_sub': "نیچے کوئی بھی جملہ ٹائپ کریں اور دیکھیں کہ اے آئی معنی سمجھنے کے لیے اسے کیسے صاف کرتا ہے۔",
        'about_test_input': "جملہ ٹائپ کرنے کی کوشش کریں",
        'about_test_val': "اسٹاک مارکیٹ میں آج زبردست تیزی دیکھی گئی! #معیشت #2026",
        'typed_label': "جو آپ نے ٹائپ کیا",
        'ai_view': "اے آئی اسے کیسے دیکھتا ہے",
        'ai_scrub_info': "اے آئی کی ورڈز پر توجہ مرکوز کرنے کے لیے نشانات اور نمبرز جیسے شور کو ہٹاتا ہے۔",
        'footer_main': "سمارٹ نیوز کلاسیفائر • اسٹریم لٹ اور مشین لرننگ کے ساتھ بنایا گیا",
        'footer_sub': "یہ ٹول خبروں کے زمرے کی پیش گوئی کرنے کے لیے اے آئی کا استعمال کرتا ہے۔ نتائج خودکار ہیں اور شاید ہمیشہ 100% درست نہ ہوں۔",
        'error_prefix': "خرابی",
        'error_sys_offline': "سسٹم کور آف لائن ہے",
        'categories': {
            'Crime': 'جرم', 'Culture': 'ثقافت', 'Education': 'تعلیم', 'Family': 'خاندان',
            'Global News': 'عالمی خبریں', 'Lifestyle': 'طرز زندگی', 'Science & Tech': 'سائنس اور ٹیکنالوجی',
            'Society': 'معاشرہ', 'Sports': 'کھیل', 'General': 'عام', 'Insufficient Data': 'ناکافی ڈیٹا'
        }
    }
}

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
            if content and len(content.strip()) > 100:
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
            if art.text and len(art.text.strip()) > 100:
                return art.text.strip()
        except Exception:
            pass

    return None

def create_pdf_report(df, h_col, filter_cat=None, deep_dive=False, url_col=None):
    import matplotlib.pyplot as plt
    import tempfile
    import os

    # Filter by category if requested
    if filter_cat and filter_cat != tr('all_cats'):
        df = df[df['Predicted Category'] == filter_cat].copy()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # --- Configuration ---
    primary_color = (15, 23, 42)    # Slate 900
    secondary_color = (59, 130, 246) # Blue 500
    accent_color = (16, 185, 129)   # Emerald 500
    text_muted = (100, 116, 139)    # Slate 500
    bg_light = (248, 250, 252)      # Slate 50
    effective_width = pdf.w - 2 * pdf.l_margin
    
    def safe_text(txt):
        if pd.isna(txt): return ""
        txt = str(txt)
        replacements = {
            "•": "-", "–": "-", "—": "-", 
            "“": "\"", "”": "\"", "‘": "'", "’": "'",
            "📈": "(+)", "💡": "!", "🎯": "*", "🌍": "",
            "🎭": "", "🎓": "", "👨‍👩‍👧‍👦": "", "🍕": "",
            "🔬": "", "🤝": "", "🏆": "", "⚖️": ""
        }
        for char, replacement in replacements.items():
            txt = txt.replace(char, replacement)
        # Attempt to clean up unicode that FPDF v1 latin-1 can't handle
        return txt.encode('latin-1', 'ignore').decode('latin-1')

    # --- Header Section ---
    pdf.set_fill_color(15, 23, 42) # Slate 900
    pdf.rect(0, 0, 210, 32, 'F')
    
    pdf.set_y(8)
    pdf.set_font("Helvetica", 'B', 24)
    pdf.set_text_color(255, 255, 255)
    report_title = "INTELLIGENCE BRIEFING" if not deep_dive else "DEEP DIVE AUDIT"
    pdf.cell(effective_width, 10, report_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    
    pdf.set_font("Helvetica", '', 9)
    pdf.set_text_color(148, 163, 184) # Slate 400
    _meta = f"Domain: {filter_cat if filter_cat else 'Comprehensive Analysis'} | {datetime.now().strftime('%B %d, %Y')}"
    pdf.cell(effective_width, 5, _meta, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    
    # Designer Accent Line
    pdf.set_fill_color(59, 130, 246) # Blue 500
    pdf.rect(pdf.l_margin, 26, 30, 1.2, 'F')

    if not deep_dive:
        # --- Summary Metrics Section ---
        pdf.set_y(40)
        counts = df['Predicted Category'].value_counts()
        if counts.empty:
            pdf.set_font("Helvetica", '', 12)
            pdf.cell(effective_width, 10, "No data available for analysis.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            return pdf.output()
        top_cat = counts.idxmax()

        # Summary Deck (Clean White Box)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(226, 232, 240) # Slate 200
        pdf.rect(pdf.l_margin, 38, effective_width, 24, 'DF')
        
        pdf.set_y(39)
        pdf.set_font("Helvetica", 'B', 8)
        pdf.set_text_color(100, 116, 139) # Slate 500
        pdf.cell(effective_width/3, 8, " ARTICLES", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        pdf.cell(effective_width/3, 8, " DOMINANT", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        pdf.cell(effective_width/3, 8, " RELIABILITY", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        pdf.set_font("Helvetica", 'B', 15)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(effective_width/3, 7, str(len(df)), 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        pdf.set_text_color(59, 130, 246)
        pdf.cell(effective_width/3, 7, safe_text(top_cat).upper(), 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        pdf.set_text_color(16, 185, 129) # Emerald
        pdf.cell(effective_width/3, 7, "71.4% CONF", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        pdf.ln(12)

        # --- Classification Index (The Table) ---
        pdf.set_font("Helvetica", 'B', 14)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(effective_width, 10, "Classification Matrix", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)
        
        # Table Header
        pdf.set_font("Helvetica", 'B', 9)
        pdf.set_fill_color(15, 23, 42)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(effective_width * 0.55, 11, "  ARTICLE HEADLINE", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='L', fill=True)
        pdf.cell(effective_width * 0.25, 11, "PREDICTED TOPIC", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C', fill=True)
        pdf.cell(effective_width * 0.20, 11, "SOURCE  ", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R', fill=True)
        
        # Table Rows
        pdf.set_font("Helvetica", '', 9)
        pdf.set_text_color(15, 23, 42)
        for count, (i, row) in enumerate(df.iterrows()):
            if count >= 300: break # Safety limit
            
            safe_h = safe_text(row[h_col])
            if len(safe_h) > 65: safe_h = safe_h[:62] + "..."
            
            _url = row[url_col] if (url_col and url_col in row and not pd.isna(row[url_col]) and str(row[url_col]).strip()) else None
            
            fill = (count % 2 == 1)
            pdf.set_fill_color(248, 250, 251) if fill else pdf.set_fill_color(255, 255, 255)
            
            # Row Start
            pdf.cell(effective_width * 0.55, 9, f"  {safe_h}", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='L', fill=True)
            
            # Topic Tag
            pdf.set_font("Helvetica", 'B', 8)
            pdf.cell(effective_width * 0.25, 9, safe_text(row['Predicted Category']).upper(), 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C', fill=True)
            
            # Link Column
            pdf.set_font("Helvetica", 'U', 8)
            pdf.set_text_color(59, 130, 246)
            pdf.cell(effective_width * 0.20, 9, "Read Story >>  ", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R', fill=True, link=_url)
            
            # Reset for next row
            pdf.set_font("Helvetica", '', 9)
            pdf.set_text_color(15, 23, 42)
    else:
        # DEEP DIVE REPORT - One Full Page per Article
        pdf.set_y(60)
        pdf.set_font("Helvetica", 'I', 11)
        pdf.set_text_color(*text_muted)
        pdf.multi_cell(effective_width, 6, "This report contains full article content analysis for the selected dataset. Full text is retrieved in real-time where available.", align='C')
        
        # Limit to 50 articles max, then pre-fetch ALL URLs in parallel
        process_df = df.head(50)
        
        # --- Step 1: Parallel fetch (much faster than sequential) ---
        from concurrent.futures import ThreadPoolExecutor, as_completed
        url_list = []
        for _, row in process_df.iterrows():
            if url_col and url_col in row and not pd.isna(row[url_col]):
                url_list.append(row[url_col])
            else:
                url_list.append(None)

        full_texts = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_url = {executor.submit(fetch_full_content, u): u for u in url_list if u}
            for future in as_completed(future_to_url):
                u = future_to_url[future]
                try:
                    full_texts[u] = future.result()
                except Exception:
                    full_texts[u] = None

        # --- Step 2: Build PDF using pre-fetched content ---
        articles_included = 0
        for i, row in process_df.iterrows():
            row_url = row[url_col] if (url_col and url_col in row and not pd.isna(row[url_col])) else None
            full_text = full_texts.get(row_url) if row_url else None
            
            # SKIP articles that failed to fetch or have no content
            if not full_text or len(str(full_text).strip()) < 100:
                continue

            articles_included += 1
            pdf.add_page()
            
            # Category Header
            cat_name = row['Predicted Category']
            pdf.set_font("Helvetica", 'B', 10)
            pdf.set_text_color(*secondary_color)
            pdf.cell(effective_width, 10, f"{safe_text(cat_name).upper()} INTELLIGENCE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Headline
            pdf.set_font("Helvetica", 'B', 18)
            pdf.set_text_color(*primary_color)
            pdf.multi_cell(effective_width, 9, safe_text(row[h_col]))
            pdf.ln(5)
            
            # URL Link
            if row_url:
                pdf.set_font("Helvetica", 'U', 10)
                pdf.set_text_color(*secondary_color)
                pdf.cell(effective_width, 8, "View Original Article", link=row_url, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(5)
                
            pdf.set_font("Helvetica", 'B', 12)
            pdf.set_text_color(*primary_color)
            pdf.cell(effective_width, 10, "Full Content Analysis:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", '', 10)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(effective_width, 6, safe_text(full_text[:5000]))

        if articles_included == 0:
            pdf.ln(20)
            pdf.set_font("Helvetica", 'I', 12)
            pdf.set_text_color(*text_muted)
            pdf.multi_cell(effective_width, 10, "No articles could be retrieved for detailed analysis. Please verify your source URLs and network connection.", align='C')

    pdf.set_y(-20)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.set_text_color(*text_muted)
    pdf.cell(effective_width, 10, "News Intelligence Analysis | Generated by AI Core", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    
    return pdf.output()

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
                        resp = requests.post(f"{API_BASE}/predict", json={"headline": headline, "description": description})
                        resp.raise_for_status()
                        data = resp.json()
                        category = data['category']
                        top_3_data = data['top_3']
                        
                        icon = ICONS.get(category, "🎭")
                        theme = CATEGORY_THEMES.get(category, {'color': '#3b82f6', 'glow': 'rgba(255,255,255,0.2)'})
                        
                        with radar_container.container():
                            st.markdown("<br>", unsafe_allow_html=True)
                            for item in top_3_data:
                                c_name = item['category']
                                c_val = item['confidence']
                                
                                # Friendly Labels for Confidence
                                if c_val > 0.8: label = tr('highly_confident')
                                elif c_val > 0.5: label = tr('likely_match')
                                else: label = tr('possible_match')
                                
                                st.markdown(f'<div class="radar-label">{tr_cat(c_name)} — {label}</div>', unsafe_allow_html=True)
                                st.progress(float(c_val))
                    except:
                        radar_container.warning(tr('confidence_err'))

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
                    with st.spinner(tr('processing_bulk')):
                        # 1. Collect texts for API
                        df['combined_text'] = (df[h_col].fillna('') + " " + df[d_col].fillna(''))
                        
                        # 2. Call Backend API
                        try:
                            resp = requests.post(f"{API_BASE}/bulk-predict", json={"texts": df['combined_text'].tolist()})
                            resp.raise_for_status()
                            df['Predicted Category'] = resp.json()['predictions']
                            
                            # Store in session state for persistence
                            st.session_state['bulk_results'] = df
                            st.session_state['bulk_h_col'] = h_col
                            st.session_state['bulk_u_col'] = u_col if u_col != "None" else None
                        except Exception as e:
                            st.error(f"Bulk analysis failed: {e}")

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
                        with e_col1:
                            # Get unique categories and sort them
                            raw_cats = res_df['Predicted Category'].unique().tolist()
                            available_cats = [tr('all_cats')] + sorted([str(c) for c in raw_cats])
                            report_filter = st.selectbox(tr('filter_report_cat'), available_cats, key='bulk_filter_sel')
                            
                        with e_col2:
                            u_col_final = st.session_state.get('bulk_u_col')
                            is_deep = st.checkbox(tr('include_full_text'), disabled=(u_col_final is None), key='bulk_deep_chk')
                            if u_col_final is None:
                                st.caption(tr('no_url_warn'))

                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Use a trigger to generate the PDF
                        if st.button("🛠️ " + tr('btn_pdf'), width="stretch", key='bulk_gen_pdf_btn'):
                            # Filter preview
                            f_df = res_df.copy()
                            if report_filter != tr('all_cats'):
                                f_df = f_df[f_df['Predicted Category'] == report_filter]
                            
                            limit_info = ""
                            if is_deep and len(f_df) > 50:
                                limit_info = " (Limited to first 50 articles)"
                                
                            with st.spinner(f"{tr('fetching_articles')}{limit_info}" if is_deep else "Generating Report..."):
                                report_bytes = create_pdf_report(res_df, res_h_col, filter_cat=report_filter, deep_dive=is_deep, url_col=u_col_final)
                                st.session_state['last_pdf_bytes'] = bytes(report_bytes)
                                st.session_state['last_pdf_name'] = f"Report_{report_filter}_{datetime.now().strftime('%H%M%S')}.pdf"

                        if 'last_pdf_bytes' in st.session_state:
                            st.download_button(
                                "✅ " + tr('btn_pdf'),
                                st.session_state['last_pdf_bytes'],
                                st.session_state['last_pdf_name'],
                                "application/pdf",
                                width="stretch",
                                key='bulk_dl_pdf_btn'
                            )
                            
                        # CSV Export (Always available and fast)
                        csv_filter_df = res_df.copy()
                        if report_filter != tr('all_cats'):
                            csv_filter_df = csv_filter_df[csv_filter_df['Predicted Category'] == report_filter]
                        
                        st.download_button(
                            tr('btn_csv'),
                            csv_filter_df.to_csv(index=False).encode('utf-8'),
                            f"Data_{report_filter}_{datetime.now().strftime('%Y%m%d')}.csv",
                            "text/csv",
                            key='bulk-csv-download-btn',
                            width="stretch"
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
                    response = requests.get(api_url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    st.session_state['last_news_results'] = data.get("articles", [])
                except Exception as e:
                    st.error(f"Failed to fetch news: {str(e)}")

        # Display Logic (Works with session state to prevent lost data on UI interaction)
        if 'last_news_results' in st.session_state:
            results = st.session_state['last_news_results']
            
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
                    if st.button("🛠️ " + tr('btn_pdf'), key="live-gen-pdf", width="stretch"):
                        with st.spinner("Generating Report..."):
                            # Build a simple PDF from the live results
                            _pdf = FPDF()
                            _pdf.set_auto_page_break(auto=True, margin=15)
                            _pdf.add_page()
                            _ew = _pdf.w - 2 * _pdf.l_margin
                            def _safe(t):
                                return str(t).encode('latin-1', 'ignore').decode('latin-1')

                            # Header
                            _pdf.set_fill_color(15, 23, 42) # Slate 900
                            _pdf.rect(0, 0, 210, 32, 'F')
                            _pdf.set_y(8)
                            _pdf.set_font("Helvetica", 'B', 24)
                            _pdf.set_text_color(255, 255, 255)
                            _pdf.cell(_ew, 10, "INTELLIGENCE REPORT", ln=True, align='L')
                            _pdf.set_font("Helvetica", '', 9)
                            _pdf.set_text_color(148, 163, 184) # Slate 400
                            _meta = f"Signal: {query or 'latest'} | {news_source} | {datetime.now().strftime('%B %d, %Y')}"
                            _pdf.cell(_ew, 5, _meta, ln=True, align='L')
                            
                            # Designer Accent Line
                            _pdf.set_fill_color(59, 130, 246) # Blue 500
                            _pdf.rect(_pdf.l_margin, 26, 30, 1.2, 'F')

                            # Summary metrics card (Move up)
                            cats = {}
                            for a in filtered_results:
                                c = a.get("category", "General")
                                cats[c] = cats.get(c, 0) + 1
                            top_cat = max(cats, key=cats.get) if cats else "N/A"

                            _pdf.set_y(40)
                            _pdf.set_fill_color(255, 255, 255)
                            _pdf.set_draw_color(226, 232, 240) # Slate 200
                            _pdf.rect(_pdf.l_margin, 38, _ew, 24, 'DF')
                            
                            _pdf.set_y(39)
                            _pdf.set_font("Helvetica", 'B', 8)
                            _pdf.set_text_color(100, 116, 139) # Slate 500
                            _pdf.cell(_ew/3, 8, " ARTICLES", 0, 0, 'C')
                            _pdf.cell(_ew/3, 8, " DOMINANT", 0, 0, 'C')
                            _pdf.cell(_ew/3, 8, " TOPICS", 0, 1, 'C')
                            
                            _pdf.set_font("Helvetica", 'B', 15)
                            _pdf.set_text_color(15, 23, 42)
                            _pdf.cell(_ew/3, 7, str(len(filtered_results)), 0, 0, 'C')
                            _pdf.set_text_color(16, 185, 129) # Emerald
                            _pdf.cell(_ew/3, 7, _safe(top_cat).upper(), 0, 0, 'C')
                            _pdf.set_text_color(59, 130, 246)
                            _pdf.cell(_ew/3, 7, str(len(cats)), 0, 1, 'C')

                            # Article index (No add_page - start on page 1)
                            _pdf.ln(12)
                            _pdf.set_font("Helvetica", 'B', 13)
                            _pdf.set_text_color(15, 23, 42)
                            _pdf.cell(_ew, 10, "Classification Matrix", ln=True)
                            _pdf.ln(1)
                            
                            # Table Header
                            _pdf.set_font("Helvetica", 'B', 9)
                            _pdf.set_fill_color(15, 23, 42)
                            _pdf.set_text_color(255, 255, 255)
                            _pdf.cell(_ew * 0.55, 10, "  ARTICLE HEADLINE", 0, 0, 'L', True)
                            _pdf.cell(_ew * 0.25, 10, "PREDICTED TOPIC", 0, 0, 'C', True)
                            _pdf.cell(_ew * 0.20, 10, "SOURCE  ", 0, 1, 'R', True)
                            
                            _pdf.set_font("Helvetica", '', 9)
                            _pdf.set_text_color(15, 23, 42)
                            for _idx, _art in enumerate(filtered_results):
                                if _idx >= 300: break # Increased limit
                                _h = _safe(_art.get("headline", "Untitled"))
                                if len(_h) > 65: _h = _h[:62] + "..."
                                _cat_t = _safe(_art.get("category", "")).upper()
                                _url = _art.get("url") if _art.get("url") and str(_art.get("url")).strip() != "#" else None
                                
                                _fill = (_idx % 2 == 1)
                                _pdf.set_fill_color(248, 250, 251) if _fill else _pdf.set_fill_color(255, 255, 255)
                                
                                # Row Start
                                _pdf.cell(_ew * 0.55, 9, f"  {_h}", 0, 0, 'L', True)
                                
                                # Topic Tag
                                _pdf.set_font("Helvetica", 'B', 8)
                                _pdf.cell(_ew * 0.25, 9, _cat_t, 0, 0, 'C', True)
                                
                                # Link Column
                                _pdf.set_font("Helvetica", 'U', 8)
                                _pdf.set_text_color(59, 130, 246)
                                _pdf.cell(_ew * 0.20, 9, "Read Story >>  ", 0, 1, 'R', True, link=_url)
                                
                                # Reset for next row
                                _pdf.set_font("Helvetica", '', 9)
                                _pdf.set_text_color(15, 23, 42)

                            _pdf.set_y(-20)
                            _pdf.set_font("Helvetica", 'I', 8)
                            _pdf.set_text_color(100, 116, 139)
                            _pdf.cell(_ew, 10, "News Intelligence Analysis | Generated by AI Core", 0, 0, 'C')

                            final_pdf = _pdf.output()
                            st.session_state['live_pdf_bytes'] = bytes(final_pdf)
                            st.session_state['live_pdf_name'] = f"LiveNews_{query or 'latest'}_{datetime.now().strftime('%H%M%S')}.pdf"

                # --- Always Available Export Options ---
                if 'last_news_results' in st.session_state:
                    if 'live_pdf_bytes' in st.session_state:
                        st.download_button(
                            "✅ " + tr('btn_pdf'),
                            st.session_state['live_pdf_bytes'],
                            st.session_state['live_pdf_name'],
                            "application/pdf",
                            key='live-dl-pdf-btn',
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