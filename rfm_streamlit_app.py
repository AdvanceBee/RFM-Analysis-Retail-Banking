import streamlit as st
import pandas as pd

st.title("📊 RFM Customer Segmentation App")

uploaded_file = st.file_uploader("Upload your RFM data (CSV)", type=["csv"])

if uploaded_file:
    rfm = pd.read_csv(uploaded_file)
    st.subheader("📄 Preview of Data")
    st.write(rfm.head())
