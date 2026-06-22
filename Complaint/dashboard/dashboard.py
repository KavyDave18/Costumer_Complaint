import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# =========================================================
# CUSTOM STYLING (UNCHANGED)
# =========================================================

st.markdown("""<style>
.main { padding-top: 2rem; }

.kpi-container {
    display:flex; flex-direction:column; justify-content:center;
    padding:1.5rem;
    background:linear-gradient(135deg,#f8f9fa 0%,#ffffff 100%);
    border-radius:12px;
    border:1px solid #e9ecef;
    box-shadow:0 2px 8px rgba(0,0,0,0.05);
}

.kpi-label {
    font-size:0.875rem;
    color:#6c757d;
    font-weight:500;
    letter-spacing:0.5px;
    margin-bottom:0.5rem;
    text-transform:uppercase;
}

.kpi-value {
    font-size:1.75rem;
    font-weight:700;
    color:#212529;
}

.section-header {
    margin-top:2.5rem;
    margin-bottom:1.5rem;
    padding-bottom:1rem;
    border-bottom:2px solid #e9ecef;
}
.section-header h2 {
    margin:0;
    color:#212529;
    font-size:1.5rem;
    font-weight:700;
}
</style>""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("## 📊")
with col2:
    st.markdown("# Customer Complaint Intelligence Dashboard")

st.markdown("---")

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():
    df = pd.read_csv("../data/dashboard_ready.csv", parse_dates=['date_received'])
    weekly = pd.read_csv("../data/cluster_week_counts.csv", parse_dates=['week'])
    return df, weekly

df, cluster_week_counts = load_data()

df['final_cluster_id'] = df['final_cluster_id'].astype(str)
cluster_week_counts['final_cluster_id'] = cluster_week_counts['final_cluster_id'].astype(str)

# Remove noise
df = df[df['final_cluster_id'] != '-1'].copy()
cluster_week_counts = cluster_week_counts[
    cluster_week_counts['final_cluster_id'] != '-1'
].copy()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.markdown("### 🎯 Filters")

products = sorted(df['product_norm'].dropna().unique())

product_filter = st.sidebar.multiselect(
    "Select Product",
    products,
    default=products if len(products) > 0 else []
)

date_min = df['date_received'].min()
date_max = df['date_received'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [date_min, date_max],
    min_value=date_min,
    max_value=date_max
)

# SAFE DATE HANDLING
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

df_filtered = df[
    (df['product_norm'].isin(product_filter)) &
    (df['date_received'] >= pd.to_datetime(start_date)) &
    (df['date_received'] <= pd.to_datetime(end_date))
].copy()

# =========================================================
# KPI SECTION
# =========================================================

st.markdown('<div class="section-header"><h2>📌 Key Metrics</h2></div>', unsafe_allow_html=True)

if not df_filtered.empty:
    total_complaints = len(df_filtered)
    total_clusters = df_filtered['final_cluster_id'].nunique()
    latest_date = df_filtered['date_received'].max()

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Total Complaints</div>
            <div class="kpi-value">{total_complaints:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Active Clusters</div>
            <div class="kpi-value">{total_clusters}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-label">Latest Complaint</div>
            <div class="kpi-value" style="font-size:1.25rem;">
                {latest_date.strftime('%b %d, %Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("⚠️ No data available for selected filters.")

# =========================================================
# ROOT CAUSE DISTRIBUTION
# =========================================================

st.markdown('<div class="section-header"><h2>🧠 Root Cause Distribution</h2></div>', unsafe_allow_html=True)

root_cols = ['delay','billing','refund','cancellation','outage']

if not df_filtered.empty and all(col in df_filtered.columns for col in root_cols):

    root_counts = df_filtered[root_cols].sum().sort_values(ascending=False)

    if root_counts.sum() > 0:
        fig_root = px.bar(
            x=root_counts.index,
            y=root_counts.values,
            labels={'x':'Root Cause','y':'Count'},
            height=400
        )

        fig_root.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig_root, use_container_width=True)

# =========================================================
# WEEKLY TREND
# =========================================================

st.markdown('<div class="section-header"><h2>📈 Weekly Trends</h2></div>', unsafe_allow_html=True)

if not df_filtered.empty:

    top_clusters = (
        df_filtered['final_cluster_id']
        .value_counts()
        .head(5)
        .index
    )

    for cluster_id in top_clusters:

        data = cluster_week_counts[
            cluster_week_counts['final_cluster_id'] == cluster_id
        ].sort_values('week').copy()

        if len(data) < 4:
            continue

        data['rolling_avg'] = data['complaint_count'].rolling(4).mean()

        fig = px.line(
            data,
            x='week',
            y='rolling_avg',
            title=f"Cluster {cluster_id}",
            height=350
        )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# CLUSTER DRILL DOWN
# =========================================================

st.markdown('<div class="section-header"><h2>🔍 Cluster Analysis</h2></div>', unsafe_allow_html=True)

if not df_filtered.empty:

    cluster_display_df = (
        df_filtered[['final_cluster_id','cluster_label']]
        .drop_duplicates()
        .dropna()
        .copy()
    )

    cluster_display_df['display_name'] = (
        cluster_display_df['cluster_label']
        + " (Cluster "
        + cluster_display_df['final_cluster_id']
        + ")"
    )

    cluster_map = dict(zip(
        cluster_display_df['display_name'],
        cluster_display_df['final_cluster_id']
    ))

    selected_display = st.selectbox(
        "Select a cluster to explore",
        cluster_display_df['display_name']
    )

    selected_cluster = cluster_map[selected_display]

    cluster_data = df_filtered[
        df_filtered['final_cluster_id'] == selected_cluster
    ]

    if not cluster_data.empty:

        col1, col2, col3 = st.columns(3)

        col1.metric("Cluster Size", len(cluster_data))
        col2.metric("% of Filtered Data",
                    f"{(len(cluster_data)/len(df_filtered))*100:.1f}%")
        col3.metric("Cluster ID", selected_cluster)

        st.markdown("##### Sample Complaints")

        sample_data = cluster_data.sample(
            min(5, len(cluster_data)),
            random_state=42
        )[['complaint_text']]

        for idx, row in sample_data.iterrows():
            st.markdown(f"> {row['complaint_text']}")
            st.divider()

# =========================================================
# EXPORT
# =========================================================

st.markdown('<div class="section-header"><h2>⬇️ Export Data</h2></div>', unsafe_allow_html=True)

if not df_filtered.empty:
    st.download_button(
        label="📥 Download CSV",
        data=df_filtered.to_csv(index=False),
        file_name="filtered_complaints.csv",
        mime="text/csv"
    )
