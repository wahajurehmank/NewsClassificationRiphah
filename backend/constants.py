# --- Shared Project Constants ---

MAPPING = {
    0: 'Crime', 
    1: 'Culture', 
    2: 'Education', 
    3: 'Family',
    4: 'Global News', 
    5: 'Lifestyle', 
    6: 'Science & Tech', 
    7: 'Society', 
    8: 'Sports',
    9: 'General',
    10: 'Insufficient Data'
}

ICONS = {
    'Crime': "⚖️", 'Culture': "🎭", 'Education': "🎓", 'Family': "👨‍👩‍👧‍👦",
    'Global News': "🌍", 'Lifestyle': "🍕", 'Science & Tech': "🔬",
    'Society': "🤝", 'Sports': "🏆", 'General': "🎭", 'Insufficient Data': "❓"
}

CATEGORY_THEMES = {
    'Crime': {'color': '#ef4444', 'glow': 'rgba(239, 68, 68, 0.5)'},
    'Culture': {'color': '#8b5cf6', 'glow': 'rgba(139, 92, 246, 0.5)'},
    'Education': {'color': '#f59e0b', 'glow': 'rgba(245, 158, 11, 0.5)'},
    'Family': {'color': '#ec4899', 'glow': 'rgba(236, 72, 153, 0.5)'},
    'Global News': {'color': '#3b82f6', 'glow': 'rgba(59, 130, 246, 0.5)'},
    'Lifestyle': {'color': '#84cc16', 'glow': 'rgba(132, 204, 22, 0.5)'},
    'Science & Tech': {'color': '#06b6d4', 'glow': 'rgba(6, 182, 212, 0.5)'},
    'Society': {'color': '#6366f1', 'glow': 'rgba(99, 102, 241, 0.5)'},
    'Sports': {'color': '#f97316', 'glow': 'rgba(249, 115, 22, 0.5)'},
    'General': {'color': '#94a3b8', 'glow': 'rgba(148, 163, 184, 0.5)'},
    'Insufficient Data': {'color': '#64748b', 'glow': 'rgba(100, 116, 139, 0.5)'}
}

# --- Master Taxonomy Mapping ---
MASTER_CATEGORY_MAPPING = {
    'POLITICS': 'Global News', 'WORLD NEWS': 'Global News',
    'WORLDPOST': 'Global News', 'THE WORLDPOST': 'Global News',
    'U.S. NEWS': 'Global News',
    'WELLNESS': 'Lifestyle', 'HEALTHY LIVING': 'Lifestyle',
    'STYLE & BEAUTY': 'Lifestyle', 'STYLE': 'Lifestyle',
    'FOOD & DRINK': 'Lifestyle', 'TASTE': 'Lifestyle',
    'TRAVEL': 'Lifestyle', 'HOME & LIVING': 'Lifestyle',
    'QUEER VOICES': 'Society', 'BLACK VOICES': 'Society',
    'LATINO VOICES': 'Society', 'WOMEN': 'Society',
    'RELIGION': 'Society',
    'ENTERTAINMENT': 'Culture', 'ARTS': 'Culture',
    'CULTURE & ARTS': 'Culture', 'ARTS & CULTURE': 'Culture',
    'COMEDY': 'Culture', 'MEDIA': 'Culture',
    'PARENTING': 'Family', 'PARENTS': 'Family',
    'WEDDINGS': 'Family', 'DIVORCE': 'Family', 'FIFTY': 'Family',
    'SCIENCE': 'Science & Tech', 'TECH': 'Science & Tech',
    'ENVIRONMENT': 'Science & Tech', 'GREEN': 'Science & Tech',
    'SPORTS': 'Sports', 'CRIME': 'Crime',
    'EDUCATION': 'Education', 'COLLEGE': 'Education'
}

FAMOUS_SOURCES_UI = {
    'ANY (ALL TOP SOURCES)': None,
    'Crime': "reuters,associated-press,the-washington-post",
    'Culture': "the-new-york-times,bbc-news,the-guardian-uk,entertainment-weekly",
    'Education': "the-wall-street-journal,bbc-news,the-guardian-uk",
    'Family': "usa-today,the-washington-post,bbc-news",
    'Global News': "bbc-news,reuters,associated-press,al-jazeera-english",
    'Lifestyle': "vice-news,buzzfeed,ign,the-lad-bible",
    'Science & Tech': "techcrunch,wired,the-next-web,ars-technica,engadget",
    'Society': "the-guardian-uk,the-new-york-times,the-economist",
    'Sports': "espn,bleacher-report,nfl-news,bbc-sport,four-four-two,espncricinfo,fox-sports"
}

