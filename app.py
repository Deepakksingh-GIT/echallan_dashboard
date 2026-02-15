import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="E-Challan Dashboard", layout="wide")
st.title("🚦 E-Challan Analytics Dashboard")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("echallan_daily_data.csv")
    
    # Clean column names
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(" ", "_")
    df.columns = df.columns.str.lower()
    
    return df

df = load_data()

st.write("### Dataset Preview")
st.dataframe(df.head())

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------
st.sidebar.header("🔍 Filter Options")

# If date column exists
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"])
    start_date = st.sidebar.date_input("Start Date", df["date"].min())
    end_date = st.sidebar.date_input("End Date", df["date"].max())
    
    df = df[(df["date"] >= pd.to_datetime(start_date)) &
            (df["date"] <= pd.to_datetime(end_date))]

# If violation_type exists
if "violation_type" in df.columns:
    violation = st.sidebar.multiselect(
        "Select Violation Type",
        df["violation_type"].unique(),
        default=df["violation_type"].unique()
    )
    df = df[df["violation_type"].isin(violation)]

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

if "challan_count" in df.columns:
    total_challans = df["challan_count"].sum()
else:
    total_challans = 0

if "total_amount" in df.columns:
    total_amount = df["total_amount"].sum()
    avg_amount = df["total_amount"].mean()
else:
    total_amount = 0
    avg_amount = 0

col1.metric("Total Challans", f"{total_challans:,}")
col2.metric("Total Revenue", f"₹ {total_amount:,.0f}")
col3.metric("Average Daily Revenue", f"₹ {avg_amount:,.0f}")

# ---------------------------------------------------
# CHARTS SECTION
# ---------------------------------------------------
st.subheader("📈 Visual Analytics")

# 1️⃣ Line Chart - Trend
if "date" in df.columns and "challan_count" in df.columns:
    fig_line = px.line(df, x="date", y="challan_count",
                       title="📅 Daily Challan Trend")
    st.plotly_chart(fig_line, use_container_width=True)

# 2️⃣ Bar Chart
if "violation_type" in df.columns and "challan_count" in df.columns:
    fig_bar = px.bar(df, x="violation_type", y="challan_count",
                     title="🚨 Challan by Violation Type")
    st.plotly_chart(fig_bar, use_container_width=True)

# 3️⃣ Pie Chart
if "violation_type" in df.columns and "challan_count" in df.columns:
    fig_pie = px.pie(df,
                     names="violation_type",
                     values="challan_count",
                     title="📊 Violation Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)

# 4️⃣ Area Chart - Revenue Trend
if "date" in df.columns and "total_amount" in df.columns:
    fig_area = px.area(df, x="date", y="total_amount",
                       title="💰 Revenue Over Time")
    st.plotly_chart(fig_area, use_container_width=True)

# 5️⃣ Scatter Plot
if "challan_count" in df.columns and "total_amount" in df.columns:
    fig_scatter = px.scatter(df,
                             x="challan_count",
                             y="total_amount",
                             title="🔎 Challan vs Revenue")
    st.plotly_chart(fig_scatter, use_container_width=True)

# 6️⃣ Correlation Heatmap
numeric_df = df.select_dtypes(include=['float64', 'int64'])

if not numeric_df.empty:
    st.subheader("🔥 Correlation Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
st.markdown("✅ Built with Streamlit | 🚀 Deploy on Streamlit Cloud")
