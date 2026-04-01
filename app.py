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

    # Category filter
    categories = ["All"] + sorted(df1["Category"].unique().tolist())
    sel_category = st.sidebar.selectbox("Category", categories)

    # Source filter
    sources = ["All"] + sorted(df1["Source"].unique().tolist())
    sel_source = st.sidebar.selectbox("Source Channel", sources)

    # Zone filter
    zones = ["All"] + sorted(df1["zone"].unique().tolist())
    sel_zone = st.sidebar.selectbox("Zone", zones)

    # Apply filters
    filtered = df1.copy()
    if sel_category != "All":
        filtered = filtered[filtered["Category"] == sel_category]
    if sel_source != "All":
        filtered = filtered[filtered["Source"] == sel_source]
    if sel_zone != "All":
        filtered = filtered[filtered["zone"] == sel_zone]

    st.markdown(f"**Filtered records:** {len(filtered):,}")

    # ── Tab Layout ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Issue Splits", "👥 Cohort Analysis", "📈 Trends", "🔍 Deep Dive"
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

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Issue Volume by {cohort_option.replace('_', ' ').title()}")
            cohort_dist = an.get_cohort_split(filtered, cohort_option)
            fig = px.bar(cohort_dist, x=cohort_option, y="Count",
                         text="Percentage", color=cohort_option,
                         color_discrete_sequence=COLORS)
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(height=400, showlegend=False,
                              margin=dict(t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader(f"Category Breakdown by {cohort_option.replace('_', ' ').title()}")
            ct, ct_pct = an.get_category_by_cohort(filtered, cohort_option)
            fig = px.bar(ct_pct.reset_index(), x=cohort_option,
                         y=ct_pct.columns.tolist(),
                         barmode="stack", color_discrete_sequence=COLORS)
            fig.update_layout(height=400, yaxis_title="Percentage (%)",
                              legend_title="Category",
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

    # ── TAB 4: Deep Dive ──
    with tab4:
        st.subheader("Query Type Split")
        qt_dist = an.get_cohort_split(filtered, "Query Type")
        fig = px.pie(qt_dist, values="Count", names="Query Type",
                     color_discrete_sequence=COLORS, hole=0.4)
        fig.update_traces(textposition="outside", textinfo="percent+label",
                          textfont_size=11)
        fig.update_layout(height=550, margin=dict(t=40, b=80, l=80, r=80))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sample Data")
        st.dataframe(filtered.head(100), use_container_width=True, height=400)


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

    theme_list = ["All"] + sorted(df2["theme"].dropna().unique().tolist())
    sel_theme = st.sidebar.selectbox("Theme", theme_list)

    filtered2 = df2.copy()
    if sel_sentiment != "All":
        filtered2 = filtered2[filtered2["sentiment"] == sel_sentiment]
    if sel_theme != "All":
        filtered2 = filtered2[filtered2["theme"] == sel_theme]

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
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Sentiment", "🏷️ Themes", "👥 Cohort Analysis", "📝 Reviews"
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


# ═════════════════════════════════════════════
# PAGE: Crosstab Analysis
# ═════════════════════════════════════════════
elif page == "📊 Crosstab Analysis":
    st.title("📊 Crosstab Analysis")
    st.markdown("Pre-computed percentage breakdowns from crosstab analysis.")

    ct1_d1, ct2_d1, ct1_d2 = load_crosstabs()

    tab_ct1, tab_ct2, tab_ct3 = st.tabs([
        "📋 Data-1: Overall Crosstab", "📋 Data-1: Category Breakdown", "⭐ Data-2: Reviews Crosstab"
    ])

    with tab_ct1:
        st.subheader("Data-1: Complaint Query Crosstab (Overall x Cohorts)")
        st.markdown("Shows percentage breakdown of Query Type, Source, Category, and Sub-Category across Gender, Age, Zone, Education, and Income cohorts.")
        st.dataframe(ct1_d1, use_container_width=True, height=800, hide_index=True)

        st.download_button(
            label="📥 Download Crosstab 1 (CSV)",
            data=ct1_d1.to_csv(index=False, header=False),
            file_name="crosstab1_data1.csv",
            mime="text/csv"
        )

    with tab_ct2:
        st.subheader("Data-1: Category & Sub-Category Breakdown")
        st.markdown("Shows percentage breakdown of Source and Query Type across each Category and Top 10 Sub-Categories.")
        st.dataframe(ct2_d1, use_container_width=True, height=500, hide_index=True)

        st.download_button(
            label="📥 Download Crosstab 2 (CSV)",
            data=ct2_d1.to_csv(index=False, header=False),
            file_name="crosstab2_data1.csv",
            mime="text/csv"
        )

    with tab_ct3:
        st.subheader("Data-2: Google Reviews Crosstab (Sentiment, Rating, Theme x Cohorts)")
        st.markdown("Shows percentage breakdown of Sentiment, Ratings, and Themes across Zone, Age, Education, and Income cohorts.")
        st.dataframe(ct1_d2, use_container_width=True, height=600, hide_index=True)

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