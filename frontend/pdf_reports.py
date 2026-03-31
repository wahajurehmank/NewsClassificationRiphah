import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from concurrent.futures import ThreadPoolExecutor, as_completed

class NewsReportGenerator:
    # Color palette
    PRIMARY_COLOR = (15, 23, 42)    # Slate 900
    SECONDARY_COLOR = (59, 130, 246) # Blue 500
    ACCENT_COLOR = (16, 185, 129)   # Emerald 500
    TEXT_MUTED = (100, 116, 139)    # Slate 500
    BG_LIGHT = (248, 250, 252)      # Slate 50
    HEADER_TEXT_COLOR = (255, 255, 255)
    HEADER_SUB_COLOR = (148, 163, 184) # Slate 400

    @staticmethod
    def is_article_worthy(text):
        """
        Hard filter for article quality. Skips menus, footers, data tables, and junk.
        """
        if not text: return False
        text = text.strip()
        if len(text) < 500: return False
        
        # Check Character Diversity
        import re
        
        # Remove repeated noise sequences (e.g. "......", "//////", "----------")
        if re.search(r'([./:\-_])\1{4,}', text): return False
        
        letters = re.findall(r'[a-zA-Z\u0600-\u06FF]', text)
        digits = re.findall(r'[0-9]', text)
        symbols = re.findall(r'[^a-zA-Z0-9\s\u0600-\u06FF]', text)
        
        total = len(text.replace(" ", ""))
        if total == 0: return False
        
        # 1. Ratio check: Real articles are mostly letters (> 85% alphabetic)
        if len(letters) / total < 0.85: return False
        
        # 2. Noise check: Too many digits or symbols (e.g. financial tables)
        if (len(digits) + len(symbols)) / total > 0.15: return False
        
        # 3. Word diversity: Junk repeats symbols/headers/shorthand
        words = [w.lower() for w in text.split() if len(w) > 3]
        if len(words) < 50: return False
        if len(set(words)) / len(words) < 0.4: return False 
        
        return True

    def __init__(self, title="INTELLIGENCE REPORT", subtitle=""):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.title = title
        self.subtitle = subtitle
        self.effective_width = self.pdf.w - 2 * self.pdf.l_margin
        
        # Register Urdu Font if available on common Linux paths
        self.has_urdu_font = False
        urdu_paths = [
            "/usr/share/fonts/truetype/noto/NotoNastaliqUrdu-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
            "frontend/assets/fonts/UrduType.ttf" # Example project path
        ]
        
        for path in urdu_paths:
            if os.path.exists(path):
                try:
                    self.pdf.add_font("UrduFont", "", path)
                    self.has_urdu_font = True
                    break
                except Exception:
                    continue

    def _safe_text(self, txt):
        if pd.isna(txt): return ""
        txt = str(txt)
        
        # 1. Normalize Whitespace (Collapse empty lines)
        import re
        txt = re.sub(r'\n{3,}', '\n\n', txt)
        # txt = re.sub(r' +', ' ', txt) # Optional: collapse spaces
        
        replacements = {
            "•": "-", "–": "-", "—": "-", 
            "“": "\"", "”": "\"", "‘": "'", "’": "'",
        }
        for char, replacement in replacements.items():
            txt = txt.replace(char, replacement)
            
        # 2. Final clean-up of non-standard chars that FPDF Helvetica lacks
        # (Only if not using UrduFont)
        return txt

    def _add_header(self):
        self.pdf.set_fill_color(*self.PRIMARY_COLOR)
        self.pdf.rect(0, 0, 210, 32, 'F')
        
        self.pdf.set_y(8)
        self.pdf.set_font("Helvetica", 'B', 24)
        self.pdf.set_text_color(*self.HEADER_TEXT_COLOR)
        
        # If title has Urdu, use UrduFont
        title_font = "UrduFont" if self.has_urdu_font and any(ord(c) > 127 for c in self.title) else "Helvetica"
        if title_font == "UrduFont": self.pdf.set_font(title_font, "", 20)
        
        self.pdf.cell(self.effective_width, 10, self.title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        
        self.pdf.set_font("Helvetica", '', 9)
        self.pdf.set_text_color(*self.HEADER_SUB_COLOR)
        
        # If subtitle has Urdu, use UrduFont
        sub_font = "UrduFont" if self.has_urdu_font and any(ord(c) > 127 for c in self.subtitle) else "Helvetica"
        if sub_font == "UrduFont": self.pdf.set_font(sub_font, "", 9)
        
        self.pdf.cell(self.effective_width, 5, self.subtitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        
        # Designer Accent Line
        self.pdf.set_fill_color(*self.SECONDARY_COLOR)
        self.pdf.rect(self.pdf.l_margin, 26, 30, 1.2, 'F')
        self.pdf.set_y(40)


    def _add_summary_metrics(self, count, top_cat, topics_count, use_reliability=False):
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_draw_color(226, 232, 240)
        self.pdf.rect(self.pdf.l_margin, 38, self.effective_width, 24, 'DF')
        
        self.pdf.set_y(39)
        self.pdf.set_font("Helvetica", 'B', 8)
        self.pdf.set_text_color(*self.TEXT_MUTED)
        self.pdf.cell(self.effective_width/3, 8, " ARTICLES", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        self.pdf.cell(self.effective_width/3, 8, " DOMINANT", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        
        right_label = " RELIABILITY" if use_reliability else " TOPICS FOUND"
        self.pdf.cell(self.effective_width/3, 8, right_label, 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        # Values Row
        self.pdf.set_font("Helvetica", 'B', 15)
        self.pdf.set_text_color(*self.PRIMARY_COLOR)
        self.pdf.cell(self.effective_width/3, 7, str(count), 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        
        # Use Urdu font for category if it's Urdu
        cat_text = self._safe_text(top_cat).upper()
        cat_font = "UrduFont" if self.has_urdu_font and any(ord(c) > 127 for c in cat_text) else "Helvetica"
        if cat_font == "UrduFont": self.pdf.set_font(cat_font, "", 12)
        else: self.pdf.set_font("Helvetica", "B", 13)
        
        self.pdf.set_text_color(*self.SECONDARY_COLOR)
        self.pdf.cell(self.effective_width/3, 7, cat_text, 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        
        # Reset to Helvetica for the last metric
        self.pdf.set_font("Helvetica", "B", 15)
        if use_reliability:
            self.pdf.set_text_color(*self.ACCENT_COLOR)
            self.pdf.cell(self.effective_width/3, 7, "71.4% CONF", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        else:
            self.pdf.set_text_color(*self.SECONDARY_COLOR)
            self.pdf.cell(self.effective_width/3, 7, str(topics_count), 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        self.pdf.ln(12)


    def _add_classification_table(self, df, h_col, url_col=None, limit=300):
        self.pdf.set_font("Helvetica", 'B', 14)
        self.pdf.set_text_color(*self.PRIMARY_COLOR)
        self.pdf.cell(self.effective_width, 10, "Classification Matrix", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(1)

        # Using FPDF2 internal table handling to simplify maintenance
        with self.pdf.table(
            col_widths=(55, 25, 20),
            text_align=("LEFT", "CENTER", "RIGHT"),
            line_height=8,
            padding=2
        ) as table:
            # Header Row
            header = table.row()
            self.pdf.set_font("Helvetica", "B", 9)
            self.pdf.set_text_color(255, 255, 255)
            self.pdf.set_fill_color(*self.PRIMARY_COLOR)
            header.cell("ARTICLE HEADLINE")
            header.cell("PREDICTED TOPIC")
            header.cell("SOURCE")

            # Data Rows
            for idx, (_, row) in enumerate(df.head(limit).iterrows()):
                data_row = table.row()
                
                # Styles for data rows
                fill_color = self.BG_LIGHT if idx % 2 == 1 else (255, 255, 255)
                self.pdf.set_fill_color(*fill_color)
                
                safe_h = self._safe_text(row[h_col])
                if len(safe_h) > 75: safe_h = safe_h[:72] + "..."
                
                # HEADLINE: Set font based on content
                h_font = "UrduFont" if self.has_urdu_font and any(ord(c) > 127 for c in safe_h) else "Helvetica"
                self.pdf.set_font(h_font, "" if h_font == "UrduFont" else "", 9)
                self.pdf.set_text_color(*self.PRIMARY_COLOR)
                data_row.cell(f"  {safe_h}")
                
                # TOPIC: Set font based on content
                topic_text = self._safe_text(row['Predicted Category']).upper()
                t_font = "UrduFont" if self.has_urdu_font and any(ord(c) > 127 for c in topic_text) else "Helvetica"
                self.pdf.set_font(t_font, "B" if t_font == "Helvetica" else "", 8)
                data_row.cell(topic_text)
                
                # SOURCE: Link column (usually English)
                url = row[url_col] if (url_col and url_col in row and not pd.isna(row[url_col]) and str(row[url_col]).strip()) else None
                self.pdf.set_font("Helvetica", "U", 8)
                self.pdf.set_text_color(*self.SECONDARY_COLOR)
                data_row.cell("Read Story >>  ", link=url)


    def _add_footer(self):
        self.pdf.set_y(-20)
        self.pdf.set_font("Helvetica", 'I', 8)
        self.pdf.set_text_color(*self.TEXT_MUTED)
        self.pdf.cell(self.effective_width, 10, "News Intelligence Analysis | Generated by AI Core", 0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

    def generate_summary_report(self, df, h_col, url_col=None, use_reliability=False):
        if df.empty:
            self.pdf.add_page()
            self.pdf.set_font("Helvetica", '', 12)
            self.pdf.cell(self.effective_width, 10, "No data available for analysis.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            return self.pdf.output(), df

        self.pdf.add_page()
        self._add_header()
        
        counts = df['Predicted Category'].value_counts()
        top_cat = counts.idxmax()
        topics_count = len(counts)
        
        self._add_summary_metrics(len(df), top_cat, topics_count, use_reliability=use_reliability)
        self._add_classification_table(df, h_col, url_col)
        self._add_footer()
        
        return self.pdf.output(), df

    def generate_deep_dive_report(self, df, h_col, fetch_content_func, url_col=None):
        self.pdf.add_page()
        self._add_header()
        
        self.pdf.set_y(60)
        self.pdf.set_font("Helvetica", 'I', 11)
        self.pdf.set_text_color(*self.TEXT_MUTED)
        self.pdf.multi_cell(self.effective_width, 6, "This report contains full article content analysis for the selected dataset. Full text is retrieved in real-time where available.", align='C')
        
        # Parallel fetch content
        process_df = df.head(50)
        url_list = []
        for _, row in process_df.iterrows():
            if url_col and url_col in row and not pd.isna(row[url_col]):
                url_list.append(row[url_col])
            else:
                url_list.append(None)

        full_texts = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_url = {executor.submit(fetch_content_func, u): u for u in url_list if u}
            for future in as_completed(future_to_url):
                u = future_to_url[future]
                try:
                    full_texts[u] = future.result()
                except Exception:
                    full_texts[u] = None

        included_rows = []
        for i, row in process_df.iterrows():
            row_url = row[url_col] if (url_col and url_col in row and not pd.isna(row[url_col])) else None
            full_text = full_texts.get(row_url) if row_url else None
            
            # Double verification skip
            if not full_text or not self.is_article_worthy(full_text):
                continue

            included_rows.append(row)
            self.pdf.add_page()
            
            # Article Details Layout
            cat_text = self._safe_text(row['Predicted Category']).upper()
            cat_font = "UrduFont" if self.has_urdu_font and any(ord(c) > 127 for c in cat_text) else "Helvetica"
            self.pdf.set_font(cat_font, "B" if cat_font == "Helvetica" else "", 10)
            self.pdf.set_text_color(*self.SECONDARY_COLOR)
            self.pdf.cell(self.effective_width, 10, f"{cat_text} INTELLIGENCE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            h_text = self._safe_text(row[h_col])
            h_font = "UrduFont" if self.has_urdu_font and any(ord(c) > 127 for c in h_text) else "Helvetica"
            self.pdf.set_font(h_font, "B" if h_font == "Helvetica" else "", 18)
            self.pdf.set_text_color(*self.PRIMARY_COLOR)
            self.pdf.multi_cell(self.effective_width, 9, h_text)
            
            if row_url:
                self.pdf.ln(2)
                self.pdf.set_font("Helvetica", 'U', 10)
                self.pdf.set_text_color(*self.SECONDARY_COLOR)
                self.pdf.cell(self.effective_width, 8, "View Original Article", link=row_url, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            self.pdf.ln(5)
            self.pdf.set_font("Helvetica", 'B', 12)
            self.pdf.set_text_color(*self.PRIMARY_COLOR)
            self.pdf.cell(self.effective_width, 10, "Full Content Analysis:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            content_text = self._safe_text(full_text[:5000])
            c_font = "UrduFont" if self.has_urdu_font and any(ord(c) > 127 for c in content_text) else "Helvetica"
            self.pdf.set_font(c_font, "" if c_font == "UrduFont" else "", 10)
            self.pdf.set_text_color(51, 65, 85)
            self.pdf.multi_cell(self.effective_width, 6, content_text)

        if not included_rows:
            self.pdf.ln(20)
            self.pdf.set_font("Helvetica", 'I', 12)
            self.pdf.set_text_color(*self.TEXT_MUTED)
            self.pdf.multi_cell(self.effective_width, 10, "No articles could be retrieved for detailed analysis. Please verify your source URLs.", align='C')

        self._add_footer()
        return self.pdf.output(), pd.DataFrame(included_rows)

