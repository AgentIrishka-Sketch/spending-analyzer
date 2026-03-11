import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💳 Spending Analyzer")

# --- Upload Excel file with keywords ---
categories_file = st.file_uploader(
    "Upload Keyword Excel (.xlsx) with columns 'Keyword' and 'Category'",
    type=["xlsx"],
    key="categories"
)

# --- Upload Revolut CSV file ---
transactions_file = st.file_uploader(
    "Upload Revolut CSV",
    type=["csv"],
    key="transactions"
)

if categories_file and transactions_file:

    # --- Load keywords Excel ---
    categories_df = pd.read_excel(categories_file, sheet_name=0)
    st.write("Categories preview:", categories_df.head())

    # Create dictionary: keyword → category
    keyword_map = dict(
        zip(
            categories_df.Keyword.str.lower().str.strip(),
            categories_df.Category.str.strip()
        )
    )

    # --- Load Revolut CSV ---
    df = pd.read_csv(transactions_file, sep=";")

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Convert date column
    df["started_date"] = pd.to_datetime(
        df["started_date"].astype(str).str.strip(),
        format="%d.%m.%Y %H:%M:%S",
        errors="coerce"
    )
    df = df.dropna(subset=["started_date"])

    # Categorize transactions
    def categorize(desc):
        desc = str(desc).lower()
        for keyword, category in keyword_map.items():
            if keyword in desc:
                return category
        return "Other"

    df["category"] = df["description"].apply(categorize)

    # Convert amount to numeric and take absolute value
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").abs()

    # Copy all transactions as expenses (positive amounts)
    expenses = df.copy()
    expenses["month"] = expenses["started_date"].dt.to_period("M").astype(str)

    # --- CATEGORY PIE ---
    st.subheader("Spending by Category")
    summary = expenses.groupby("category")["amount"].sum().reset_index()
    fig1 = px.pie(summary, names="category", values="amount")
    st.plotly_chart(fig1, use_container_width=True)

    # --- MONTHLY SPENDING ---
    st.subheader("Monthly Spending")
    monthly = expenses.groupby("month")["amount"].sum().reset_index()
    fig2 = px.bar(monthly, x="month", y="amount")
    st.plotly_chart(fig2, use_container_width=True)

    # --- TOP MERCHANTS ---
    st.subheader("Top Merchants")
    merchants = (
        expenses.groupby("description")["amount"]
        .sum()
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
