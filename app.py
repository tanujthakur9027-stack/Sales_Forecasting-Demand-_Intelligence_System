
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Forecasting Dashboard", page_icon="📈", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("train.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    if "Ship Date" in df.columns:
        df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=True, errors="coerce")
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month_name()
    return df

df = load_data()

st.title("📈 Sales Forecasting & Demand Intelligence System")

page = st.sidebar.selectbox(
    "Navigation",
    ["Sales Overview","Forecast Explorer","Anomaly Report","Demand Segments"]
)

if page == "Sales Overview":
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Sales", f"${df['Sales'].sum():,.0f}")
    c2.metric("Orders", len(df))
    c3.metric("Categories", df["Category"].nunique())

    monthly = df.groupby(pd.Grouper(key="Order Date",freq="ME"))["Sales"].sum().reset_index()
    st.plotly_chart(
        px.line(monthly,x="Order Date",y="Sales",markers=True,title="Monthly Sales"),
        width="stretch"
    )

    region = df.groupby("Region")["Sales"].sum().reset_index()
    st.plotly_chart(
        px.bar(region,x="Region",y="Sales",title="Sales by Region"),
        width="stretch"
    )

    cat = df.groupby("Category")["Sales"].sum().reset_index()
    st.plotly_chart(
        px.pie(cat,names="Category",values="Sales",hole=0.45,title="Category Share"),
        width="stretch"
    )

elif page == "Forecast Explorer":
    st.header("Forecast Explorer")
    try:
        cmp = pd.read_csv("model_comparison.csv")
        st.dataframe(cmp, width="stretch")
    except Exception:
        st.warning("model_comparison.csv not found.")

    by = st.radio("View trend by",["Category","Region"])

    if by=="Category":
        value = st.selectbox("Category", sorted(df["Category"].dropna().unique()))
        temp = df[df["Category"]==value]
    else:
        value = st.selectbox("Region", sorted(df["Region"].dropna().unique()))
        temp = df[df["Region"]==value]

    trend = temp.groupby(pd.Grouper(key="Order Date",freq="ME"))["Sales"].sum().reset_index()
    st.plotly_chart(
        px.line(trend,x="Order Date",y="Sales",markers=True,title=f"{value} Sales Trend"),
        width="stretch"
    )

elif page == "Anomaly Report":
    st.header("Anomaly Report")
    try:
        anomaly = pd.read_csv("anomaly_report.csv")
        st.dataframe(anomaly, width="stretch")
        if "Order Date" in anomaly.columns:
            anomaly["Order Date"] = pd.to_datetime(anomaly["Order Date"], errors="coerce")
            st.plotly_chart(
                px.line(anomaly,x="Order Date",y="Sales",title="Anomaly Timeline"),
                width="stretch"
            )
    except Exception:
        st.warning("anomaly_report.csv not found.")

elif page == "Demand Segments":
    st.header("Demand Segments")
    try:
        product = pd.read_csv("product_clusters.csv")
        st.dataframe(product, width="stretch")
        if {"PC1","PC2","Cluster"}.issubset(product.columns):
            st.plotly_chart(
                px.scatter(product,x="PC1",y="PC2",color=product["Cluster"].astype(str),
                           hover_name="Sub-Category"),
                width="stretch"
            )
    except Exception:
        st.warning("product_clusters.csv not found.")
