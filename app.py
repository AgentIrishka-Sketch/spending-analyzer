import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Spending Analyzer")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.write(df.columns)

   
