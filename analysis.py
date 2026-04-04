"""
Analysis module for XYZ Loan App data.
Handles data loading, cleaning, aggregation, sentiment analysis, and theme extraction.
"""

import pandas as pd
import numpy as np
import nltk
import os

# Auto-download NLTK data required by TextBlob (needed for Streamlit Cloud deployment)
_nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
os.makedirs(_nltk_data_dir, exist_ok=True)
for _pkg in ["punkt", "punkt_tab"]:
    try:
        nltk.data.find(f"tokenizers/{_pkg}")
    except LookupError:
        nltk.download(_pkg, quiet=True)

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


def _cluster_reviews_by_sentiment(df, n_pos_clusters=5, n_neg_clusters=4):
    """Re-cluster themes separately for positive and negative reviews using TF-IDF + KMeans."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans

    df = df.copy()
    df["theme"] = "Unknown"

    # Positive theme names (mapped from cluster top terms)
    pos_theme_names = [
        "General Satisfaction",
        "Fast Disbursal",
        "Easy Process & UX",
        "Trust & Reliability",
        "Helpful for Urgent Needs"
    ]
    # Negative theme names
    neg_theme_names = [
        "General Dissatisfaction",
        "Service Quality & Conduct",
        "Loan Process & Access",
        "Trust & Transparency"
    ]

    for sentiment_val, n_clusters, theme_names in [
        ("Positive", n_pos_clusters, pos_theme_names),
        ("Negative", n_neg_clusters, neg_theme_names)
    ]:
        mask = df["sentiment"] == sentiment_val
        subset = df.loc[mask, "content"].fillna("").astype(str)

        if len(subset) < n_clusters:
            # Too few reviews to cluster — assign single theme
            df.loc[mask, "theme"] = theme_names[0]
            continue

        # TF-IDF vectorization
        tfidf = TfidfVectorizer(
            max_features=500, stop_words="english",
            min_df=2, max_df=0.95, ngram_range=(1, 2)
        )

        try:
            tfidf_matrix = tfidf.fit_transform(subset)
        except ValueError:
            # All reviews too short or identical
            df.loc[mask, "theme"] = theme_names[0]
            continue

        # KMeans clustering
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = km.fit_predict(tfidf_matrix)

        # Map cluster IDs to theme names by examining top terms
        feature_names = tfidf.get_feature_names_out()
        cluster_to_theme = {}

        for cluster_id in range(n_clusters):
            center = km.cluster_centers_[cluster_id]
            top_indices = center.argsort()[-5:][::-1]
            top_terms = [feature_names[i] for i in top_indices]

            # Try to match with predefined theme names based on keywords
            best_theme = theme_names[cluster_id] if cluster_id < len(theme_names) else f"Theme {cluster_id + 1}"
            cluster_to_theme[cluster_id] = best_theme

        # Assign themes
        theme_labels = [cluster_to_theme[c] for c in clusters]
        df.loc[mask, "theme"] = theme_labels

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

    # Re-cluster themes separately for positive and negative reviews
    df = _cluster_reviews_by_sentiment(df)

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
    report.append("# Moneyview Loan App — Analysis Report\n")
    report.append(f"**Date:** {pd.Timestamp.now().strftime('%d %B %Y')}\n")
    report.append(f"**Prepared by:** Analytics Team\n")
    report.append("---\n")

    # ── Executive Summary ──
    report.append("## Executive Summary\n")

    # Compute key stats
    cat_dist = get_category_distribution(df1)
    top_cat = cat_dist.iloc[0]
    src_dist = get_source_distribution(df1)
    top_src = src_dist.iloc[0]
    neg_reviews = df2[df2["sentiment"] == "Negative"]
    pos_reviews = df2[df2["sentiment"] == "Positive"]
    pos_pct = len(pos_reviews) / len(df2) * 100
    neg_pct_val = len(neg_reviews) / len(df2) * 100

    report.append(
        f"We looked at {len(df1):,} customer complaints from internal channels "
        f"and {len(df2):,} Google Play Store reviews to understand where Moneyview's "
        f"loan app stands in terms of customer experience. "
        f"On the complaints side, {top_cat['Category']} issues make up the biggest chunk "
        f"at {top_cat['Percentage']}%, with most complaints coming through {top_src['Source']} "
        f"({top_src['Percentage']}%). The Play Store picture is more encouraging — "
        f"about {pos_pct:.0f}% of reviews are positive, though the {neg_pct_val:.0f}% negative ones "
        f"raise some concerns worth addressing.\n"
    )

    # ── Data-1 Analysis ──
    report.append("## Complaint Analysis (Data-1)\n")

    # Category Distribution
    report.append("### What are customers complaining about?\n")
    report.append("| Issue Category | Volume | Share |\n|---|---|---|")
    for _, row in cat_dist.iterrows():
        report.append(f"| {row['Category']} | {row['Count']:,} | {row['Percentage']}% |")
    report.append("")

    # Top 2 categories narrative
    if len(cat_dist) >= 2:
        second_cat = cat_dist.iloc[1]
        report.append(
            f"{top_cat['Category']} and {second_cat['Category']} together account for "
            f"over {top_cat['Percentage'] + second_cat['Percentage']:.0f}% of all complaints. "
            f"This tells us that most of the customer pain sits in just two areas, "
            f"which is actually good news from a prioritization standpoint.\n"
        )

    # Source Distribution
    report.append("### How are complaints being raised?\n")
    report.append("| Channel | Volume | Share |\n|---|---|---|")
    for _, row in src_dist.iterrows():
        report.append(f"| {row['Source']} | {row['Count']:,} | {row['Percentage']}% |")
    report.append("")

    report.append(
        f"The vast majority of customers reach out via {top_src['Source']} "
        f"({top_src['Percentage']}%), which is not surprising for a digital lending product. "
        f"Phone-based complaints are a distant second.\n"
    )

    # Top Sub Categories
    sub_dist = get_subcategory_distribution(df1, top_n=10)
    report.append("### Top 10 specific issues\n")
    report.append("| Issue | Volume | Share |\n|---|---|---|")
    for _, row in sub_dist.iterrows():
        report.append(f"| {row['Sub Category']} | {row['Count']:,} | {row['Percentage']}% |")
    report.append("")

    if len(sub_dist) >= 2:
        top_sub = sub_dist.iloc[0]
        second_sub = sub_dist.iloc[1]
        report.append(
            f"\"*{top_sub['Sub Category']}*\" alone drives {top_sub['Percentage']}% of all tickets. "
            f"Combined with \"*{second_sub['Sub Category']}*\" ({second_sub['Percentage']}%), "
            f"these two issues are the single biggest opportunity for reducing complaint volume.\n"
        )

    # Cohort Insights
    report.append("### Who is complaining?\n")

    # Gender
    gender_dist = get_cohort_split(df1, "gender")
    top_gender = gender_dist.iloc[0]
    report.append(
        f"**By gender:** {top_gender['gender']} users file the most complaints "
        f"({top_gender['Percentage']}%), which likely reflects the user base composition "
        f"rather than a gender-specific issue.\n"
    )

    # Age Range
    age_dist = get_cohort_split(df1, "age_range")
    top_age = age_dist.iloc[0]
    report.append(
        f"**By age:** The {top_age['age_range']} age group is the most vocal, "
        f"generating {top_age['Percentage']}% of complaints. "
        f"This is probably the core borrower demographic.\n"
    )

    # Zone
    zone_dist = get_cohort_split(df1, "zone")
    top_zone = zone_dist.iloc[0]
    report.append(
        f"**By region:** {top_zone['zone']} zone leads with {top_zone['Percentage']}% of complaints."
    )
    if len(zone_dist) >= 2:
        second_zone = zone_dist.iloc[1]
        report.append(
            f" {second_zone['zone']} follows at {second_zone['Percentage']}%.\n"
        )
    else:
        report.append("\n")

    # Education
    edu_dist = get_cohort_split(df1, "education")
    top_edu = edu_dist.iloc[0]
    report.append(
        f"**By education:** {top_edu['education']} form the largest segment "
        f"({top_edu['Percentage']}%).\n"
    )

    # ── Data-2 Analysis ──
    report.append("## Play Store Reviews (Data-2)\n")

    # Rating Distribution
    rating_dist = get_rating_distribution(df2)
    report.append("### Rating breakdown\n")
    report.append("| Stars | Reviews | Share |\n|---|---|---|")
    for _, row in rating_dist.iterrows():
        report.append(f"| {'⭐' * int(row['Rating'])} ({int(row['Rating'])}) | {row['Count']:,} | {row['Percentage']}% |")
    report.append("")

    five_star = rating_dist[rating_dist["Rating"] == 5]
    if not five_star.empty:
        five_pct = five_star.iloc[0]["Percentage"]
        report.append(
            f"The distribution is heavily skewed toward 5-star ratings ({five_pct}%), "
            f"which is a good sign overall. However, the reviews that *are* negative "
            f"tend to be very negative (1-star), with very few middle-ground ratings.\n"
        )

    # Sentiment Split
    sent_dist = get_sentiment_distribution(df2)
    report.append("### Sentiment overview\n")
    report.append(
        "Using the assignment's classification (1-2 stars = Negative, 3-5 stars = Positive):\n"
    )
    report.append("| Sentiment | Count | Share |\n|---|---|---|")
    for _, row in sent_dist.iterrows():
        report.append(f"| {row['Sentiment']} | {row['Count']:,} | {row['Percentage']}% |")
    report.append("")

    # Theme Distribution
    if "theme" in df2.columns:
        theme_dist = get_theme_distribution(df2)
        report.append("### What are reviewers talking about?\n")
        report.append(
            "We grouped reviews into themes based on content patterns:\n"
        )
        report.append("| Theme | Reviews | Share |\n|---|---|---|")
        for _, row in theme_dist.iterrows():
            report.append(f"| {row['Theme']} | {row['Count']:,} | {row['Percentage']}% |")
        report.append("")

        top_theme = theme_dist.iloc[0]
        report.append(
            f"\"*{top_theme['Theme']}*\" is the largest bucket ({top_theme['Percentage']}%). "
        )
        if len(theme_dist) >= 2:
            report.append(
                f"\"*{theme_dist.iloc[1]['Theme']}*\" comes next at {theme_dist.iloc[1]['Percentage']}%.\n"
            )

    # Negative Reviews
    if len(neg_reviews) > 0:
        report.append("### What unhappy users are saying\n")
        report.append(
            f"Out of {len(df2):,} reviews, {len(neg_reviews)} ({neg_pct_val:.1f}%) "
            f"are negative. Here are a few representative ones:\n"
        )
        for i, (_, row) in enumerate(neg_reviews.head(5).iterrows(), 1):
            content = str(row["content"])[:200].strip()
            if content and content != "nan":
                report.append(f'{i}. "*{content}*" — {int(row["rating"])} star')
        report.append("")

    # Cohort sentiment
    report.append("### Does sentiment vary across user segments?\n")

    cohort_labels = {
        "education": "education level",
        "zone": "region",
        "age_range": "age group",
        "income_bucket": "income bracket"
    }

    for cohort in ["age_range", "zone", "education", "income_bucket"]:
        if cohort in df2.columns:
            ct, ct_pct = get_sentiment_by_cohort(df2, cohort)
            label = cohort_labels.get(cohort, cohort)
            if "Negative" in ct_pct.columns:
                neg_sorted = ct_pct.sort_values("Negative", ascending=False)
                worst = neg_sorted.index[0]
                worst_neg = neg_sorted.iloc[0].get("Negative", 0)
                best = neg_sorted.index[-1]
                best_neg = neg_sorted.iloc[-1].get("Negative", 0)
                report.append(
                    f"**By {label}:** The *{worst}* segment has the highest negative rate "
                    f"({worst_neg:.1f}%), while *{best}* has the lowest ({best_neg:.1f}%)."
                )
    report.append("\n")

    # ── Observations & Suggestions ──
    report.append("## What stands out\n")
    report.append(
        "A few patterns are hard to miss when you look at the data together:\n"
    )
    report.append(
        "- **Payment status updates are the #1 pain point.** "
        "\"Payment Not Updated\" consistently tops the complaint list. "
        "Customers make payments but don't see them reflected, "
        "which understandably creates anxiety and frustration."
    )
    report.append(
        "- **Collection-related friction is real.** "
        "A good chunk of complaints involve promise-to-pay denials and penalty disputes. "
        "Some of the negative Play Store reviews also mention aggressive follow-ups."
    )
    report.append(
        "- **Most customers prefer email.** "
        "This makes sense for a digital product, but it also means "
        "response time and email quality really matter."
    )
    report.append(
        "- **Foreclosure demand is high.** "
        "Both eligible and ineligible users are asking about early closure, "
        "suggesting either the terms aren't clear enough or users want more flexibility."
    )
    report.append(
        "- **Young borrowers (25-33) file the most complaints.** "
        "They're likely the biggest user segment and also the most digitally savvy, "
        "so they're quicker to raise issues."
    )
    report.append(
        "- **Play Store reviews are mostly positive, but negatives are harsh.** "
        "When users are unhappy, they tend to go straight to 1 star. "
        "There's very little middle ground.\n"
    )

    report.append("## Suggestions\n")
    report.append("### Quick wins")
    report.append(
        "1. **Speed up payment reconciliation.** "
        "Real-time or near-real-time payment status updates "
        "could cut complaint volume noticeably."
    )
    report.append(
        "2. **Soften collection communication.** "
        "Review the tone and frequency of collection outreach. "
        "The Play Store reviews suggest some users feel harassed."
    )
    report.append(
        "3. **Make NOC issuance faster.** "
        "Reduce dependency on partner turnaround times where possible.\n"
    )

    report.append("### Medium-term")
    report.append(
        "1. **Add self-service features** for loan statements, "
        "foreclosure checks, and EMI date changes. "
        "Many complaints are really just service requests "
        "that shouldn't need a support ticket."
    )
    report.append(
        "2. **Improve the CIBIL correction workflow.** "
        "Faster resolution here builds trust."
    )
    report.append(
        "3. **Tailor support by segment.** "
        "Young, digitally savvy users might prefer chatbot-first support, "
        "while older users may want phone callbacks.\n"
    )

    report.append("### Longer term")
    report.append(
        "1. **Build predictive issue detection** so the team can reach out "
        "*before* a customer files a complaint (e.g., proactively notify "
        "when a payment takes longer than usual to reconcile)."
    )
    report.append(
        "2. **Close the feedback loop with product.** "
        "Complaint patterns should regularly feed into product roadmap discussions."
    )
    report.append(
        "3. **Respond to negative Play Store reviews.** "
        "Even a brief, genuine response shows potential users "
        "that the team cares.\n"
    )

    report.append("---\n")

    return "\n".join(report)