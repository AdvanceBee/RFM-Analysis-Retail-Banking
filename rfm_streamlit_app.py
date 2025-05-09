import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# App layout config
st.set_page_config(page_title="RFM Customer Segmentation", layout="wide")

# Sidebar Navigation
st.sidebar.title("📊 Navigation")
app_mode = st.sidebar.radio("Go to section:", [
    "Upload RFM File",
    "Upload Raw Transactions",
    "Explore Clusters",
    "Visualizations",
    "Download & Summary"
])

# Title
st.title(":bar_chart: RFM Customer Segmentation App")
st.markdown("Navigate through the sidebar to upload and analyze customer segmentation data.")

# Smart Insight Function
def generate_cluster_insight(recency, frequency, monetary):
    if recency < 30 and frequency >= 3 and monetary > 3000:
        return "🔥 Loyal & High-Value Customers"
    elif recency > 60 and frequency <= 1:
        return "⏳ At Risk or Churned Customers"
    elif frequency > 2 and monetary < 1000:
        return "💡 Engaged but Low Spending"
    elif recency < 40 and frequency == 1:
        return "🧪 New or One-Time Shoppers"
    else:
        return "📌 Moderate Activity Customers"

# Upload and store RFM file
if "rfm_data" not in st.session_state:
    st.session_state.rfm_data = None

if app_mode == "Upload RFM File":
    uploaded_file = st.file_uploader("Upload your RFM CSV file", type=["csv"], key="rfm_upload")

    if uploaded_file:
        rfm = pd.read_csv(uploaded_file)
        st.session_state.rfm_data = rfm
        st.success("✅ RFM data uploaded and stored!")
        st.dataframe(rfm.head())
    elif st.session_state.rfm_data is not None:
        st.info("📄 Previously uploaded data:")
        st.dataframe(st.session_state.rfm_data.head())
    else:
        st.warning("📁 Please upload a CSV file.")

# Use rfm from session state in other tabs
rfm = st.session_state.get("rfm_data", None)


# ---- Explore Clusters ----
elif app_mode == "Explore Clusters":
    rfm = st.session_state.get("rfm")

    if rfm is not None:
        st.subheader(":bar_chart: Customer Counts per Segment / Cluster")

        if 'Segment' in rfm.columns:
            count_data = rfm['Segment'].value_counts().sort_values().reset_index()
            count_data.columns = ['Segment', 'Count']

            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(data=count_data, y='Segment', x='Count', palette='Blues_d', ax=ax)
            ax.set_title("Customer Count by Segment")
            st.pyplot(fig)

        elif 'Cluster' in rfm.columns:
            count_data = rfm['Cluster'].value_counts().sort_values().reset_index()
            count_data.columns = ['Cluster', 'Count']

            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(data=count_data, y='Cluster', x='Count', palette='viridis', ax=ax)
            ax.set_title("Customer Count by Cluster")
            st.pyplot(fig)

        else:
            st.warning("\u26a0\ufe0f No 'Segment' or 'Cluster' column available to show counts.")
    else:
        st.info("\ud83d\udcc1 Please upload and process RFM data to view segment/cluster counts.")

# ---- Visualizations ----
elif app_mode == "Visualizations":
    rfm = st.session_state.get("rfm")

    if rfm is not None:
        st.subheader("\ud83d\udd39 RFM Pair Plot by Cluster")
        try:
            plot_data = rfm[['Recency', 'Frequency', 'Monetary', 'Cluster']].copy()
            if len(plot_data) > 1000:
                plot_data = plot_data.sample(1000)
            plot_data['Cluster'] = plot_data['Cluster'].astype(str)

            sns.set(style="ticks")
            fig = sns.pairplot(data=plot_data, hue='Cluster', palette='viridis', plot_kws={'alpha': 0.6})
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error generating pair plot: {e}")
    else:
        st.info("\ud83d\udcc1 Please upload RFM data first.")

# ---- Download & Summary ----
elif app_mode == "Download & Summary":
    rfm = st.session_state.get("rfm")

    if rfm is not None:
        st.subheader("\ud83d\udcdc RFM Summary by Cluster")
        if 'Segment' in rfm.columns and 'Cluster' in rfm.columns:
            summary = rfm.groupby(['Cluster', 'Segment'])[['Recency', 'Frequency', 'Monetary']].mean().round(1)
            st.dataframe(summary.reset_index())

        st.markdown("---")
        st.subheader(":calendar: Download Segmented Data")
        csv = rfm.to_csv(index=False)
        if st.download_button("Download RFM data as CSV", data=csv, file_name="rfm_segmented_output.csv", mime="text/csv"):
            st.success("\u2705 Download started! Check your browser.")
    else:
        st.info("\ud83d\udcc1 Please upload and process RFM data first.")
