import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# App layout config
st.set_page_config(page_title="RFM Customer Segmentation", layout="wide")

# Sidebar
st.sidebar.title("📊 Navigation")
app_mode = st.sidebar.radio("Go to section:", [
    "Upload RFM File",
    "Upload Raw Transactions",
    "Explore Clusters",
    "Visualizations",
    "Download & Summary"
])

# Title and instructions
st.title("📊 RFM Customer Segmentation App")
st.markdown("Navigate through the sidebar to upload and analyze customer segmentation data.")

# Insight logic function
def generate_cluster_insight(recency, frequency, monetary):
    if recency < 30 and frequency >= 3 and monetary > 3000:
        return "🔥 Loyal & High-Value Customers\nThese customers buy frequently and recently. Focus on retention and VIP treatment."
    elif recency > 60 and frequency <= 1:
        return "⏳ At Risk or Churned Customers\nThey haven't purchased in a while. Consider win-back campaigns or surveys."
    elif frequency > 2 and monetary < 1000:
        return "💡 Engaged but Low Spending\nThey visit often but spend little. Upsell, bundle offers, or loyalty points may help."
    elif recency < 40 and frequency == 1:
        return "🧪 New or One-Time Shoppers\nThese are new or occasional buyers. Welcome them with onboarding offers."
    else:
        return "📌 Moderate Activity Customers\nThey’re average across RFM. Use personalized campaigns to boost loyalty."

