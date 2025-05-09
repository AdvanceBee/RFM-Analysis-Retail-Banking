import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# App layout config
st.set_page_config(page_title="RFM Customer Segmentation", layout="wide")

# Title and instructions
st.title("📊 RFM Customer Segmentation App")
st.markdown("Upload your RFM dataset (must include Recency, Frequency, Monetary, and Cluster columns).")

# File uploader
uploaded_file = st.file_uploader("Upload your RFM CSV file", type=["csv"])

if uploaded_file:
    rfm = pd.read_csv(uploaded_file)
    
    # Data preview
    st.subheader("📄 Preview of Uploaded Data")
    st.dataframe(rfm.head())

    # Summary metrics
    st.subheader("📌 Summary Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🕒 Avg. Recency", f"{rfm['Recency'].mean():.1f} days")
    with col2:
        st.metric("🔁 Avg. Frequency", f"{rfm['Frequency'].mean():.1f} times")
    with col3:
        st.metric("💰 Avg. Monetary", f"${rfm['Monetary'].mean():,.2f}")

    # Cluster filter
    st.markdown("---")
    st.subheader("🎯 Filter by Customer Cluster")

    if 'Cluster' in rfm.columns:
        selected_cluster = st.selectbox(
            "Select a cluster to explore:",
            sorted(rfm['Cluster'].unique())
        )

        filtered_df = rfm[rfm['Cluster'] == selected_cluster]

        st.write(f"Showing {len(filtered_df)} customers in Cluster {selected_cluster}")
        st.dataframe(filtered_df.head())

        # ✅ Show segment name if column exists
        if 'Segment' in filtered_df.columns:
            segment_name = filtered_df['Segment'].iloc[0]
            st.success(f"🧠 Segment: **{segment_name}**")
    else:
        st.warning("⚠️ Cluster column not found in your data.")

    # Scatter plot
    st.subheader("📊 Recency vs Frequency by Cluster")
    if 'Cluster' in rfm.columns:
        fig1, ax1 = plt.subplots()
        sns.scatterplot(data=rfm, x="Recency", y="Frequency", hue="Cluster", palette="viridis", ax=ax1)
        ax1.set_title("Customer Clusters")
        st.pyplot(fig1)

    # Box plots
    st.subheader("📦 RFM Distribution by Cluster")
    if 'Cluster' in rfm.columns:
        fig2, axes = plt.subplots(1, 3, figsize=(18, 5))

        sns.boxplot(data=rfm, x='Cluster', y='Recency', ax=axes[0])
        axes[0].set_title('Recency')

        sns.boxplot(data=rfm, x='Cluster', y='Frequency', ax=axes[1])
        axes[1].set_title('Frequency')

        sns.boxplot(data=rfm, x='Cluster', y='Monetary', ax=axes[2])
        axes[2].set_title('Monetary')

        st.pyplot(fig2)

    # Summary stats by cluster
    if 'Segment' in rfm.columns:
        st.subheader("📋 RFM Summary by Cluster")
        summary = rfm.groupby(['Cluster', 'Segment'])[['Recency', 'Frequency', 'Monetary']].mean().round(1)
        st.dataframe(summary.reset_index())

    # Download button
    st.markdown("---")
    st.subheader("📥 Download Segmented Data")
    csv = rfm.to_csv(index=False)
    if st.download_button("Download RFM data as CSV", data=csv, file_name="rfm_segmented_output.csv", mime="text/csv"):
        st.success("✅ Download started! Check your browser.")

else:
    st.info("📂 Please upload a CSV file to begin.")