STAKEHOLDER_INSIGHTS = {
    'Crime': {
        'Simple': 'This article is about crime, law enforcement, or legal matters.',
        'FunFact': 'Crime news often focuses on "proximal relevance" — things happening near people\'s homes or safety.',
        'Context': 'The AI detected words like "law", "arrest", or "court" which strongly link to this category.'
    },
    'Culture': {
        'Simple': 'This article covers entertainment, arts, or media.',
        'FunFact': 'Did you know? Cultural news is the most shared type of news on platforms like Pinterest and Instagram!',
        'Context': 'Names of famous people, movies, or artistic terms triggered this prediction.'
    },
    'Education': {
        'Simple': 'This article is about schools, learning, or academic topics.',
        'FunFact': 'Education news sees massive traffic spikes every August and September during "Back to School" season.',
        'Context': 'The mention of academic institutions or learning processes helped the AI find this match.'
    },
    'Family': {
        'Simple': 'This article is about family life, parenting, or relationships.',
        'FunFact': 'Family-oriented news has some of the highest "Evergreen" value, meaning people read it for years after it\'s published.',
        'Context': 'Terms related to life stages and domestic life were the primary signals here.'
    },
    'Global News': {
        'Simple': 'This article covers world events, politics, or international affairs.',
        'FunFact': 'Global news moves fast — modern AI can categorize a world event within 3 seconds of the headline breaking.',
        'Context': 'Countries, political roles, and government actions were identified in the text.'
    },
    'Lifestyle': {
        'Simple': 'This article is about lifestyle topics — like health, travel, food, or fashion.',
        'FunFact': 'Travel articles are known as "Aspirational News" — users mostly read them for inspiration rather than immediate action.',
        'Context': 'Wellness, leisure, and consumer keywords led the AI to this result.'
    },
    'Science & Tech': {
        'Simple': 'This article is about science, technology, or innovation.',
        'FunFact': 'Articles about Space and AI are currently the two fastest-growing sub-sectors in tech journalism.',
        'Context': 'Technical terminology or mentions of emerging innovations were detected.'
    },
    'Society': {
        'Simple': 'This article covers social issues, identity, or community topics.',
        'FunFact': 'Society news often has the highest comment engagement because it touches on personal beliefs and community values.',
        'Context': 'Keywords related to community, identity, and social movements were prominent.'
    },
    'Sports': {
        'Simple': 'This article is about sports and athletic achievements.',
        'FunFact': 'Sports journalism is one of the oldest forms of news, dating back to ancient event announcements.',
        'Context': 'Game terminology, team names, or athletic action words were spotted by the engine.'
    },
    'General': {
        'Simple': 'This article is a general interest piece covering a mix of subjects.',
        'FunFact': 'General news serves as the "Front Page" of our digital lives, connecting us to the broader world.',
        'Context': 'The text didn\'t have a heavy bias toward one specific topic, leading to a "Balanced" result.'
    }
}

