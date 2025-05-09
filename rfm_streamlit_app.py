import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# App layout config
st.set_page_config(page_title="RFM Customer Segmentation", layout="wide")

# Title and instructions
st.title("📊 RFM Customer Segmentation App")
st.markdown("Upload your RFM dataset (must include Recency, Frequency, Monetary, and Cluster columns).")

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

# ---- Optional: Upload Raw Data and Compute RFM ----
st.markdown("## 🔄 Upload Raw Transactions to Compute RFM")
raw_file = st.file_uploader("Upload raw transactions (CustomerID, InvoiceDate, Amount)", type=["csv"], key="raw")

if raw_file:
    raw_df = pd.read_csv(raw_file, parse_dates=["InvoiceDate"])

    st.success("Raw data uploaded successfully!")
    st.dataframe(raw_df.head())

    try:
        # Reference date: 1 day after the last invoice
        ref_date = raw_df["InvoiceDate"].max() + pd.Timedelta(days=1)

        # Compute Recency, Frequency, Monetary
        rfm = raw_df.groupby("CustomerID").agg({
            "InvoiceDate": lambda x: (ref_date - x.max()).days,
            "InvoiceDate": "count",
            "Amount": "sum"
        }).rename(columns={
            "InvoiceDate": "Frequency",  # Reassigned later
            "<lambda_0>": "Recency",     # Fixed naming
            "Amount": "Monetary"
        })

        rfm["Recency"] = raw_df.groupby("CustomerID")["InvoiceDate"].apply(lambda x: (ref_date - x.max()).days)
        rfm = rfm.rename(columns={"InvoiceDate": "Frequency"})

        # Compute RFM scores
        rfm["R_Score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1])
        rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
        rfm["M_Score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4])

        # Combine for total score
        rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)

        st.subheader("🎯 Computed RFM Table")
        st.dataframe(rfm.reset_index())

        # Save processed for download or further use
        csv = rfm.reset_index().to_csv(index=False)
        st.download_button("Download Computed RFM CSV", data=csv, file_name="rfm_computed.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error processing raw data: {e}")


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

    # Cluster filter section
    st.markdown("---")
    st.subheader("🎯 Filter by Customer Cluster")

    if 'Cluster' in rfm.columns:
        cluster_options = sorted(rfm['Cluster'].dropna().unique())

        if cluster_options:
            selected_cluster = st.selectbox("Select a cluster to explore:", cluster_options)

            filtered_df = rfm[rfm['Cluster'] == selected_cluster]

            if not filtered_df.empty:
                st.dataframe(filtered_df.head())

                segment_name = filtered_df['Segment'].iloc[0] if 'Segment' in filtered_df.columns else "N/A"
                st.markdown(f"🔎 **{len(filtered_df):,} customers** in **Cluster {selected_cluster}** — Segment: **{segment_name}**")

                # Smart cluster insight
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

# Pair Plot to show relationships
st.subheader("🔗 RFM Pair Plot by Cluster")
if 'Cluster' in rfm.columns:
    try:
        # Sample data if too large
        plot_data = rfm[['Recency', 'Frequency', 'Monetary', 'Cluster']].copy()
        if len(plot_data) > 1000:
            plot_data = plot_data.sample(1000, random_state=1)  # speed for large data

        # Cluster must be a string or category for hue
        plot_data['Cluster'] = plot_data['Cluster'].astype(str)

        sns.set(style="ticks")
        fig3 = sns.pairplot(data=plot_data, hue='Cluster', palette='viridis', plot_kws={'alpha': 0.6})
        st.pyplot(fig3)
    except Exception as e:
        st.error(f"Error generating pair plot: {e}")
else:
    st.warning("⚠️ 'Cluster' column not found for plotting.")
    
    
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
