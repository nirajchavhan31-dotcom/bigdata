import streamlit as st
import pandas as pd
import numpy as np
import time

st.title("📦 Real-Time Inventory Dashboard")

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Category", "Stock", "Price"])

categories = ["TV", "Mobile", "Laptop"]

def generate_data():
    return pd.DataFrame({
        "Category": np.random.choice(categories, 10),
        "Stock": np.random.randint(1, 100, 10),
        "Price": np.random.randint(1000, 5000, 10)
    })

# Add new data every run
new_data = generate_data()
st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)

df = st.session_state.data

# KPIs
total_stock = df["Stock"].sum()
avg_price = df["Price"].mean()
low_stock_df = df[df["Stock"] < 20]

stock_by_category = df.groupby("Category")["Stock"].sum()
avg_price_category = df.groupby("Category")["Price"].mean()

st.subheader("Live Inventory Data 📡")
st.dataframe(df.tail(10))

col1, col2, col3 = st.columns(3)
col1.metric("Total Stock", total_stock)
col2.metric("Avg Price", round(avg_price, 2))
col3.metric("Low Stock Items", len(low_stock_df))

# ALERT
if not low_stock_df.empty:
    st.error("🚨 Low Stock Alert!")
    st.dataframe(low_stock_df.tail(5))
else:
    st.success("✅ Stock levels are healthy")

st.subheader("Stock Distribution")
st.bar_chart(stock_by_category)

st.subheader("Average Price per Category")
st.bar_chart(avg_price_category)

# 🔁 Auto refresh
time.sleep(1)
st.rerun()