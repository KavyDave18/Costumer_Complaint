import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():
    df = pd.read_csv(
        "../data/dashboard_ready.csv",
        parse_dates=['date_received']
    )

    weekly = pd.read_csv(
        "../data/cluster_week_counts.csv",
        parse_dates=['week']
    )

    return df, weekly


df, cluster_week_counts = load_data()

df['final_cluster_id'] = df['final_cluster_id'].astype(str)
cluster_week_counts['final_cluster_id'] = cluster_week_counts['final_cluster_id'].astype(str)

# Remove noise
df = df[df['final_cluster_id'] != '-1']
cluster_week_counts = cluster_week_counts[
    cluster_week_counts['final_cluster_id'] != '-1'
]

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("Filters")

product_filter = st.sidebar.multiselect(
    "Select Product",
    sorted(df['product_norm'].dropna().unique()),
    default=sorted(df['product_norm'].dropna().unique())
)

date_min = df['date_received'].min()
date_max = df['date_received'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [date_min, date_max],
    min_value=date_min,
    max_value=date_max
)

# --- Safe date handling ---
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range
    end_date = date_range

df_filtered = df[
    (df['product_norm'].isin(product_filter)) &
    (df['date_received'] >= pd.to_datetime(start_date)) &
    (df['date_received'] <= pd.to_datetime(end_date))
]

# =========================================================
# HEADER
# =========================================================

st.title("Customer Complaint Intelligence Dashboard")
st.markdown("---")

# =========================================================
# KPI SECTION
# =========================================================

st.header("Key Metrics")

if not df_filtered.empty:
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Complaints", f"{len(df_filtered):,}")
    col2.metric("Active Clusters", df_filtered['final_cluster_id'].nunique())
    col3.metric(
        "Latest Complaint",
        df_filtered['date_received'].max().strftime('%b %d, %Y')
    )
else:
    st.warning("No data available for selected filters.")

# =========================================================
# ROOT CAUSE DISTRIBUTION
# =========================================================

# st.header("Root Cause Distribution")

root_cols = ['delay','billing','refund','cancellation','outage']

if not df_filtered.empty and all(col in df_filtered.columns for col in root_cols):

    root_counts = (
        df_filtered[root_cols]
        .sum()
        .sort_values(ascending=False)
    )

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
# WEEKLY TREND SECTION
# =========================================================

st.header("Weekly Trends (Top 5 Clusters)")

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
        ].sort_values('week')

        if len(data) < 4:
            continue

        data = data.copy()
        data['rolling_avg'] = data['complaint_count'].rolling(4).mean()

        # Use cluster label instead of raw ID
        cluster_label = df_filtered[
            df_filtered['final_cluster_id'] == cluster_id
        ]['cluster_label'].iloc[0]

        fig = px.line(
            data,
            x='week',
            y='rolling_avg',
            title=cluster_label,
            height=350
        )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Week",
            yaxis_title="4-Week Moving Average"
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# HIGH VOLUME CLUSTERS (RENAMED)
# =========================================================

st.header("High Volume Clusters")

if not df_filtered.empty:

    cluster_sizes = (
        df_filtered
        .groupby('final_cluster_id')
        .size()
        .reset_index(name='complaint_count')
        .sort_values('complaint_count', ascending=False)
        .head(5)
    )

    cluster_sizes = cluster_sizes.merge(
        df_filtered[['final_cluster_id','cluster_label']]
        .drop_duplicates(),
        on='final_cluster_id',
        how='left'
    )

    display_df = cluster_sizes[
        ['cluster_label','complaint_count']
    ].rename(columns={
        'cluster_label':'Cluster',
        'complaint_count':'Complaints'
    })

    st.dataframe(display_df, use_container_width=True)

# =========================================================
# CLUSTER DRILLDOWN
# =========================================================

st.header("Cluster Analysis")

if not df_filtered.empty:

    cluster_display_df = (
        df_filtered[['final_cluster_id', 'cluster_label']]
        .drop_duplicates()
        .dropna(subset=['cluster_label'])
    )

    cluster_display_df['display_name'] = (
        cluster_display_df['cluster_label']
    )

    cluster_map = dict(
        zip(cluster_display_df['display_name'],
            cluster_display_df['final_cluster_id'])
    )

    selected_display = st.selectbox(
        "Select Cluster",
        cluster_display_df['display_name']
    )

    selected_cluster = cluster_map[selected_display]

    cluster_data = df_filtered[
        df_filtered['final_cluster_id'] == selected_cluster
    ]

    if not cluster_data.empty:

        st.subheader("Cluster Summary")

        col1, col2 = st.columns(2)

        col1.metric("Cluster Size", len(cluster_data))
        col2.metric(
            "% of Filtered Data",
            f"{(len(cluster_data)/len(df_filtered))*100:.1f}%"
        )

        st.subheader("Sample Complaints")

        sample = cluster_data[['complaint_text']].sample(
            min(5, len(cluster_data))
        )

        st.dataframe(sample, use_container_width=True)

# =========================================================
# EXPORT
# =========================================================

st.header("Export")

if not df_filtered.empty:
    st.download_button(
        label="Download Filtered Data",
        data=df_filtered.to_csv(index=False),
        file_name="filtered_complaints.csv",
        mime="text/csv"
    )
