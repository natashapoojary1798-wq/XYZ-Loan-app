"""
XYZ Loan App — Comprehensive Analysis Dashboard
Streamlit application combining Data-1 (Complaints) and Data-2 (Reviews) analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import analysis as an

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="XYZ Loan App — Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container { padding-top: 1rem; max-width: 1400px; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem; border-radius: 12px; color: white; text-align: center;
    }
    .metric-card h3 { margin: 0; font-size: 2rem; }
    .metric-card p { margin: 0.3rem 0 0 0; font-size: 0.9rem; opacity: 0.85; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px; border-radius: 8px 8px 0 0;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Color palette
COLORS = px.colors.qualitative.Set2
NEG_POS_COLORS = {"Negative": "#EF553B", "Positive": "#00CC96", "Neutral": "#FFA15A", "Unknown": "#BABABA"}


# ─────────────────────────────────────────────
# Data Loading (cached)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading Data-1 (complaints)...")
def load_d1():
    return an.load_data1()

@st.cache_data(show_spinner="Loading Data-2 (reviews)...")
def load_d2():
    df = an.load_data2()
    df = an.add_sentiment_scores(df)
    return df


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
st.sidebar.title("📊 XYZ Loan App")
st.sidebar.markdown("### Analysis Dashboard")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "📋 Data-1: Complaints", "⭐ Data-2: Reviews", "📊 Crosstab Analysis", "📝 Report"],
    index=0
)

# Load data
df1 = load_d1()
df2 = load_d2()

@st.cache_data(show_spinner="Loading crosstab data...")
def load_crosstabs():
    ct1_d1 = an.load_crosstab1_data1()
    ct2_d1 = an.load_crosstab2_data1()
    ct1_d2 = an.load_crosstab1_data2()
    return ct1_d1, ct2_d1, ct1_d2


# ═════════════════════════════════════════════
# PAGE: Overview
# ═════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("🏠 Dashboard Overview")
    st.markdown("Comprehensive analysis of XYZ Loan App customer complaints and Google reviews.")

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(df1):,}</h3>
            <p>Total Complaints (Data-1)</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3>{len(df2):,}</h3>
            <p>Total Reviews (Data-2)</p>
        </div>""", unsafe_allow_html=True)

    with col3:
        top_cat = df1["Category"].value_counts().index[0]
        top_cat_pct = (df1["Category"].value_counts().iloc[0] / len(df1) * 100)
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3>{top_cat_pct:.1f}%</h3>
            <p>Top Issue: {top_cat}</p>
        </div>""", unsafe_allow_html=True)

    with col4:
        pos_pct = (df2["sentiment"] == "Positive").sum() / len(df2) * 100
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <h3>{pos_pct:.1f}%</h3>
            <p>Positive Reviews</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Side-by-side charts
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📋 Complaint Categories")
        cat_dist = an.get_category_distribution(df1)
        fig = px.pie(cat_dist, values="Count", names="Category",
                     color_discrete_sequence=COLORS, hole=0.4)
        fig.update_traces(textposition="outside", textinfo="percent+label",
                          textfont_size=11)
        fig.update_layout(height=550, margin=dict(t=40, b=80, l=80, r=80),
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("⭐ Review Ratings")
        rating_dist = an.get_rating_distribution(df2)
        fig = px.bar(rating_dist, x="Rating", y="Count",
                     text="Percentage", color="Rating",
                     color_continuous_scale="RdYlGn")
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(height=550, margin=dict(t=40, b=40),
                          showlegend=False, coloraxis_showscale=False,
                          xaxis_title="Rating (Stars)", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)


# ═════════════════════════════════════════════
# PAGE: Data-1 Complaints Dashboard
# ═════════════════════════════════════════════
elif page == "📋 Data-1: Complaints":
    st.title("📋 Data-1: Customer Complaints & Issues")
    st.markdown(f"**Total records:** {len(df1):,}")

    # Filters in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filters")

    # Query Type filter
    query_types = ["All"] + sorted(df1["Query Type"].unique().tolist())
    sel_query_type = st.sidebar.selectbox("Query Type", query_types)

    # Category filter
    categories = ["All"] + sorted(df1["Category"].unique().tolist())
    sel_category = st.sidebar.selectbox("Category", categories)

    # Source filter
    sources = ["All"] + sorted(df1["Source"].unique().tolist())
    sel_source = st.sidebar.selectbox("Source Channel", sources)

    # Demographic filters
    st.sidebar.markdown("**Demographics**")

    # Gender filter
    genders = ["All"] + sorted(df1["gender"].unique().tolist())
    sel_gender = st.sidebar.selectbox("Gender", genders)

    # Age Range filter
    age_ranges = ["All"] + sorted(df1["age_range"].unique().tolist())
    sel_age = st.sidebar.selectbox("Age Range", age_ranges)

    # Education filter
    edu_levels = ["All"] + sorted(df1["education"].unique().tolist())
    sel_edu = st.sidebar.selectbox("Education Level", edu_levels)

    # Zone filter
    zones = ["All"] + sorted(df1["zone"].unique().tolist())
    sel_zone = st.sidebar.selectbox("Zone", zones)

    # Income Bucket filter
    income_buckets = ["All"] + sorted(df1["income_bucket"].unique().tolist())
    sel_income = st.sidebar.selectbox("Income Bucket", income_buckets)

    # Apply filters
    filtered = df1.copy()
    if sel_query_type != "All":
        filtered = filtered[filtered["Query Type"] == sel_query_type]
    if sel_category != "All":
        filtered = filtered[filtered["Category"] == sel_category]
    if sel_source != "All":
        filtered = filtered[filtered["Source"] == sel_source]
    if sel_gender != "All":
        filtered = filtered[filtered["gender"] == sel_gender]
    if sel_age != "All":
        filtered = filtered[filtered["age_range"] == sel_age]
    if sel_edu != "All":
        filtered = filtered[filtered["education"] == sel_edu]
    if sel_zone != "All":
        filtered = filtered[filtered["zone"] == sel_zone]
    if sel_income != "All":
        filtered = filtered[filtered["income_bucket"] == sel_income]

    st.markdown(f"**Filtered records:** {len(filtered):,}")

    # ── Tab Layout ──
    tab1, tab2, tab3, tab5 = st.tabs([
        "📊 Issue Splits", "👥 Cohort Analysis", "📈 Trends", "💡 Key Insights"
    ])

    # ── TAB 1: Issue Splits ──
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Category Distribution")
            cat_dist = an.get_category_distribution(filtered)
            fig = px.pie(cat_dist, values="Count", names="Category",
                         color_discrete_sequence=COLORS, hole=0.4)
            fig.update_traces(textposition="outside", textinfo="percent+label",
                              textfont_size=11)
            fig.update_layout(height=550, showlegend=False,
                              margin=dict(l=80, r=80, t=40, b=80))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Source Channel Distribution")
            src_dist = an.get_source_distribution(filtered)
            fig = px.pie(src_dist, values="Count", names="Source",
                         color_discrete_sequence=COLORS, hole=0.45)
            fig.update_traces(textposition="outside", textinfo="percent+label",
                              textfont_size=11)
            fig.update_layout(height=550, margin=dict(t=40, b=80, l=80, r=80))
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Top 10 Sub-Categories")
        sub_dist = an.get_subcategory_distribution(filtered, top_n=10)
        fig = px.bar(sub_dist, x="Count", y="Sub Category", orientation="h",
                     text="Percentage", color="Count",
                     color_continuous_scale="Blues")
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(height=500, yaxis=dict(categoryorder="total ascending"),
                          coloraxis_showscale=False,
                          margin=dict(l=10, r=60, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Query Type Split")
        qt_dist = an.get_cohort_split(filtered, "Query Type")
        fig = px.pie(qt_dist, values="Count", names="Query Type",
                     color_discrete_sequence=COLORS, hole=0.4)
        fig.update_traces(textposition="outside", textinfo="percent+label",
                          textfont_size=11)
        fig.update_layout(height=550, margin=dict(t=40, b=80, l=80, r=80))
        st.plotly_chart(fig, use_container_width=True)

    # ── TAB 2: Cohort Analysis ──
    with tab2:
        cohort_option = st.selectbox(
            "Select Cohort Dimension",
            ["gender", "age_range", "education", "zone", "income_bucket"],
            format_func=lambda x: {
                "gender": "Gender",
                "age_range": "Age Range",
                "education": "Education Level",
                "zone": "Zone",
                "income_bucket": "Income Bucket"
            }.get(x, x)
        )

        st.subheader(f"Issue Volume by {cohort_option.replace('_', ' ').title()}")
        cohort_dist = an.get_cohort_split(filtered, cohort_option)
        fig = px.bar(cohort_dist, x=cohort_option, y="Count",
                     text="Percentage", color=cohort_option,
                     color_discrete_sequence=COLORS)
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(height=400, showlegend=False,
                          margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # Top 10 Sub-Category × Cohort
        st.subheader(f"Top 10 Sub-Category × {cohort_option.replace('_', ' ').title()}")
        ct_sub, ct_sub_pct = an.get_subcategory_by_cohort(filtered, cohort_option, top_n=10)
        fig = px.imshow(ct_sub.T, text_auto=True, aspect="auto",
                        color_continuous_scale="YlOrRd",
                        labels=dict(x=cohort_option.replace("_", " ").title(),
                                    y="Sub Category", color="Count"))
        fig.update_layout(height=450, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # Heatmap: Category × Cohort
        st.subheader(f"Issue Heatmap: Category × {cohort_option.replace('_', ' ').title()}")
        ct, _ = an.get_category_by_cohort(filtered, cohort_option)
        fig = px.imshow(ct.T, text_auto=True, aspect="auto",
                        color_continuous_scale="YlOrRd",
                        labels=dict(x=cohort_option.replace("_", " ").title(),
                                    y="Category", color="Count"))
        fig.update_layout(height=400, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── TAB 3: Trends ──
    with tab3:
        st.subheader("Monthly Issue Volume")
        monthly = an.get_monthly_trend(filtered)
        fig = px.line(monthly, x="month", y="Count", markers=True,
                      line_shape="spline")
        fig.update_layout(height=350, xaxis_title="Month", yaxis_title="Issue Count",
                          margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Monthly Trend by Category")
        cat_monthly = an.get_category_monthly_trend(filtered)
        fig = px.line(cat_monthly, x="month", y="Count", color="Category",
                      markers=True, color_discrete_sequence=COLORS)
        fig.update_layout(height=450, xaxis_title="Month", yaxis_title="Issue Count",
                          margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── TAB 5: Key Insights ──
    with tab5:
        st.subheader("💡 Key Insights — Complaint Analysis")
        st.markdown("---")

        # Compute stats from full df1 (not filtered)
        _cat_dist = an.get_category_distribution(df1)
        _top_cat = _cat_dist.iloc[0]
        _second_cat = _cat_dist.iloc[1] if len(_cat_dist) > 1 else None
        _src_dist = an.get_source_distribution(df1)
        _top_src = _src_dist.iloc[0]
        _sub_dist = an.get_subcategory_distribution(df1, top_n=5)
        _top_sub = _sub_dist.iloc[0]
        _age_dist = an.get_cohort_split(df1, "age_range")
        _top_age = _age_dist.iloc[0]

        # Insight cards
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("""
            <div style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">🔥 Payment issues are the #1 problem</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    <b>{cat}</b> makes up <b>{pct}%</b> of all complaints ({cnt:,} tickets).
                    Within this, "<i>Payment Not Updated</i>" alone drives <b>{sub_pct}%</b> of total volume.
                    Customers pay but don't see it reflected — that's the single biggest pain point.
                </p>
            </div>
            """.format(
                cat=_top_cat['Category'], pct=_top_cat['Percentage'],
                cnt=_top_cat['Count'], sub_pct=_top_sub['Percentage']
            ), unsafe_allow_html=True)

            st.markdown("""
            <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">📧 Email dominates as support channel</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    <b>{pct}%</b> of complaints come through <b>{src}</b>.
                    Phone is a distant second at ~10%. This is typical for a digital lending product
                    — users prefer written communication they can reference later.
                </p>
            </div>
            """.format(src=_top_src['Source'], pct=_top_src['Percentage']), unsafe_allow_html=True)

            st.markdown("""
            <div style="background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">📊 Two categories = 57% of all complaints</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    {cat1} ({pct1}%) and {cat2} ({pct2}%) together make up
                    over half of all complaints. This concentration is actually helpful —
                    fixing just two areas could dramatically reduce ticket volume.
                </p>
            </div>
            """.format(
                cat1=_top_cat['Category'], pct1=_top_cat['Percentage'],
                cat2=_second_cat['Category'] if _second_cat is not None else "N/A",
                pct2=_second_cat['Percentage'] if _second_cat is not None else 0
            ), unsafe_allow_html=True)

        with col_b:
            st.markdown("""
            <div style="background: #fce4ec; border-left: 4px solid #e91e63; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">⚠️ Collection practices cause friction</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    Collection-related complaints ({pct}%) include "Promise To Pay Denied"
                    and penalty charge disputes. Users feel pressured — this matches
                    the harassment concerns seen in Play Store reviews too.
                </p>
            </div>
            """.format(
                pct=_second_cat['Percentage'] if _second_cat is not None else 0
            ), unsafe_allow_html=True)

            st.markdown("""
            <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">🏠 Foreclosure demand is notable</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    About <b>10.8%</b> of complaints are foreclosure-related. Both eligible
                    and ineligible users are asking about early closure — either loan terms
                    aren't communicated well enough, or users just want more flexibility.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background: #fff8e1; border-left: 4px solid #ffc107; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">📌 Young borrowers (25-33) file the most complaints</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    The <b>{age}</b> age group generates <b>{pct}%</b> of all complaints.
                    They're likely the core user base and also the most digitally active,
                    so they're quicker to raise issues when something goes wrong.
                </p>
            </div>
            """.format(age=_top_age['age_range'], pct=_top_age['Percentage']), unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 💡 Bottom line")
        st.info(
            "Payment reconciliation delays and collection-related friction are the two "
            "biggest drivers of complaint volume. Fixing real-time payment status updates "
            "alone could eliminate ~25% of all incoming tickets."
        )


# ═════════════════════════════════════════════
# PAGE: Data-2 Reviews Dashboard
# ═════════════════════════════════════════════
elif page == "⭐ Data-2: Reviews":
    st.title("⭐ Data-2: Google Reviews Analysis")
    st.markdown(f"**Total reviews:** {len(df2):,}")

    # Filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filters")

    sentiments = ["All"] + sorted(df2["sentiment"].unique().tolist())
    sel_sentiment = st.sidebar.selectbox("Sentiment", sentiments)

    # Apply sentiment filter first, then build theme list from filtered data
    _sentiment_filtered = df2.copy()
    if sel_sentiment != "All":
        _sentiment_filtered = _sentiment_filtered[_sentiment_filtered["sentiment"] == sel_sentiment]

    # Theme list updates based on selected sentiment
    theme_list = ["All"] + sorted(_sentiment_filtered["theme"].dropna().unique().tolist())
    sel_theme = st.sidebar.selectbox("Theme", theme_list)

    # Demographic filters
    st.sidebar.markdown("**Demographics**")

    d2_ages = ["All"] + sorted(df2["age_range"].dropna().unique().tolist())
    d2_sel_age = st.sidebar.selectbox("Age Range", d2_ages, key="d2_age")

    d2_zones = ["All"] + sorted(df2["zone"].dropna().unique().tolist())
    d2_sel_zone = st.sidebar.selectbox("Zone", d2_zones, key="d2_zone")

    d2_edus = ["All"] + sorted(df2["education"].dropna().unique().tolist())
    d2_sel_edu = st.sidebar.selectbox("Education Level", d2_edus, key="d2_edu")

    d2_incomes = ["All"] + sorted(df2["income_bucket"].dropna().unique().tolist())
    d2_sel_income = st.sidebar.selectbox("Income Bucket", d2_incomes, key="d2_income")

    # Apply all filters
    filtered2 = _sentiment_filtered.copy()
    if sel_theme != "All":
        filtered2 = filtered2[filtered2["theme"] == sel_theme]
    if d2_sel_age != "All":
        filtered2 = filtered2[filtered2["age_range"] == d2_sel_age]
    if d2_sel_zone != "All":
        filtered2 = filtered2[filtered2["zone"] == d2_sel_zone]
    if d2_sel_edu != "All":
        filtered2 = filtered2[filtered2["education"] == d2_sel_edu]
    if d2_sel_income != "All":
        filtered2 = filtered2[filtered2["income_bucket"] == d2_sel_income]

    st.markdown(f"**Filtered reviews:** {len(filtered2):,}")

    # Overall Sentiment Scorecard
    st.markdown("### 📊 Sentiment Scorecard")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        avg_rating = filtered2["rating"].mean()
        st.metric("Avg Rating", f"{avg_rating:.2f} ⭐")
    with col2:
        pos_count = (filtered2["sentiment"] == "Positive").sum()
        st.metric("Positive", f"{pos_count:,} ({pos_count/max(len(filtered2),1)*100:.1f}%)")
    with col3:
        neg_count = (filtered2["sentiment"] == "Negative").sum()
        st.metric("Negative", f"{neg_count:,} ({neg_count/max(len(filtered2),1)*100:.1f}%)")
    with col4:
        avg_sent = filtered2["sentiment_score"].mean()
        st.metric("Avg Sentiment Score", f"{avg_sent:.3f}")
    with col5:
        five_star = (filtered2["rating"] == 5).sum()
        st.metric("5-Star Reviews", f"{five_star:,} ({five_star/max(len(filtered2),1)*100:.1f}%)")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Sentiment", "🏷️ Themes", "👥 Cohort Analysis", "📝 Reviews", "💡 Key Insights"
    ])

    # ── TAB 1: Sentiment ──
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Rating Distribution")
            rating_dist = an.get_rating_distribution(filtered2)
            fig = px.bar(rating_dist, x="Rating", y="Count",
                         text="Percentage",
                         color="Rating", color_continuous_scale="RdYlGn")
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(height=400, coloraxis_showscale=False,
                              xaxis_title="Rating (Stars)", yaxis_title="Count",
                              margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Sentiment Split (1-2 Neg / 3-5 Pos)")
            sent_dist = an.get_sentiment_distribution(filtered2)
            fig = px.pie(sent_dist, values="Count", names="Sentiment",
                         color="Sentiment", color_discrete_map=NEG_POS_COLORS,
                         hole=0.45)
            fig.update_traces(textposition="outside", textinfo="percent+label",
                              textfont_size=11)
            fig.update_layout(height=550, margin=dict(t=40, b=80, l=80, r=80))
            st.plotly_chart(fig, use_container_width=True)

        # Diverging Stacked Bar Chart for sentiment score distribution
        st.subheader("Sentiment Score Distribution (Diverging)")
        df_scores = filtered2.copy()
        # Bin sentiment scores
        bins = [-1, -0.5, -0.2, -0.05, 0.05, 0.2, 0.5, 1]
        labels_bins = ["Very Negative\n(-1 to -0.5)", "Negative\n(-0.5 to -0.2)",
                       "Slightly Negative\n(-0.2 to -0.05)", "Neutral\n(-0.05 to 0.05)",
                       "Slightly Positive\n(0.05 to 0.2)", "Positive\n(0.2 to 0.5)",
                       "Very Positive\n(0.5 to 1)"]
        df_scores["score_bin"] = pd.cut(df_scores["sentiment_score"], bins=bins, labels=labels_bins)
        bin_counts = df_scores["score_bin"].value_counts().reindex(labels_bins).fillna(0)

        colors_diverging = ["#d73027", "#f46d43", "#fdae61", "#ffffbf", "#a6d96a", "#66bd63", "#1a9850"]

        fig = go.Figure()
        for i, (label, count) in enumerate(bin_counts.items()):
            # Negative scores go left, positive go right
            if i < 3:
                fig.add_trace(go.Bar(
                    y=["Sentiment Distribution"],
                    x=[-count],
                    name=label, orientation="h",
                    marker_color=colors_diverging[i],
                    text=f"{int(count)}", textposition="inside"
                ))
            elif i == 3:
                fig.add_trace(go.Bar(
                    y=["Sentiment Distribution"],
                    x=[count if count > 0 else 0.5],
                    name=label, orientation="h",
                    marker_color=colors_diverging[i],
                    text=f"{int(count)}", textposition="inside"
                ))
            else:
                fig.add_trace(go.Bar(
                    y=["Sentiment Distribution"],
                    x=[count],
                    name=label, orientation="h",
                    marker_color=colors_diverging[i],
                    text=f"{int(count)}", textposition="inside"
                ))

        fig.update_layout(
            barmode="relative",
            height=200,
            xaxis_title="← Negative | Positive →",
            yaxis_title="",
            legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5),
            margin=dict(t=10, b=80, l=10, r=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── TAB 2: Themes ──
    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Theme Distribution")
            theme_dist = an.get_theme_distribution(filtered2)
            fig = px.bar(theme_dist, x="Count", y="Theme", orientation="h",
                         text="Percentage", color="Theme",
                         color_discrete_sequence=COLORS)
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(height=450, showlegend=False,
                              yaxis=dict(categoryorder="total ascending"),
                              margin=dict(l=10, r=60, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Theme × Sentiment")
            ct, ct_pct = an.get_theme_sentiment_cross(filtered2)
            fig = px.bar(ct_pct.reset_index(), x="theme",
                         y=[c for c in ct_pct.columns if c in NEG_POS_COLORS],
                         barmode="stack",
                         color_discrete_map=NEG_POS_COLORS)
            fig.update_layout(height=450, xaxis_title="Theme",
                              yaxis_title="Percentage (%)",
                              legend_title="Sentiment",
                              margin=dict(t=10, b=10))
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        # Theme details
        st.subheader("Theme Details")
        selected_theme = st.selectbox("Select a theme to explore",
                                      filtered2["theme"].unique().tolist())
        theme_reviews = filtered2[filtered2["theme"] == selected_theme]
        st.markdown(f"**Reviews in this theme:** {len(theme_reviews)}")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Sample Positive Reviews:**")
            pos_samples = theme_reviews[theme_reviews["sentiment"] == "Positive"]["content"].head(5)
            if len(pos_samples) == 0:
                st.info("No positive reviews in this theme.")
            for i, review in enumerate(pos_samples, 1):
                st.markdown(f"{i}. _{str(review)[:200]}_")
        with col_b:
            st.markdown("**Sample Negative Reviews:**")
            neg_samples = theme_reviews[theme_reviews["sentiment"] == "Negative"]["content"].head(5)
            if len(neg_samples) == 0:
                st.info("No negative reviews in this theme.")
            for i, review in enumerate(neg_samples, 1):
                st.markdown(f"{i}. _{str(review)[:200]}_")

    # ── TAB 3: Cohort Analysis ──
    with tab3:
        cohort_option2 = st.selectbox(
            "Select Cohort Dimension",
            ["education", "zone", "age_range", "income_bucket"],
            format_func=lambda x: x.replace("_", " ").title(),
            key="cohort_d2"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Review Volume by {cohort_option2.replace('_', ' ').title()}")
            cohort_dist = filtered2[cohort_option2].value_counts().reset_index()
            cohort_dist.columns = [cohort_option2, "Count"]
            fig = px.bar(cohort_dist, x=cohort_option2, y="Count",
                         color=cohort_option2, color_discrete_sequence=COLORS,
                         text_auto=True)
            fig.update_layout(height=400, showlegend=False,
                              margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader(f"Sentiment by {cohort_option2.replace('_', ' ').title()}")
            ct, ct_pct = an.get_sentiment_by_cohort(filtered2, cohort_option2)
            fig = px.bar(ct_pct.reset_index(), x=cohort_option2,
                         y=[c for c in ct_pct.columns if c in NEG_POS_COLORS],
                         barmode="stack",
                         color_discrete_map=NEG_POS_COLORS)
            fig.update_layout(height=400, yaxis_title="Percentage (%)",
                              legend_title="Sentiment",
                              margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

    # ── TAB 4: Reviews Browser ──
    with tab4:
        st.subheader("Browse Reviews")

        # Sort options
        sort_col = st.selectbox("Sort by", ["rating", "sentiment_score", "review_date"])
        sort_asc = st.checkbox("Ascending", value=False)

        display_cols = ["content", "rating", "sentiment", "sentiment_score",
                        "theme", "age_range", "income_bucket", "education", "zone"]
        display_df = filtered2[[c for c in display_cols if c in filtered2.columns]].copy()
        display_df = display_df.sort_values(sort_col, ascending=sort_asc)
        st.dataframe(display_df, use_container_width=True, height=500)

    # ── TAB 5: Key Insights ──
    with tab5:
        st.subheader("💡 Key Insights — Reviews Analysis")
        st.markdown("---")

        # Compute stats from full df2
        _pos_count = (df2["sentiment"] == "Positive").sum()
        _neg_count = (df2["sentiment"] == "Negative").sum()
        _pos_pct = _pos_count / len(df2) * 100
        _neg_pct = _neg_count / len(df2) * 100
        _five_star = (df2["rating"] == 5).sum()
        _five_pct = _five_star / len(df2) * 100
        _one_star = (df2["rating"] == 1).sum()
        _one_pct = _one_star / len(df2) * 100
        _avg_rating = df2["rating"].mean()

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("""
            <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">✅ Overall sentiment is strongly positive</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    <b>{pos_pct:.0f}%</b> of reviews are positive ({pos:,} out of {total:,}).
                    Average rating is <b>{avg:.1f} ⭐</b>. The app is generally well-received
                    by its user base.
                </p>
            </div>
            """.format(pos_pct=_pos_pct, pos=_pos_count, total=len(df2), avg=_avg_rating),
            unsafe_allow_html=True)

            st.markdown("""
            <div style="background: #fce4ec; border-left: 4px solid #e91e63; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">🔴 Negatives are extreme — almost all 1-star</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    Of the <b>{neg:,}</b> negative reviews ({neg_pct:.1f}%),
                    <b>{one:,}</b> are 1-star ({one_pct:.0f}% of total).
                    There's almost no middle ground — users are either very happy
                    or very unhappy. Very few 2-3 star ratings exist.
                </p>
            </div>
            """.format(neg=_neg_count, neg_pct=_neg_pct, one=_one_star, one_pct=_one_pct),
            unsafe_allow_html=True)

            st.markdown("""
            <div style="background: #f3e5f5; border-left: 4px solid #9c27b0; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">📉 Older users (42+) are the most dissatisfied</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    The 42+ age group has a <b>17.2%</b> negative rate — more than double
                    the 7% seen in younger groups. This segment may need a different
                    support approach (phone callbacks vs. self-service).
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown("""
            <div style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">⚡ Negative reviews mention harassment & scams</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    The harshest reviews consistently mention "harassment", "mental torture",
                    "unethical practices", and "scammers" — mostly tied to collection
                    follow-ups. Even if these are a small minority, they're publicly visible
                    and damaging to the brand.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">🏷️ "App Experience" is the dominant theme</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    About <b>79%</b> of reviews fall under "App Experience" —
                    the remaining split between "Positive Feedback" (17%) and
                    "Loan Process" (4.5%). Most users are commenting on the
                    app itself rather than loan terms.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background: #fff8e1; border-left: 4px solid #ffc107; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
                <h4 style="margin:0 0 8px 0;">💰 Mid-income users are surprisingly unhappy</h4>
                <p style="margin:0; font-size: 0.95rem;">
                    The ₹75K-1L income bracket has a <b>22.2%</b> negative rate —
                    the highest of any income segment. Lower and higher income groups
                    are more satisfied. This mid-tier group may have higher
                    expectations that aren't being met.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 💡 Bottom line")
        st.info(
            "The Play Store picture is largely positive (91% favorable), "
            "but the negative reviews are disproportionately loud and damaging. "
            "Collection-related complaints mirror what's seen in Data-1 — "
            "softening collection practices would improve both internal complaint metrics "
            "and public-facing ratings."
        )


# ═════════════════════════════════════════════
# PAGE: Crosstab Analysis
# ═════════════════════════════════════════════
elif page == "📊 Crosstab Analysis":
    st.title("📊 Crosstab Analysis")
    st.markdown("Pre-computed percentage breakdowns from crosstab analysis with color-coded heatmaps.")

    ct1_d1, ct2_d1, ct1_d2 = load_crosstabs()

    # ── Helper: Parse crosstab CSV into structured sections ──
    def parse_crosstab_sections(df_raw):
        """Parse a raw crosstab CSV into named sections with proper headers."""
        sections = {}
        current_section = None
        header_row = None
        data_rows = []

        for idx, row in df_raw.iterrows():
            values = row.tolist()
            non_empty = [v for v in values if pd.notna(v) and str(v).strip() != ""]

            # Detect section headers (single non-empty value in first column, rest empty)
            if len(non_empty) == 1 and idx > 2:
                # Save previous section
                if current_section and data_rows:
                    sections[current_section] = pd.DataFrame(data_rows, columns=header_row)
                current_section = str(non_empty[0]).strip()
                data_rows = []
            elif idx <= 3:
                # Header rows (title, group headers, column names, base)
                if idx == 2:
                    header_row = [str(v).strip() if pd.notna(v) else "" for v in values]
                elif idx == 3:
                    if current_section is None:
                        current_section = "Base"
                    data_rows.append([str(v).strip() if pd.notna(v) else "" for v in values])
            else:
                if current_section:
                    data_rows.append([str(v).strip() if pd.notna(v) else "" for v in values])

        # Save last section
        if current_section and data_rows:
            sections[current_section] = pd.DataFrame(data_rows, columns=header_row)

        return sections

    def pct_to_float(val):
        """Convert percentage string to float for coloring."""
        try:
            s = str(val).strip().replace("%", "").replace(",", "")
            return float(s)
        except (ValueError, TypeError):
            return None

    def ensure_unique_columns(df):
        """Ensure all column names are unique by appending suffixes to duplicates."""
        cols = list(df.columns)
        seen = {}
        new_cols = []
        for c in cols:
            if c in seen:
                seen[c] += 1
                new_cols.append(f"{c}_{seen[c]}" if c else f"Col_{seen[c]}")
            else:
                seen[c] = 0
                new_cols.append(c if c else "Item")
        return new_cols

    def style_pct_table(df, skip_first_col=True):
        """Apply gradient background to percentage columns using HTML table."""
        def color_pct_style(val):
            f = pct_to_float(val)
            if f is None:
                return ""
            if f >= 50:
                return f"background-color: rgba(102, 126, 234, {f/100*0.7 + 0.1}); color: white; font-weight: 600"
            elif f >= 20:
                return f"background-color: rgba(102, 126, 234, {f/100*0.5 + 0.05}); color: #1a1a2e"
            elif f >= 10:
                return f"background-color: rgba(102, 126, 234, {f/100*0.4}); color: #333"
            elif f > 0:
                return f"background-color: rgba(102, 126, 234, 0.05); color: #666"
            else:
                return "color: #ccc"

        # Build HTML table manually to avoid Styler issues with non-unique columns
        html = '<div style="overflow-x: auto;"><table style="width:100%; border-collapse: collapse; font-size: 0.85rem;">'

        # Header row
        html += '<tr>'
        for i, col in enumerate(df.columns):
            bg = "#667eea" if i > 0 or not skip_first_col else "#4a4a6a"
            html += f'<th style="padding: 8px 12px; background-color: {bg}; color: white; text-align: center; border: 1px solid #ddd; white-space: nowrap;">{col}</th>'
        html += '</tr>'

        # Data rows
        for _, row in df.iterrows():
            html += '<tr>'
            for i, val in enumerate(row):
                val_str = str(val).strip() if pd.notna(val) and str(val).strip() not in ["nan"] else ""
                if i == 0 and skip_first_col:
                    html += f'<td style="padding: 6px 12px; font-weight: 600; background-color: #f8f9fa; text-align: left; border: 1px solid #eee; white-space: nowrap; min-width: 180px;">{val_str}</td>'
                else:
                    style = color_pct_style(val_str)
                    html += f'<td style="padding: 6px 10px; text-align: center; border: 1px solid #eee; {style}">{val_str}</td>'
            html += '</tr>'

        html += '</table></div>'
        return html

    def render_section_as_heatmap(section_name, df_section, icon="📊"):
        """Render a crosstab section as a styled heatmap HTML table."""
        if df_section is None or df_section.empty:
            return

        # Clean column names - ensure unique
        df_display = df_section.copy()
        df_display.columns = ensure_unique_columns(df_display)

        # Remove fully empty rows
        df_display = df_display.dropna(how="all")
        df_display = df_display[df_display.apply(lambda row: any(str(v).strip() not in ["", "nan"] for v in row), axis=1)]

        if df_display.empty:
            return

        st.markdown(f"#### {icon} {section_name}")
        html_table = style_pct_table(df_display)
        st.markdown(html_table, unsafe_allow_html=True)

    # ── Helper: Parse Data-1 Crosstab 2 (different structure) ──
    def parse_crosstab2(df_raw):
        """Parse crosstab2 which has Category and Sub-Category as column groups."""
        sections = {}
        current_section = None
        data_rows = []
        # Row 0: group headers, Row 1: column names, Row 2: counts
        col_names = [str(v).strip() if pd.notna(v) else "" for v in df_raw.iloc[1].tolist()]

        for idx in range(2, len(df_raw)):
            row = df_raw.iloc[idx]
            values = [str(v).strip() if pd.notna(v) else "" for v in row.tolist()]
            non_empty = [v for v in values if v not in ["", "nan"]]

            if len(non_empty) == 1 and values[0] not in ["", "nan"]:
                if current_section and data_rows:
                    sections[current_section] = pd.DataFrame(data_rows, columns=col_names)
                current_section = values[0]
                data_rows = []
            elif non_empty:
                data_rows.append(values)

        if current_section and data_rows:
            sections[current_section] = pd.DataFrame(data_rows, columns=col_names)

        return sections, col_names

    # ── Helper: Parse Data-2 Crosstab ──
    def parse_crosstab_d2(df_raw):
        """Parse Data-2 crosstab with Sentiment, Rating, Theme sections."""
        sections = {}
        current_section = None
        data_rows = []
        # Row 2: column names (Value, Total, zone groups, age groups, etc.)
        header_row = [str(v).strip() if pd.notna(v) else "" for v in df_raw.iloc[2].tolist()]

        for idx in range(3, len(df_raw)):
            row = df_raw.iloc[idx]
            values = [str(v).strip() if pd.notna(v) else "" for v in row.tolist()]
            non_empty = [v for v in values if v not in ["", "nan"]]

            if len(non_empty) == 1 and values[0] not in ["", "nan"]:
                if current_section and data_rows:
                    sections[current_section] = pd.DataFrame(data_rows, columns=header_row)
                current_section = values[0]
                data_rows = []
            elif non_empty:
                data_rows.append(values)

        if current_section and data_rows:
            sections[current_section] = pd.DataFrame(data_rows, columns=header_row)

        return sections, header_row

    # ── Tab Layout ──
    tab_ct1, tab_ct2, tab_ct3 = st.tabs([
        "📋 Data-1: Overall Crosstab", "📋 Data-1: Category Breakdown", "⭐ Data-2: Reviews Crosstab"
    ])

    # ══════════════════════════════════════
    # TAB 1: Data-1 Overall Crosstab
    # ══════════════════════════════════════
    with tab_ct1:
        st.subheader("Data-1: Complaint Query Crosstab")
        st.markdown("Percentage breakdown of **Query Type, Source, Category, Sub-Category** across demographic cohorts.")

        # Column group info
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
                    padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;
                    border-left: 4px solid #667eea;">
            <b>Cohort Groups:</b>
            👤 <b>Gender</b> (M, F, O, Unknown) &nbsp;│&nbsp;
            📅 <b>Age</b> (Below 21 to 42+) &nbsp;│&nbsp;
            🗺️ <b>Zone</b> (South, North, East, West, Central, Other, North East) &nbsp;│&nbsp;
            🎓 <b>Education</b> (Graduate, Below Graduate, Other) &nbsp;│&nbsp;
            💰 <b>Income</b> (Low to Ultra HNI)
        </div>
        """, unsafe_allow_html=True)

        sections = parse_crosstab_sections(ct1_d1)

        section_icons = {
            "Base": "📊", "Query Type": "❓", "Source": "📱",
            "Category": "📂", "Sub Category": "📋"
        }

        for section_name, section_df in sections.items():
            icon = section_icons.get(section_name, "📊")

            if section_name == "Sub Category":
                with st.expander(f"{icon} {section_name} (click to expand — {len(section_df)} items)", expanded=False):
                    render_section_as_heatmap(section_name, section_df, "📋")
            else:
                render_section_as_heatmap(section_name, section_df, icon)

            if section_name != list(sections.keys())[-1]:
                st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #eee;'>",
                            unsafe_allow_html=True)

        st.download_button(
            label="📥 Download Full Crosstab (CSV)",
            data=ct1_d1.to_csv(index=False, header=False),
            file_name="crosstab1_data1.csv",
            mime="text/csv"
        )

    # ══════════════════════════════════════
    # TAB 2: Data-1 Category Breakdown
    # ══════════════════════════════════════
    with tab_ct2:
        st.subheader("Data-1: Category & Sub-Category Breakdown")
        st.markdown("Percentage breakdown of **Source** and **Query Type** across each Category and Top Sub-Categories.")

        ct2_sections, ct2_cols = parse_crosstab2(ct2_d1)

        # Show the counts row first
        if ct2_d1.shape[0] > 2:
            counts_row = ct2_d1.iloc[2].tolist()
            col_labels = ct2_d1.iloc[1].tolist()

            # Build a nice summary of categories and their counts
            categories_info = []
            for i, (label, count) in enumerate(zip(col_labels, counts_row)):
                if pd.notna(label) and str(label).strip() and pd.notna(count) and str(count).strip():
                    categories_info.append((str(label).strip(), str(count).strip()))

            if categories_info:
                st.markdown("#### 📊 Volume Overview")
                # Display counts as metric cards
                cols = st.columns(min(len(categories_info), 5))
                for i, (cat, count) in enumerate(categories_info[:10]):
                    col_idx = i % min(len(categories_info), 5)
                    with cols[col_idx]:
                        st.metric(cat, count)

        st.markdown("---")

        for section_name, section_df in ct2_sections.items():
            icon = "📱" if section_name == "Source" else "❓"
            render_section_as_heatmap(section_name, section_df, icon)
            st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #eee;'>",
                        unsafe_allow_html=True)

        st.download_button(
            label="📥 Download Category Breakdown (CSV)",
            data=ct2_d1.to_csv(index=False, header=False),
            file_name="crosstab2_data1.csv",
            mime="text/csv"
        )

    # ══════════════════════════════════════
    # TAB 3: Data-2 Reviews Crosstab
    # ══════════════════════════════════════
    with tab_ct3:
        st.subheader("Data-2: Google Reviews Crosstab")
        st.markdown("Percentage breakdown of **Sentiment, Ratings, Themes** across demographic cohorts.")

        # Cohort info
        st.markdown("""
        <div style="background: linear-gradient(135deg, #43e97b15 0%, #38f9d715 100%);
                    padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;
                    border-left: 4px solid #43e97b;">
            <b>Cohort Groups:</b>
            🗺️ <b>Zone</b> (South, North, West, East) &nbsp;│&nbsp;
            📅 <b>Age</b> (Below 21 to 42+) &nbsp;│&nbsp;
            🎓 <b>Education</b> (Graduate, Below Graduate) &nbsp;│&nbsp;
            💰 <b>Income</b> (Low to Ultra HNI)
        </div>
        """, unsafe_allow_html=True)

        # Base info
        if ct1_d2.shape[0] > 3:
            base_row = ct1_d2.iloc[3].tolist()
            total_reviews = str(base_row[1]).strip() if len(base_row) > 1 else "N/A"
            st.markdown(f"**Total Reviews:** {total_reviews}")

        d2_sections, d2_cols = parse_crosstab_d2(ct1_d2)

        section_icons_d2 = {
            "Sentiment": "😊", "Rating (1-5 star)": "⭐",
            "Sentiment - Positive": "✅", "Sentiment - Negetive": "❌"
        }

        for section_name, section_df in d2_sections.items():
            icon = section_icons_d2.get(section_name, "📊")

            # Use green/red styling for sentiment sections
            render_section_as_heatmap(section_name, section_df, icon)

            if section_name != list(d2_sections.keys())[-1]:
                st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #eee;'>",
                            unsafe_allow_html=True)

        st.download_button(
            label="📥 Download Reviews Crosstab (CSV)",
            data=ct1_d2.to_csv(index=False, header=False),
            file_name="crosstab1_data2.csv",
            mime="text/csv"
        )


# ═════════════════════════════════════════════
# PAGE: Report
# ═════════════════════════════════════════════
elif page == "📝 Report":
    st.title("📝 Analysis Report")
    st.markdown("Auto-generated comprehensive report from both datasets.")

    report_text = an.generate_report(df1, df2)

    # Display report
    st.markdown(report_text)

    # Download button
    st.download_button(
        label="📥 Download Report (Markdown)",
        data=report_text,
        file_name="xyz_loan_app_analysis_report.md",
        mime="text/markdown"
    )

    # Also save to file
    if st.button("💾 Save Report to File"):
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report_text)
        st.success("Report saved to `report.md`")


# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='text-align:center; color:#888; font-size:0.8rem;'>"
    "XYZ Loan App Analysis Dashboard<br>"
    "Built with Streamlit + Plotly</p>",
    unsafe_allow_html=True
)