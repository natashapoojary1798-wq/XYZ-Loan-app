# XYZ Loan App — Comprehensive Analysis Dashboard

Interactive Streamlit dashboard analyzing customer complaints (Data-1) and Google Play reviews (Data-2) for the XYZ Loan App.

## 📂 Project Structure

```
├── csv/
│   ├── data-1.csv          # Customer complaints (~238K records)
│   ├── data-2.csv          # Google reviews (~741 records)
│   └── question.txt        # Assignment brief
├── app.py                  # Streamlit dashboard (main entry point)
├── analysis.py             # Data analysis module
├── requirements.txt        # Python dependencies
├── report.md               # Generated analysis report (after running)
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Install Dependencies

```bash
# Windows
venv\Scripts\pip install -r requirements.txt

# macOS/Linux
venv/bin/pip install -r requirements.txt
```

### 3. Download NLTK Data (one-time)

```bash
# Windows
venv\Scripts\python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# macOS/Linux
venv/bin/python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

### 4. Run the Dashboard

```bash
# Windows
venv\Scripts\streamlit run app.py

# macOS/Linux
venv/bin/streamlit run app.py
```

The dashboard will open at **http://localhost:8501**.

### 5. Make accessible on local network (optional)

```bash
streamlit run app.py --server.address 0.0.0.0
```

Others on the same Wi-Fi/LAN can access at `http://<your-local-ip>:8501`.

---

## ☁️ Deploy on Streamlit Community Cloud (Free, Public URL)

### Prerequisites
- A **GitHub account**
- Code pushed to a **public** (or private with Streamlit access) GitHub repository

### Steps

1. **Push to GitHub** — ensure these files are in the repo:
   ```
   app.py
   analysis.py
   requirements.txt
   .streamlit/config.toml
   csv/data-1-new.csv
   csv/data-2-new.csv
   csv/crosstab1-data1.csv
   csv/crosstab1-data2.csv
   csv/crosstab2-data1.csv
   ```

2. **Go to** [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub

3. **Click** "New app" → select your repository, branch (`main`), and main file: `app.py`

4. **Click** "Deploy" — Streamlit Cloud will install dependencies from `requirements.txt` and start the app

5. **Done!** You'll get a public URL like `https://your-app-name.streamlit.app`

### ⚠️ Important Notes

| Concern | Details |
|---------|---------|
| **NLTK data** | Auto-downloaded at runtime (handled in `analysis.py`) |
| **Large CSV files** | `data-1-new.csv` is 27 MB — works fine but makes repo heavy. Consider Git LFS for repos > 100 MB |
| **Free tier limits** | 1 GB RAM, apps sleep after inactivity, public repos only (private repos need paid plan) |
| **Secrets** | No secrets/API keys needed for this app |

### Alternative Deployment Options

| Platform | Free Tier | URL |
|----------|-----------|-----|
| **Streamlit Cloud** | ✅ Yes | [share.streamlit.io](https://share.streamlit.io) |
| **Hugging Face Spaces** | ✅ Yes | [huggingface.co/spaces](https://huggingface.co/spaces) |
| **Railway** | ✅ Starter plan | [railway.app](https://railway.app) |
| **Render** | ✅ Yes | [render.com](https://render.com) |

---

## 📊 Dashboard Pages

### 🏠 Overview
- KPI cards: total complaints, total reviews, top issue category, positive review %
- Category pie chart and rating bar chart side-by-side

### 📋 Data-1: Complaints
- **Issue Splits:** Category/sub-category distribution, source channel breakdown
- **Cohort Analysis:** Issue breakdown by gender, age, education, zone, income
- **Trends:** Monthly issue volume and category trends
- **Deep Dive:** Query type split and raw data browser
- Interactive filters: Category, Source, Zone

### ⭐ Data-2: Reviews
- **Sentiment:** Rating distribution, positive/negative split, sentiment score histogram
- **Themes:** Auto-extracted themes via TF-IDF + KMeans, theme × sentiment cross-analysis
- **Cohort Analysis:** Sentiment split by education, zone, age, income
- **Reviews Browser:** Sortable, filterable review table
- Interactive filters: Sentiment, Theme

### 📝 Report
- Auto-generated comprehensive markdown report
- Download as `.md` file or save locally

## 🔧 Tech Stack

| Component | Library |
|-----------|---------|
| Dashboard | Streamlit 1.40 |
| Charts | Plotly 5.24 |
| Data Processing | Pandas 2.2 |
| Sentiment Analysis | TextBlob 0.18 |
| Theme Extraction | scikit-learn (TF-IDF + KMeans) |
| NLP | NLTK 3.9 |

## 📋 Assignment Coverage

| Requirement | Implementation |
|------------|----------------|
| Data-1: Overall issue splits | ✅ Category & sub-category distribution |
| Data-1: Cohort splits | ✅ Gender, age, education, zone, income breakdowns |
| Data-2: Bucket issues into themes | ✅ TF-IDF + KMeans automated theme extraction |
| Data-2: 1-2 as negative, 3-5 as positive | ✅ Rating-based sentiment classification |
| Data-2: Sentiment analysis | ✅ TextBlob polarity + rating-based sentiment |
| Data-2: Cohort analysis | ✅ Sentiment by education, zone, age, income |
| Data-2: Percentages | ✅ All charts show percentage breakdowns |
| Report with key insights | ✅ Auto-generated report with recommendations |