# ---- Upload Raw Transactions ----
if app_mode == "Upload Raw Transactions":
    st.markdown("## 🔄 Upload Raw Transactions to Compute RFM")
    raw_file = st.file_uploader("Upload raw transactions (CustomerID, InvoiceDate, Amount)", type=["csv"], key="raw")

    if raw_file:
        raw_df = pd.read_csv(raw_file, parse_dates=["InvoiceDate"])

        st.success("Raw data uploaded successfully!")
        st.dataframe(raw_df.head())

        try:
            ref_date = raw_df["InvoiceDate"].max() + pd.Timedelta(days=1)
            rfm = raw_df.groupby("CustomerID").agg({
                "InvoiceDate": lambda x: (ref_date - x.max()).days,
                "InvoiceDate": "count",
                "Amount": "sum"
            }).rename(columns={
                "InvoiceDate": "Frequency",
                "<lambda_0>": "Recency",
                "Amount": "Monetary"
            })
            rfm["Recency"] = raw_df.groupby("CustomerID")["InvoiceDate"].apply(lambda x: (ref_date - x.max()).days)
            rfm = rfm.rename(columns={"InvoiceDate": "Frequency"})

            rfm["R_Score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1])
            rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
            rfm["M_Score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4])
            rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)

            st.subheader("🌟 Computed RFM Table")
            st.dataframe(rfm.reset_index())

            csv = rfm.reset_index().to_csv(index=False)
            st.download_button("Download Computed RFM CSV", data=csv, file_name="rfm_computed.csv", mime="text/csv")

        except Exception as e:
            st.error(f"Error processing raw data: {e}")

# ---- Upload RFM File ----
elif app_mode == "Upload RFM File":
    uploaded_file = st.file_uploader("Upload your RFM CSV file", type=["csv"])

    if uploaded_file:
        rfm = pd.read_csv(uploaded_file)
        st.subheader("📄 Preview of Uploaded Data")
        st.dataframe(rfm.head())

# ---- Explore Clusters ----
elif app_mode == "Explore Clusters":
    if 'rfm' in locals():
        st.subheader("🌟 Filter by Customer Cluster")

        if 'Cluster' in rfm.columns:
            cluster_options = sorted(rfm['Cluster'].dropna().unique())

            if cluster_options:
                selected_cluster = st.selectbox("Select a cluster to explore:", cluster_options)
                filtered_df = rfm[rfm['Cluster'] == selected_cluster]

                if not filtered_df.empty:
                    st.dataframe(filtered_df.head())

                    segment_name = filtered_df['Segment'].iloc[0] if 'Segment' in filtered_df.columns else "N/A"
                    st.markdown(f"🔎 **{len(filtered_df):,} customers** in **Cluster {selected_cluster}** — Segment: **{segment_name}**")

                    try:
                        avg_r = filtered_df['Recency'].mean()
                        avg_f = filtered_df['Frequency'].mean()
                        avg_m = filtered_df['Monetary'].mean()
                        insight = generate_cluster_insight(avg_r, avg_f, avg_m)
                        st.info(f"📊 **Insight**: {insight}")
                    except Exception as e:
                        st.warning("⚠️ Could not generate insight. Please check column names and data.")
                else:
                    st.warning("⚠️ No records found for this cluster.")
            else:
                st.warning("⚠️ No cluster options available in your data.")
        else:
            st.warning("⚠️ Cluster column not found in your data.")
    else:
        st.info("📂 Please upload a CSV file in 'Upload RFM File' section.")

# ---- Visualizations ----
elif app_mode == "Visualizations":
    if 'rfm' in locals() and 'Cluster' in rfm.columns:
        st.subheader("📊 Recency vs Frequency by Cluster")
        fig1, ax1 = plt.subplots()
        sns.scatterplot(data=rfm, x="Recency", y="Frequency", hue="Cluster", palette="viridis", ax=ax1)
        ax1.set_title("Customer Clusters")
        st.pyplot(fig1)

        st.subheader("📦 RFM Distribution by Cluster")
        fig2, axes = plt.subplots(1, 3, figsize=(18, 5))
        sns.boxplot(data=rfm, x='Cluster', y='Recency', ax=axes[0])
        axes[0].set_title('Recency')
        sns.boxplot(data=rfm, x='Cluster', y='Frequency', ax=axes[1])
        axes[1].set_title('Frequency')
        sns.boxplot(data=rfm, x='Cluster', y='Monetary', ax=axes[2])
        axes[2].set_title('Monetary')
        st.pyplot(fig2)

        st.subheader("🔗 RFM Pair Plot by Cluster")
        try:
            plot_data = rfm[['Recency', 'Frequency', 'Monetary', 'Cluster']].copy()
            if len(plot_data) > 1000:
                plot_data = plot_data.sample(1000, random_state=1)
            plot_data['Cluster'] = plot_data['Cluster'].astype(str)
            sns.set(style="ticks")
            fig3 = sns.pairplot(data=plot_data, hue='Cluster', palette='viridis', plot_kws={'alpha': 0.6})
            st.pyplot(fig3)
        except Exception as e:
            st.error(f"Error generating pair plot: {e}")
    else:
        st.info("📂 Please upload and prepare your data in earlier steps.")

# Horizontal Bar Chart - Customer Count by Segment or Cluster
st.subheader("📊 Customer Counts per Segment / Cluster")

if 'Segment' in rfm.columns:
    count_data = rfm['Segment'].value_counts().sort_values().reset_index()
    count_data.columns = ['Segment', 'Count']

    fig4, ax4 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=count_data, y='Segment', x='Count', palette='Blues_d', ax=ax4)
    ax4.set_title("Customer Count by Segment")
    st.pyplot(fig4)

elif 'Cluster' in rfm.columns:
    count_data = rfm['Cluster'].value_counts().sort_values().reset_index()
    count_data.columns = ['Cluster', 'Count']

    fig4, ax4 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=count_data, y='Cluster', x='Count', palette='viridis', ax=ax4)
    ax4.set_title("Customer Count by Cluster")
    st.pyplot(fig4)
else:
    st.warning("⚠️ No 'Segment' or 'Cluster' column available to show counts.")

# ---- Download & Summary ----
elif app_mode == "Download & Summary":
    if 'rfm' in locals():
        if 'Segment' in rfm.columns:
            st.subheader("📋 RFM Summary by Cluster")
            summary = rfm.groupby(['Cluster', 'Segment'])[['Recency', 'Frequency', 'Monetary']].mean().round(1)
            st.dataframe(summary.reset_index())

        st.markdown("---")
        st.subheader("📅 Download Segmented Data")
        csv = rfm.to_csv(index=False)
        if st.download_button("Download RFM data as CSV", data=csv, file_name="rfm_segmented_output.csv", mime="text/csv"):
            st.success("✅ Download started! Check your browser.")
    else:
        st.info("📂 Please upload and process RFM data first.")
