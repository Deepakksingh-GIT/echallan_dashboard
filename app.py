import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="E-Challan BI Dashboard",
                   layout="wide",
                   page_icon="🚦")

st.title("🚦 E-Challan Business Intelligence Dashboard")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("echallan_daily_data.csv")
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
    start = st.sidebar.date_input("Start Date", df["date"].min())
    end = st.sidebar.date_input("End Date", df["date"].max())
    df = df[(df["date"] >= pd.to_datetime(start)) &
            (df["date"] <= pd.to_datetime(end))]

# Category Filter
categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
selected_category_col = None

if categorical_cols:
    selected_category_col = st.sidebar.selectbox(
        "Select Category Column",
        categorical_cols
    )
    selected_values = st.sidebar.multiselect(
        "Select Values",
        df[selected_category_col].unique(),
        default=df[selected_category_col].unique()
    )
    df = df[df[selected_category_col].isin(selected_values)]

# Top N
top_n = st.sidebar.slider("Select Top N", 1, 20, 5)

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.sidebar.header("📊 KPI Selection")
kpi_option = st.sidebar.radio(
    "Choose KPI",
    ["All KPIs", "Numeric Column Summary"]
)

numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

st.subheader("📊 Key Performance Indicators")

if numeric_cols:
    selected_kpi_col = st.selectbox("Select KPI Column", numeric_cols)

    total = df[selected_kpi_col].sum()
    avg = df[selected_kpi_col].mean()
    max_val = df[selected_kpi_col].max()

    col1, col2, col3 = st.columns(3)

    if kpi_option == "All KPIs":
        col1.metric("Total", f"{total:,.0f}")
        col2.metric("Average", f"{avg:,.2f}")
        col3.metric("Maximum", f"{max_val:,.0f}")

    else:
        col1.metric("Total", f"{total:,.0f}")

# --------------------------------------------------
# DYNAMIC CHART OPTIONS
# --------------------------------------------------
st.sidebar.header("📈 Chart Options")

chart_type = st.sidebar.selectbox(
    "Select Chart Type",
    ["Bar Chart", "Line Chart", "Pie Chart",
     "Histogram", "Area Chart",
     "Scatter Plot", "Heatmap"]
)

# Axis Selection
x_axis = None
y_axis = None

if numeric_cols:
    x_axis = st.sidebar.selectbox("Select X-Axis", df.columns)
    y_axis = st.sidebar.selectbox("Select Y-Axis (Numeric)", numeric_cols)

# --------------------------------------------------
# CHART DISPLAY
# --------------------------------------------------
st.subheader("📈 Dynamic Visualization")

if chart_type == "Bar Chart":
    if x_axis and y_axis:
        grouped = df.groupby(x_axis, as_index=False)[y_axis].sum()
        grouped = grouped.sort_values(by=y_axis, ascending=False).head(top_n)
        fig = px.bar(grouped, x=x_axis, y=y_axis,
                     title="Bar Chart")
        st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Line Chart":
    if x_axis and y_axis:
        grouped = df.groupby(x_axis, as_index=False)[y_axis].sum()
        fig = px.line(grouped, x=x_axis, y=y_axis,
                      title="Line Chart")
        st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Pie Chart":
    if x_axis and y_axis:
        grouped = df.groupby(x_axis, as_index=False)[y_axis].sum()
        grouped = grouped.head(top_n)
        fig = px.pie(grouped, names=x_axis,
                     values=y_axis,
                     title="Pie Chart")
        st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Histogram":
    if y_axis:
        fig = px.histogram(df, x=y_axis,
                           title="Histogram")
        st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Area Chart":
    if x_axis and y_axis:
        grouped = df.groupby(x_axis, as_index=False)[y_axis].sum()
        fig = px.area(grouped, x=x_axis, y=y_axis,
                      title="Area Chart")
        st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Scatter Plot":
    if x_axis and y_axis:
        fig = px.scatter(df,
                         x=x_axis,
                         y=y_axis,
                         title="Scatter Plot")
        st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Heatmap":
    numeric_df = df.select_dtypes(include=["int64", "float64"])
    if not numeric_df.empty:
        fig, ax = plt.subplots()
        sns.heatmap(numeric_df.corr(),
                    annot=True,
                    cmap="coolwarm",
                    ax=ax)
        st.pyplot(fig)

# --------------------------------------------------
# DOWNLOAD BUTTON
# --------------------------------------------------
st.subheader("⬇ Download Filtered Data")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_data.csv",
    mime="text/csv"
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown("🚀 Built by Deepak | Streamlit BI Dashboard")
