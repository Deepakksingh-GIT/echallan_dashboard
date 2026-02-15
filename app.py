import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="E-Challan Pro Dashboard",
                   layout="wide",
                   page_icon="🚦")

st.title("🚦 E-Challan Analytics Dashboard (Professional Version)")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("echallan_daily_data.csv")
    
    # Clean column names
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(" ", "_")
    df.columns = df.columns.str.lower()
    
    return df

df = load_data()

if df.empty:
    st.error("Dataset is empty.")
    st.stop()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

# Date Filter
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    
    start_date = st.sidebar.date_input("Start Date", df["date"].min())
    end_date = st.sidebar.date_input("End Date", df["date"].max())
    
    df = df[(df["date"] >= pd.to_datetime(start_date)) &
            (df["date"] <= pd.to_datetime(end_date))]

# Violation Filter
if "violation_type" in df.columns:
    violation = st.sidebar.multiselect(
        "Select Violation Type",
        options=df["violation_type"].unique(),
        default=df["violation_type"].unique()
    )
    df = df[df["violation_type"].isin(violation)]

# Top N
top_n = st.sidebar.slider("Select Top N Violations", 1, 20, 5)

# KPI Selector
st.sidebar.header("📊 KPI Selection")
kpi_option = st.sidebar.radio(
    "Choose KPI",
    ["All KPIs", "Total Challans", "Total Revenue", "Average Revenue"]
)

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_challans = df["challan_count"].sum() if "challan_count" in df.columns else 0
total_amount = df["total_amount"].sum() if "total_amount" in df.columns else 0
avg_amount = df["total_amount"].mean() if "total_amount" in df.columns else 0

# Growth Calculation (if date available)
growth = 0
if "date" in df.columns and "challan_count" in df.columns:
    trend = df.groupby("date")["challan_count"].sum().reset_index()
    if len(trend) > 1:
        growth = ((trend["challan_count"].iloc[-1] -
                   trend["challan_count"].iloc[0])
                  / trend["challan_count"].iloc[0]) * 100

# --------------------------------------------------
# KPI DISPLAY
# --------------------------------------------------
st.subheader("📊 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

if kpi_option == "All KPIs":
    col1.metric("Total Challans", f"{total_challans:,}",
                f"{growth:.2f}% Growth")
    col2.metric("Total Revenue", f"₹ {total_amount:,.0f}")
    col3.metric("Average Revenue", f"₹ {avg_amount:,.0f}")

elif kpi_option == "Total Challans":
    col1.metric("Total Challans", f"{total_challans:,}",
                f"{growth:.2f}% Growth")

elif kpi_option == "Total Revenue":
    col2.metric("Total Revenue", f"₹ {total_amount:,.0f}")

elif kpi_option == "Average Revenue":
    col3.metric("Average Revenue", f"₹ {avg_amount:,.0f}")

# --------------------------------------------------
# TOP N DATA
# --------------------------------------------------
top_data = pd.DataFrame()

if "violation_type" in df.columns and "challan_count" in df.columns:
    grouped = (
        df.groupby("violation_type", as_index=False)["challan_count"]
        .sum()
        .sort_values(by="challan_count", ascending=False)
    )
    
    if not grouped.empty:
        top_data = grouped.head(top_n)

# --------------------------------------------------
# CHARTS
# --------------------------------------------------
st.subheader("📈 Visual Analytics")

# 1️⃣ Top N Bar Chart
if not top_data.empty:
    fig_bar = px.bar(
        top_data,
        x="violation_type",
        y="challan_count",
        title=f"Top {top_n} Violations"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# 2️⃣ Line Chart
if "date" in df.columns and "challan_count" in df.columns:
    trend_data = df.groupby("date")["challan_count"].sum().reset_index()
    fig_line = px.line(
        trend_data,
        x="date",
        y="challan_count",
        title="Daily Challan Trend"
    )
    st.plotly_chart(fig_line, use_container_width=True)

# 3️⃣ Revenue Area
if "date" in df.columns and "total_amount" in df.columns:
    revenue_data = df.groupby("date")["total_amount"].sum().reset_index()
    fig_area = px.area(
        revenue_data,
        x="date",
        y="total_amount",
        title="Revenue Over Time"
    )
    st.plotly_chart(fig_area, use_container_width=True)

# 4️⃣ Pie Chart
if not top_data.empty:
    fig_pie = px.pie(
        top_data,
        names="violation_type",
        values="challan_count",
        title="Violation Distribution"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 5️⃣ Scatter Plot
if "challan_count" in df.columns and "total_amount" in df.columns:
    fig_scatter = px.scatter(
        df,
        x="challan_count",
        y="total_amount",
        title="Challan vs Revenue"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# 6️⃣ Heatmap
numeric_df = df.select_dtypes(include=["float64", "int64"])
if not numeric_df.empty:
    st.subheader("🔥 Correlation Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# --------------------------------------------------
# DOWNLOAD BUTTON
# --------------------------------------------------
st.subheader("⬇ Download Filtered Data")
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_echallan_data.csv",
    mime="text/csv",
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown("🚀 Built by Deepak | Streamlit Professional Dashboard")
