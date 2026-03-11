import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Spending Analyzer")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w_]", "", regex=True)
    )

    st.write("Columns:", list(df.columns))
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

    if "description" in df.columns:
        df["category"] = df["description"].apply(categorize)

        summary = df.groupby("category")["amount"].sum().abs().reset_index()

        fig = px.pie(summary, names="category", values="amount")
        st.plotly_chart(fig)
    else:
        st.error(f"'description' column not found. Columns: {list(df.columns)}")