STAKEHOLDER_INSIGHTS_UR = {
    'Crime': {
        'Simple': 'یہ مضمون جرم، قانون نافذ کرنے والے اداروں، یا قانونی معاملات کے بارے میں ہے۔',
        'FunFact': 'جرم کی خبریں اکثر "قریبی مطابقت" پر توجہ مرکوز کرتی ہیں — یعنی وہ چیزیں جو لوگوں کے گھروں یا حفاظت کے قریب ہوتی ہیں۔',
        'Context': 'اے آئی نے "قانون"، "گرفتاری"، یا "عدالت" جیسے الفاظ کا پتہ لگایا جو اس زمرے سے مضبوطی سے جڑے ہوئے ہیں۔'
    },
    'Culture': {
        'Simple': 'یہ مضمون تفریح، فنون لطیفہ، یا میڈیا پر محیط ہے۔',
        'FunFact': 'کیا آپ جانتے ہیں؟ ثقافتی خبریں پنٹرسٹ اور انسٹاگرام جیسے پلیٹ فارمز پر سب سے زیادہ شیئر کی جانے والی خبریں ہیں!',
        'Context': 'مشہور لوگوں کے نام، فلموں، یا فنکارانہ اصطلاحات نے اس پیش گوئی کو جنم دیا۔'
    },
    'Education': {
        'Simple': 'یہ مضمون اسکولوں، سیکھنے، یا تعلیمی موضوعات کے بارے میں ہے۔',
        'FunFact': 'تعلیمی خبروں میں ہر سال اگست اور ستمبر میں "بیک ٹو اسکول" سیزن کے دوران زبردست اضافہ دیکھا جاتا ہے۔',
        'Context': 'تعلیمی اداروں یا سیکھنے کے عمل کے تذکرے نے اے آئی کو اس میچ کو تلاش کرنے میں مدد کی۔'
    },
    'Family': {
        'Simple': 'یہ مضمون خاندانی زندگی، والدین، یا تعلقات کے بارے میں ہے۔',
        'FunFact': 'خاندان پر مبنی خبروں کی "سدا بہار" قدر سب سے زیادہ ہوتی ہے، یعنی لوگ اسے شائع ہونے کے کئی سالوں کے بعد بھی پڑھتے ہیں۔',
        'Context': 'زندگی کے مراحل اور گھریلو زندگی سے متعلق اصطلاحات یہاں بنیادی سگنلز تھے۔'
    },
    'Global News': {
        'Simple': 'یہ مضمون عالمی واقعات، سیاست، یا بین الاقوامی امور پر محیط ہے۔',
        'FunFact': 'عالمی خبریں تیزی سے بدلتی ہیں — جدید اے آئی سرخی بننے کے 3 سیکنڈ کے اندر عالمی واقعے کی درجہ بندی کر سکتی ہے۔',
        'Context': 'متن میں ممالک، سیاسی کرداروں اور حکومتی اقدامات کی نشاندہی کی گئی۔'
    },
    'Lifestyle': {
        'Simple': 'یہ مضمون طرز زندگی کے موضوعات کے بارے میں ہے — جیسے صحت، سفر، کھانا، یا فیشن۔',
        'FunFact': 'سفر کے مضامین کو "خوابیدہ خبریں" کہا جاتا ہے — صارفین انہیں فوری کارروائی کے بجائے زیادہ تر ترغیب کے لیے پڑھتے ہیں۔',
        'Context': 'فلاح و بہبود، تفریح، اور صارفین کے کلیدی الفاظ نے اے آئی کو اس نتیجے پر پہنچایا۔'
    },
    'Science & Tech': {
        'Simple': 'یہ مضمون سائنس، ٹیکنالوجی، یا جدت طرازی کے بارے میں ہے۔',
        'FunFact': 'خلا اور اے آئی کے بارے میں مضامین فی الحال ٹیک جرنلزم میں سب سے تیزی سے بڑھتے ہوئے دو ذیلی شعبے ہیں۔',
        'Context': 'تکنیکی اصطلاحات یا ابھرتی ہوئی اختراعات کے تذکرے کا پتہ چلا۔'
    },
    'Society': {
        'Simple': 'یہ مضمون سماجی مسائل، شناخت، یا کمیونٹی کے موضوعات پر محیط ہے۔',
        'FunFact': 'معاشرے کی خبروں میں اکثر تبصروں کی مصروفیت سب سے زیادہ ہوتی ہے کیونکہ یہ ذاتی عقائد اور کمیونٹی کی اقدار کو چھوتی ہے۔',
        'Context': 'کمیونٹی، شناخت اور سماجی تحریکوں سے متعلق کلیدی الفاظ نمایاں تھے۔'
    },
    'Sports': {
        'Simple': 'یہ مضمون کھیلوں اور کھلاڑیوں کی کامیابیوں کے بارے میں ہے۔',
        'FunFact': 'اسپورٹس جرنلزم خبروں کی قدیم ترین شکلوں میں سے ایک ہے، جو قدیم دور کے مقابلوں کے اعلانات تک جاتی ہے۔',
        'Context': 'کھیل کی اصطلاحات، ٹیموں کے نام، یا کھلاڑیوں کے ایکشن الفاظ انجن کے ذریعے دیکھے گئے۔'
    },
    'General': {
        'Simple': 'یہ مضمون ایک عمومی دلچسپی کا ٹکڑا ہے جس میں مختلف مضامین کا امتزاج ہے۔',
        'FunFact': 'عمومی خبریں ہماری ڈیجیٹل زندگی کے "فرنٹ پیج" کے طور پر کام کرتی ہیں، جو ہمیں وسیع تر دنیا سے جوڑتی ہیں۔',
        'Context': 'متن کا کسی ایک مخصوص موضوع کی طرف زیادہ رجحان نہیں تھا، جس کی وجہ سے "متوازن" نتیجہ نکلا۔'
    }
}
