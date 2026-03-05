import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Spending Analyzer")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.write("Preview", df.head())

    categories = {
        "Groceries": ["tesco", "lidl", "albert"],
        "Fuel": ["shell", "fuel"],
        "Entertainment": ["netflix", "spotify"]
    }

    def categorize(desc):
        desc = str(desc).lower()
        for cat, keywords in categories.items():
            for kw in keywords:
                if kw in desc:
                    return cat
        return "Other"

    df["category"] = df["description"].apply(categorize)
    df["amount"] = df["amount"].abs()

    summary = df.groupby("category")["amount"].sum().reset_index()

    fig = px.pie(summary, names="category", values="amount")
    st.plotly_chart(fig)
