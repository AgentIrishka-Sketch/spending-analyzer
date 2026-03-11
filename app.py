import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Spending Analyzer")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # очистка названий колонок
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

    st.write("Preview", df.head())

    categories = {
        "Groceries": ["tesco", "lidl", "albert", "billa", "sklizeno", "vilgain"],
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

    # суммирование расходов (Revolut часто хранит траты как отрицательные числа)
    summary = df.groupby("category")["amount"].sum().abs().reset_index()

    fig = px.pie(summary, names="category", values="amount")
    st.plotly_chart(fig)
