import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💳 Spending Analyzer")

uploaded_file = st.file_uploader("Upload Revolut CSV", type="csv")

if uploaded_file:

    df = pd.read_csv(uploaded_file, sep=";")

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

   df["started_date"] = pd.to_datetime(
    df["started_date"].astype(str).str.strip(),
    format="%d.%m.%Y %H:%M:%S",
    errors="coerce"
)
df = df.dropna(subset=["started_date"])

    categories_df = pd.read_csv("categories.csv")

    keyword_map = dict(
        zip(categories_df.keyword.str.lower(),
            categories_df.category)
    )

    def categorize(desc):

        desc = str(desc).lower()

        for keyword, category in keyword_map.items():

            if keyword in desc:
                return category

        return "Other"

    df["category"] = df["description"].apply(categorize)

    df["amount"] = pd.to_numeric(df["amount"])

    expenses = df[df["amount"] < 0]

    expenses["month"] = expenses["started_date"].dt.to_period("M").astype(str)

    # --- CATEGORY PIE ---
    st.subheader("Spending by Category")

    summary = (
        expenses.groupby("category")["amount"]
        .sum()
        .abs()
        .reset_index()
    )

    fig1 = px.pie(summary, names="category", values="amount")

    st.plotly_chart(fig1, use_container_width=True)

    # --- MONTHLY SPENDING ---

    st.subheader("Monthly Spending")

    monthly = (
        expenses.groupby("month")["amount"]
        .sum()
        .abs()
        .reset_index()
    )

    fig2 = px.bar(monthly, x="month", y="amount")

    st.plotly_chart(fig2, use_container_width=True)

    # --- TOP MERCHANTS ---

    st.subheader("Top Merchants")

    merchants = (
        expenses.groupby("description")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig3 = px.bar(merchants, x="amount", y="description", orientation="h")

    st.plotly_chart(fig3, use_container_width=True)

    # --- TRANSACTIONS TABLE ---

    st.subheader("Transactions")

    st.dataframe(
        expenses[
            ["started_date", "description", "category", "amount"]
        ].sort_values("started_date", ascending=False)
    )
