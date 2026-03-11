import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💳 Spending Analyzer")

# --- Загрузка Excel файла категорий ---
categories_file = st.file_uploader(
    "Upload Categories Excel (.xlsx)", type=["xlsx"], key="categories"
)

if categories_file:
    categories_df = pd.read_excel(categories_file, sheet_name=0)
    st.write("Categories preview:", categories_df.head())

    # словарь keyword → category
    keyword_map = dict(
        zip(
            categories_df.keyword.str.lower().str.strip(),
            categories_df.category.str.strip()
        )
    )

    # --- Загрузка CSV транзакций Revolut ---
    transactions_file = st.file_uploader(
        "Upload Transactions CSV", type=["csv"], key="transactions"
    )

    if transactions_file:
        df = pd.read_csv(transactions_file, sep=";")

        # очистка колонок
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        # конвертация даты в datetime (формат DD.MM.YYYY HH:MM:SS)
        df["started_date"] = pd.to_datetime(
            df["started_date"].astype(str).str.strip(),
            format="%d.%m.%Y %H:%M:%S",
            errors="coerce"
        )
        df = df.dropna(subset=["started_date"])

        # функция категоризации
        def categorize(desc):
            desc = str(desc).lower()
            for keyword, category in keyword_map.items():
                if keyword in desc:
                    return category
            return "Other"

        df["category"] = df["description"].apply(categorize)

        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        expenses = df[df["amount"] < 0].copy()
        expenses["month"] = expenses["started_date"].dt.to_period("M").astype(str)

        # --- Pie chart по категориям ---
        st.subheader("Spending by Category")
        summary = expenses.groupby("category")["amount"].sum().abs().reset_index()
        fig1 = px.pie(summary, names="category", values="amount")
        st.plotly_chart(fig1, use_container_width=True)

        # --- Monthly spending ---
        st.subheader("Monthly Spending")
        monthly = expenses.groupby("month")["amount"].sum().abs().reset_index()
        fig2 = px.bar(monthly, x="month", y="amount")
        st.plotly_chart(fig2, use_container_width=True)

        # --- Top merchants ---
        st.subheader("Top Merchants")
        merchants = (
            expenses.groupby("description")["amount"]
            .sum()
            .abs()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        fig3 = px.bar(
            merchants, x="amount", y="description", orientation="h"
        )
        st.plotly_chart(fig3, use_container_width=True)

        # --- Таблица транзакций ---
        st.subheader("Transactions")
        st.dataframe(
            expenses[
                ["started_date", "description", "category", "amount"]
            ].sort_values("started_date", ascending=False)
        )
