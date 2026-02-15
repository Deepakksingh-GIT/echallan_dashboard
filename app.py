import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="E-Challan Dashboard", layout="wide")

st.title("🚦 E-Challan Analytics Dashboard")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("echallan_daily_data.csv")
    return df

df = load_data()

# Sidebar Filter
st.sidebar.header("Filter Data")

if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"])
    start_date = st.sidebar.date_input("Start Date", df["Date"].min())
    end_date = st.sidebar.date_input("End Date", df["Date"].max())
    df = df[(df["Date"] >= pd.to_datetime(start_date)) & 
            (df["Date"] <= pd.to_datetime(end_date))]

# Clean Column Names
df.columns = df.columns.str.strip()      # remove extra spaces
df.columns = df.columns.str.replace(" ", "_")  # replace space with underscore
df.columns = df.columns.str.lower()      # make lowercase

st.write("Columns in dataset:", df.columns)

# KPI Section
st.subheader("📊 Key Performance Indicators")

total_challans = df["Challan_Count"].sum()
total_amount = df["Total_Amount"].sum()
avg_amount = df["Total_Amount"].mean()

col1, col2, col3 = st.columns(3)

col1.metric("Total Challans", total_challans)
col2.metric("Total Amount Collected", f"₹ {total_amount:,.0f}")
col3.metric("Average Amount per Day", f"₹ {avg_amount:,.0f}")

# Charts Section
st.subheader("📈 Visual Analytics")

# Line Chart
fig_line = px.line(df, x="Date", y="Challan_Count",
                   title="Daily Challan Trend")
st.plotly_chart(fig_line, use_container_width=True)

# Bar Chart
fig_bar = px.bar(df, x="Violation_Type", y="Challan_Count",
                 title="Challan by Violation Type")
st.plotly_chart(fig_bar, use_container_width=True)

# Pie Chart
fig_pie = px.pie(df, names="Violation_Type",
                 values="Challan_Count",
                 title="Violation Distribution")
st.plotly_chart(fig_pie, use_container_width=True)

# Area Chart
fig_area = px.area(df, x="Date", y="Total_Amount",
                   title="Revenue Over Time")
st.plotly_chart(fig_area, use_container_width=True)
