import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# App layout config
st.set_page_config(page_title="RFM Customer Segmentation", layout="wide")

# Title
st.title(":bar_chart: RFM Customer Segmentation App")
st.markdown("Upload your dataset and explore RFM segmentation with visual insights.")

# Upload section
st.subheader("📁 Upload Your RFM File")

uploaded_file = st.file_uploader("Upload your RFM CSV file", type=["csv"], key="rfm_file")

# Try to read uploaded file
if uploaded_file is not None:
    rfm_df = pd.read_csv(uploaded_file)
    st.session_state.rfm = rfm_df
    st.success("✅ File uploaded successfully.")
    st.dataframe(rfm_df.head())

# If not uploaded, check if session already has RFM
elif "rfm" in st.session_state:
    rfm_df = st.session_state.rfm
    st.info("ℹ️ Showing previously uploaded data")
    st.dataframe(rfm_df.head())

# If neither, try loading the fallback sample file
elif os.path.exists("sample_rfm_data.csv"):
    rfm_df = pd.read_csv("sample_rfm_data.csv")
    st.session_state.rfm = rfm_df
    st.warning("⚠️ No file uploaded — using sample RFM data.")
    st.dataframe(rfm_df.head())

# Nothing to show
else:
    rfm_df = None
    st.error("❌ No data found. Please upload a CSV file to proceed.")

# Optional: Upload raw transactions to compute RFM
st.markdown("---")
st.subheader("🔄 Upload Raw Transactions to Compute RFM")
raw_file = st.file_uploader("Upload raw transactions (CustomerID, InvoiceDate, Amount)", type=["csv"], key="raw")

if raw_file:
    raw_df = pd.read_csv(raw_file, parse_dates=["InvoiceDate"])
    st.dataframe(raw_df.head())

    try:
        ref_date = raw_df["InvoiceDate"].max() + pd.Timedelta(days=1)
        rfm = raw_df.groupby("CustomerID").agg({
            "InvoiceDate": "count",
            "Amount": "sum"
        }).rename(columns={
            "InvoiceDate": "Frequency",
            "Amount": "Monetary"
        })

        rfm["Recency"] = raw_df.groupby("CustomerID")["InvoiceDate"].apply(lambda x: (ref_date - x.max()).days)

        rfm["R_Score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1])
        rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
        rfm["M_Score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4])
        rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)

        st.session_state.rfm = rfm
        st.success("✅ RFM computed and stored in session!")
        st.dataframe(rfm.reset_index())
    except Exception as e:
        st.error(f"Error processing raw data: {e}")

# Show summary metrics and visualizations if data exists
if rfm_df is not None:
    st.markdown("---")
    st.subheader("📌 Summary Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🕒 Avg. Recency", f"{rfm_df['Recency'].mean():.1f} days")
    with col2:
        st.metric("🔁 Avg. Frequency", f"{rfm_df['Frequency'].mean():.1f} times")
    with col3:
        st.metric("💰 Avg. Monetary", f"${rfm_df['Monetary'].mean():,.2f}")

    # Horizontal bar chart by Segment or Cluster
    st.markdown("---")
    st.subheader("📊 Customer Counts per Segment / Cluster")
    if 'Segment' in rfm_df.columns:
        count_data = rfm_df['Segment'].value_counts().sort_values().reset_index()
        count_data.columns = ['Segment', 'Count']
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=count_data, y='Segment', x='Count', palette='Blues_d', ax=ax)
        ax.set_title("Customer Count by Segment")
        st.pyplot(fig)
    elif 'Cluster' in rfm_df.columns:
        count_data = rfm_df['Cluster'].value_counts().sort_values().reset_index()
        count_data.columns = ['Cluster', 'Count']
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=count_data, y='Cluster', x='Count', palette='viridis', ax=ax)
        ax.set_title("Customer Count by Cluster")
        st.pyplot(fig)

    # Pair Plot
    st.markdown("---")
    st.subheader("🔗 RFM Pair Plot by Cluster")
    try:
        if 'Cluster' in rfm_df.columns:
            plot_data = rfm_df[['Recency', 'Frequency', 'Monetary', 'Cluster']].copy()
            if len(plot_data) > 1000:
                plot_data = plot_data.sample(1000)
            plot_data['Cluster'] = plot_data['Cluster'].astype(str)
            sns.set(style="ticks")
            fig_pair = sns.pairplot(data=plot_data, hue='Cluster', palette='viridis', plot_kws={'alpha': 0.6})
            st.pyplot(fig_pair)
        else:
            st.warning("'Cluster' column is required for pair plot.")
    except Exception as e:
        st.error(f"Error generating pair plot: {e}")

    # Download section
    st.markdown("---")
    st.subheader("📅 Download Segmented Data")
    csv = rfm_df.to_csv(index=False)
    if st.download_button("Download RFM data as CSV", data=csv, file_name="rfm_segmented_output.csv", mime="text/csv"):
        st.success("✅ Download started! Check your browser.")
