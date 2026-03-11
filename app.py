import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.title("💳 Spending Analyzer")

# --- Upload Excel file with keywords ---
categories_file = st.file_uploader(
    "Upload Keyword Excel (.xlsx) with columns 'Keyword' and 'Category'",
    type=["xlsx"]
)

# --- Upload Revolut CSV file ---
transactions_file = st.file_uploader(
    "Upload Revolut CSV",
    type=["csv"]
)

if categories_file and transactions_file:

    # --- Load keywords Excel ---
    categories_df = pd.read_excel(categories_file)
    
    # Normalize keywords
    def normalize_text(text):
        text = str(text).lower().strip()
        text = re.sub(r"[^a-z0-9]", "", text)  # remove non-alphanumeric
        return text

    categories_df["keyword_norm"] = categories_df["Keyword"].apply(normalize_text)
    
    # --- Load Revolut CSV ---
    df = pd.read_csv(transactions_file, sep=";")
    
    # Normalize columns
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    # Ensure correct columns exist
    required_cols = ["description", "amount", "started_date"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Column '{col}' not found in CSV. Found columns: {df.columns.tolist()}")
            st.stop()

    # Normalize transaction descriptions
    df["description_norm"] = df["description"].apply(normalize_text)
    
    # Convert amounts to numeric
    df["amount"] = (
        df["amount"].astype(str)
        .str.replace(",", ".")
        .str.replace(" ", "")
    )
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").abs()

    # Convert date column
    df["started_date"] = pd.to_datetime(
        df["started_date"].astype(str).str.strip(),
        format="%d.%m.%Y %H:%M:%S",
        errors="coerce"
    )
    df = df.dropna(subset=["started_date"])
    df["month"] = df["started_date"].dt.to_period("M").astype(str)

    # --- Categorize transactions ---
    keyword_map = dict(zip(categories_df["keyword_norm"], categories_df["Category"]))

    def categorize(desc_norm):
        for keyword_norm, category in keyword_map.items():
            if keyword_norm in desc_norm:  # partial match
                return category
        return "Other"

    df["category"] = df["description_norm"].apply(categorize)

    # --- Debug: show categories mapping ---
    st.write("Categories after mapping:")
    st.dataframe(df["category"].value_counts())

    # --- CATEGORY PIE ---
    st.subheader("Spending by Category")
    summary = df.groupby("category")["amount"].sum().reset_index()
    fig1 = px.pie(summary, names="category", values="amount")
    st.plotly_chart(fig1, use_container_width=True)

    # --- MONTHLY SPENDING ---
    st.subheader("Monthly Spending")
    monthly = df.groupby("month")["amount"].sum().reset_index()
    fig2 = px.bar(monthly, x="month", y="amount")
    st.plotly_chart(fig2, use_container_width=True)

    # --- TOP MERCHANTS ---
    st.subheader("Top Merchants")
    merchants = df.groupby("description")["amount"].sum().sort_values(ascending=False).head(10).reset_index()
    fig3 = px.bar(merchants, x="amount", y="description", orientation="h")
    st.plotly_chart(fig3, use_container_width=True)

    # --- TRANSACTIONS TABLE ---
    st.subheader("Transactions")
    st.dataframe(df[["started_date", "description", "category", "amount"]].sort_values("started_date", ascending=False))
