"""
Analysis module for XYZ Loan App data.
Handles data loading, cleaning, aggregation, sentiment analysis, and theme extraction.
"""

import pandas as pd
import numpy as np
from textblob import TextBlob


# ─────────────────────────────────────────────
# Data Loading & Cleaning
# ─────────────────────────────────────────────

def load_data1(path="csv/data-1-new.csv"):
    """Load and clean Data-1 (app complaints/issues)."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    # Parse datetime (format: DD-MM-YYYY HH.MM)
    df["DateTime"] = pd.to_datetime(df["DateTime"], format="%d-%m-%Y %H.%M", errors="coerce")

    # Standardize column names for internal use
    df = df.rename(columns={
        "Gender": "gender",
        "Age_range": "age_range",
        "Zone": "zone",
        "Education_Cleaned": "education",
        "Monthly_Income_Cleaned": "income_bucket"
    })

    # Clean categorical columns
    for col in ["Query Type", "Source", "Category", "Sub Category",
                "gender", "education", "age_range", "zone", "income_bucket"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": "Unknown", "": "Unknown"})

    # Exclude invalid data rows
    df = df[df["income_bucket"] != "Invalid Data"]

    # Extract month
    df["month"] = df["DateTime"].dt.to_period("M").astype(str)

    return df


def load_crosstab1_data1(path="csv/crosstab1-data1.csv"):
    """Load pre-computed crosstab for Data-1 (overall x cohorts)."""
    df = pd.read_csv(path, encoding="cp1252", header=None)
    return df


def load_crosstab2_data1(path="csv/crosstab2-data1.csv"):
    """Load pre-computed crosstab for Data-1 (category x sub-category breakdown)."""
    df = pd.read_csv(path, encoding="cp1252", header=None)
    return df


def load_crosstab1_data2(path="csv/crosstab1-data2.csv"):
    """Load pre-computed crosstab for Data-2 (reviews x cohorts)."""
    df = pd.read_csv(path, encoding="cp1252", header=None)
    return df


def load_data2(path="csv/data-2-new.csv"):
    """Load and clean Data-2 (Google reviews)."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    # Rename for consistency
    df = df.rename(columns={
        "Google_Review": "content",
        "Rating (1-5 star)": "rating",
        "DateTime": "review_date",
        "Sentiment": "sentiment",
        "Age_Range": "age_range",
        "Zone": "zone",
        "Education": "education",
        "Monthly_Income_Cleaned": "income_bucket",
        "Theme": "theme"
    })

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # Clean categorical columns
    for col in ["sentiment", "age_range", "zone", "education", "income_bucket", "theme"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": "Unknown", "": "Unknown"})

    return df


# ─────────────────────────────────────────────
# Data-1 Aggregations
# ─────────────────────────────────────────────

def get_category_distribution(df):
    """Get issue distribution by Category."""
    counts = df["Category"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


def get_subcategory_distribution(df, top_n=10):
    """Get issue distribution by Sub Category."""
    counts = df["Sub Category"].value_counts().head(top_n).reset_index()
    counts.columns = ["Sub Category", "Count"]
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


def get_source_distribution(df):
    """Get distribution by Source channel."""
    counts = df["Source"].value_counts().reset_index()
    counts.columns = ["Source", "Count"]
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


def get_cohort_split(df, cohort_col):
    """Get issue distribution by a cohort column."""
    counts = df[cohort_col].value_counts().reset_index()
    counts.columns = [cohort_col, "Count"]
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


def get_category_by_cohort(df, cohort_col):
    """Cross-tabulation of Category by a cohort column."""
    ct = pd.crosstab(df[cohort_col], df["Category"])
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    return ct, ct_pct


def get_subcategory_by_cohort(df, cohort_col, top_n=10):
    """Cross-tabulation of top Sub Categories by a cohort column."""
    top_subs = df["Sub Category"].value_counts().head(top_n).index
    df_top = df[df["Sub Category"].isin(top_subs)]
    ct = pd.crosstab(df_top[cohort_col], df_top["Sub Category"])
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    return ct, ct_pct


def get_monthly_trend(df):
    """Get monthly trend of issues."""
    counts = df.groupby("month").size().reset_index(name="Count")
    return counts


def get_category_monthly_trend(df):
    """Get monthly trend by category."""
    counts = df.groupby(["month", "Category"]).size().reset_index(name="Count")
    return counts


# ─────────────────────────────────────────────
# Data-2 Sentiment Analysis
# ─────────────────────────────────────────────

def get_sentiment_score(text):
    """Get sentiment polarity using TextBlob."""
    if not isinstance(text, str) or text.strip() == "":
        return 0.0
    try:
        return TextBlob(text).sentiment.polarity
    except Exception:
        return 0.0


def add_sentiment_scores(df):
    """Add detailed sentiment scores to Data-2."""
    df = df.copy()
    df["sentiment_score"] = df["content"].apply(get_sentiment_score)
    df["sentiment_label"] = df["sentiment_score"].apply(
        lambda x: "Positive" if x > 0.05 else ("Negative" if x < -0.05 else "Neutral")
    )
    return df


def get_sentiment_distribution(df):
    """Get distribution of sentiment categories."""
    counts = df["sentiment"].value_counts().reset_index()
    counts.columns = ["Sentiment", "Count"]
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


def get_rating_distribution(df):
    """Get distribution of ratings."""
    counts = df["rating"].value_counts().sort_index().reset_index()
    counts.columns = ["Rating", "Count"]
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


def get_theme_distribution(df):
    """Get distribution of themes."""
    counts = df["theme"].value_counts().reset_index()
    counts.columns = ["Theme", "Count"]
    counts["Percentage"] = (counts["Count"] / counts["Count"].sum() * 100).round(2)
    return counts


def get_theme_sentiment_cross(df):
    """Cross-tabulation of themes by sentiment."""
    ct = pd.crosstab(df["theme"], df["sentiment"])
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    return ct, ct_pct


def get_sentiment_by_cohort(df, cohort_col):
    """Get sentiment distribution by cohort."""
    ct = pd.crosstab(df[cohort_col], df["sentiment"])
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    return ct, ct_pct


# ─────────────────────────────────────────────
# Report Generation
# ─────────────────────────────────────────────

def generate_report(df1, df2):
    """Generate a comprehensive markdown report."""
    report = []
    report.append("# XYZ Loan App — Comprehensive Analysis Report\n")
    report.append(f"**Generated on:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
    report.append("---\n")

    # ── Executive Summary ──
    report.append("## 1. Executive Summary\n")
    report.append(f"This report analyzes **{len(df1):,}** customer complaints/issues (Data-1) "
                  f"and **{len(df2):,}** Google Play reviews (Data-2) for the XYZ Loan App. "
                  "The analysis covers issue distribution, channel usage, cohort breakdowns, "
                  "sentiment analysis, and thematic review analysis.\n")

    # ── Data-1 Analysis ──
    report.append("## 2. Data-1 Analysis: Customer Complaints & Issues\n")

    # Category Distribution
    cat_dist = get_category_distribution(df1)
    report.append("### 2.1 Issue Category Distribution\n")
    report.append("| Category | Count | Percentage |\n|---|---|---|")
    for _, row in cat_dist.iterrows():
        report.append(f"| {row['Category']} | {row['Count']:,} | {row['Percentage']}% |")
    report.append("")

    top_cat = cat_dist.iloc[0]
    report.append(f"**Key Finding:** *{top_cat['Category']}* is the dominant issue category, "
                  f"accounting for **{top_cat['Percentage']}%** of all complaints.\n")

    # Source Distribution
    src_dist = get_source_distribution(df1)
    report.append("### 2.2 Channel Distribution\n")
    report.append("| Channel | Count | Percentage |\n|---|---|---|")
    for _, row in src_dist.iterrows():
        report.append(f"| {row['Source']} | {row['Count']:,} | {row['Percentage']}% |")
    report.append("")

    top_src = src_dist.iloc[0]
    report.append(f"**Key Finding:** *{top_src['Source']}* is the primary complaint channel "
                  f"({top_src['Percentage']}%), suggesting most users prefer written communication.\n")

    # Top Sub Categories
    sub_dist = get_subcategory_distribution(df1, top_n=10)
    report.append("### 2.3 Top 10 Sub-Categories\n")
    report.append("| Sub Category | Count | Percentage |\n|---|---|---|")
    for _, row in sub_dist.iterrows():
        report.append(f"| {row['Sub Category']} | {row['Count']:,} | {row['Percentage']}% |")
    report.append("")

    # Cohort Insights
    report.append("### 2.4 Cohort Analysis\n")

    # Gender
    gender_dist = get_cohort_split(df1, "gender")
    report.append("**Gender Distribution:**\n")
    for _, row in gender_dist.iterrows():
        report.append(f"- {row['gender']}: {row['Count']:,} ({row['Percentage']}%)")
    report.append("")

    # Age Range
    age_dist = get_cohort_split(df1, "age_range")
    report.append("**Age Range Distribution:**\n")
    for _, row in age_dist.iterrows():
        report.append(f"- {row['age_range']}: {row['Count']:,} ({row['Percentage']}%)")
    report.append("")

    # Zone
    zone_dist = get_cohort_split(df1, "zone")
    report.append("**Zone Distribution:**\n")
    for _, row in zone_dist.iterrows():
        report.append(f"- {row['zone']}: {row['Count']:,} ({row['Percentage']}%)")
    report.append("")

    # Education
    edu_dist = get_cohort_split(df1, "education")
    report.append("**Education Level Distribution:**\n")
    for _, row in edu_dist.iterrows():
        report.append(f"- {row['education']}: {row['Count']:,} ({row['Percentage']}%)")
    report.append("")

    # ── Data-2 Analysis ──
    report.append("## 3. Data-2 Analysis: Google Reviews\n")

    # Rating Distribution
    rating_dist = get_rating_distribution(df2)
    report.append("### 3.1 Rating Distribution\n")
    report.append("| Rating | Count | Percentage |\n|---|---|---|")
    for _, row in rating_dist.iterrows():
        report.append(f"| {int(row['Rating'])} ⭐ | {row['Count']:,} | {row['Percentage']}% |")
    report.append("")

    # Sentiment Split
    sent_dist = get_sentiment_distribution(df2)
    report.append("### 3.2 Sentiment Split (1-2 = Negative, 3-5 = Positive)\n")
    report.append("| Sentiment | Count | Percentage |\n|---|---|---|")
    for _, row in sent_dist.iterrows():
        report.append(f"| {row['Sentiment']} | {row['Count']:,} | {row['Percentage']}% |")
    report.append("")

    # Theme Distribution
    if "theme" in df2.columns:
        theme_dist = get_theme_distribution(df2)
        report.append("### 3.3 Theme Distribution\n")
        report.append("| Theme | Count | Percentage |\n|---|---|---|")
        for _, row in theme_dist.iterrows():
            report.append(f"| {row['Theme']} | {row['Count']:,} | {row['Percentage']}% |")
        report.append("")

    # Negative Reviews Analysis
    neg_reviews = df2[df2["sentiment"] == "Negative"]
    if len(neg_reviews) > 0:
        report.append("### 3.4 Key Negative Review Themes\n")
        report.append(f"Total negative reviews (1-2 stars): **{len(neg_reviews)}** "
                      f"({len(neg_reviews)/len(df2)*100:.1f}%)\n")
        report.append("**Sample negative reviews:**\n")
        for _, row in neg_reviews.head(5).iterrows():
            content = str(row["content"])[:150]
            report.append(f"- *\"{content}...\"* (Rating: {int(row['rating'])}⭐)")
        report.append("")

    # Cohort sentiment
    report.append("### 3.5 Sentiment by Cohort\n")

    for cohort in ["education", "zone", "age_range", "income_bucket"]:
        if cohort in df2.columns:
            ct, ct_pct = get_sentiment_by_cohort(df2, cohort)
            report.append(f"**Sentiment by {cohort.replace('_', ' ').title()}:**\n")
            if "Negative" in ct_pct.columns:
                neg_sorted = ct_pct.sort_values("Negative", ascending=False)
                for idx, row in neg_sorted.head(5).iterrows():
                    neg_pct = row.get("Negative", 0)
                    pos_pct = row.get("Positive", 0)
                    report.append(f"- {idx}: Negative {neg_pct:.1f}% | Positive {pos_pct:.1f}%")
            report.append("")

    # ── Key Insights & Recommendations ──
    report.append("## 4. Key Insights\n")
    report.append("1. **Payment-related issues dominate** — \"Payment Not Updated\" is the single "
                  "largest sub-category, indicating systemic payment reconciliation problems.")
    report.append("2. **Collection-related complaints are significant** — Promise-to-pay denials and "
                  "penalty charges suggest aggressive collection practices causing customer friction.")
    report.append("3. **Email is the overwhelmingly preferred channel** — Digital-first complaint "
                  "behavior aligns with the app's user base.")
    report.append("4. **Foreclosure requests are high** — Both eligible and ineligible foreclosure "
                  "queries indicate users want early loan closure options.")
    report.append("5. **Google reviews show thematic patterns** — Themes like 'General Dissatisfaction', "
                  "'Service Quality & Conduct', and 'Trust & Transparency' highlight key improvement areas.")
    report.append("6. **Younger demographics (25-33) report the most issues** — This is likely "
                  "the core user base and needs targeted support improvements.\n")

    report.append("## 5. Recommendations & Way Forward\n")
    report.append("### 5.1 Immediate Actions")
    report.append("1. **Fix payment reconciliation** — Implement real-time payment status updates "
                  "to reduce \"Payment Not Updated\" complaints.")
    report.append("2. **Review collection practices** — Address harassment allegations in Google "
                  "reviews; implement empathetic collection protocols.")
    report.append("3. **Streamline NOC process** — Reduce wait times and partner dependencies "
                  "for NOC issuance.\n")

    report.append("### 5.2 Medium-term Improvements")
    report.append("1. **Enhance self-service options** — Add in-app features for loan statements, "
                  "foreclosure eligibility checks, and EMI date changes.")
    report.append("2. **Improve CIBIL correction process** — Partner with credit bureaus for "
                  "faster resolution.")
    report.append("3. **Targeted communication for cohorts** — Create age-specific and "
                  "education-level-specific support resources.\n")

    report.append("### 5.3 Long-term Strategy")
    report.append("1. **Proactive issue detection** — Use ML models to predict and prevent "
                  "common issues before users report them.")
    report.append("2. **Feedback loop with product** — Channel complaint insights into product "
                  "development for UX improvements.")
    report.append("3. **Review response management** — Actively respond to negative Google "
                  "reviews to demonstrate customer care.\n")

    report.append("---\n")
    report.append("*Report generated automatically from data analysis. "
                  "For questions, contact the analytics team.*\n")

    return "\n".join(report)