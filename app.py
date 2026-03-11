import streamlit as st
import pandas as pd
import re

st.title("💳 Simple Spending by Category")

# --- Upload Excel file with keywords ---
categories_file = st.file_uploader("Upload Category Excel (.xlsx)", type=["xlsx"])

# --- Upload Revolut CSV file ---
transactions_file = st.file_uploader("Upload Revolut CSV", type=["csv"])

if categories_file and transactions_file:

    # --- Load categories ---
    categories_df = pd.read_excel(categories_file)
    
    # Normalize keywords
    def normalize(text):
        text = str(text).lower().strip()
        text = re.sub(r"[^a-z0-9]", "", text)  # remove non-alphanumeric chars
        return text

    categories_df["keyword_norm"] = categories_df["Keyword"].apply(normalize)

    # --- Load CSV ---
    df = pd.read_csv(transactions_file, sep=";")
    
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Check required columns
    if "description" not in df.columns or "amount" not in df.columns:
        st.error("CSV must contain 'Description' and 'Amount' columns")
        st.stop()

    # Normalize description
    df["description_norm"] = df["description"].apply(normalize)

    # Convert amount to numeric
    df["amount"] = df["amount"].astype(str).str.replace(",", ".").str.replace(" ", "")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").abs()

    # --- Categorize ---
    keyword_map = dict(zip(categories_df["keyword_norm"], categories_df["Category"]))

    def categorize(desc_norm):
        for keyword_norm, category in keyword_map.items():
            if keyword_norm in desc_norm:
                return category
        return "Unknown"

    df["category"] = df["description_norm"].apply(categorize)

    # --- Sum per category ---
    summary = df.groupby("category")["amount"].sum().reset_index()
    summary = summary.sort_values(by="amount", ascending=False)

    st.subheader("Total Spend per Category")
    st.dataframe(summary)
