import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Fitness Watch Dashboard", layout="wide")
st.title("⌚ Women's Fitness Smartwatch Analysis")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("fit_watches_flipkart.csv")
    return df

df = load_data()

# ---------------- CLEAN COLUMN NAMES ----------------
df.columns = df.columns.str.strip().str.lower()

# ---------------- CLEAN PRICE ----------------
df["current price"] = (
    df["current price"]
    .astype(str)
    .str.replace("₹", "", regex=False)
    .str.replace(",", "", regex=False)
)
df["current price"] = pd.to_numeric(df["current price"], errors="coerce")

# ---------------- CLEAN DISCOUNT ----------------
if "discount %" in df.columns:
    df["discount %"] = df["discount %"].astype(str).str.replace("%", "")
    df["discount %"] = pd.to_numeric(df["discount %"], errors="coerce")

# ---------------- DROP NULLS ----------------
df = df.dropna(subset=["current price"])

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔎 Filters")

# Brand filter
if "brand" in df.columns:
    brands = st.sidebar.multiselect(
        "Select Brand",
        df["brand"].unique(),
        default=df["brand"].unique()
    )
    df = df[df["brand"].isin(brands)]

# Price filter
min_price = int(df["current price"].min())
max_price = int(df["current price"].max())

price_range = st.sidebar.slider(
    "Price Range",
    min_price,
    max_price,
    (min_price, max_price)
)

df = df[
    (df["current price"] >= price_range[0]) &
    (df["current price"] <= price_range[1])
]

# ---------------- FEATURE PROCESSING ----------------
for col in ["heart rate monitor", "health features", "smart functions",
            "step count", "calorie count"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.lower()

# Create feature flags
df["Heart Rate"] = df["heart rate monitor"].str.contains("yes|heart|hr", na=False)
df["Step Count"] = df["step count"].str.contains("yes|step", na=False)
df["Calorie Count"] = df["calorie count"].str.contains("yes|calorie", na=False)

df["Sleep Tracking"] = df["health features"].str.contains("sleep", na=False)
df["Stress Tracking"] = df["health features"].str.contains("stress", na=False)
df["Female Cycle"] = df["health features"].str.contains("cycle|period", na=False)

df["Sports Modes"] = df["smart functions"].str.contains("sport|mode", na=False)

feature_cols = [
    "Heart Rate", "Step Count", "Calorie Count",
    "Sleep Tracking", "Stress Tracking",
    "Female Cycle", "Sports Modes"
]

# Convert True/False → Yes/No
for col in feature_cols:
    df[col] = df[col].map({True: "Yes", False: "No"})

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📄 Data", "📊 EDA", "🚀 Features"])

# ---------------- TAB 1 ----------------
with tab1:
    st.subheader("Dataset")
    st.dataframe(df)

# ---------------- TAB 2 ----------------
with tab2:

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Watches", len(df))
    col2.metric("Avg Price", int(df["current price"].mean()))
    col3.metric("Max Price", int(df["current price"].max()))

    # Price distribution
    st.subheader("💰 Price Distribution")
    fig, ax = plt.subplots()
    sns.histplot(df["current price"], kde=True, ax=ax)
    st.pyplot(fig)

    # Discount vs Price
    if "discount %" in df.columns:
        st.subheader("📉 Discount vs Price")
        fig2, ax2 = plt.subplots()
        sns.scatterplot(x="discount %", y="current price", data=df, ax=ax2)
        st.pyplot(fig2)

    # Brand distribution
    if "brand" in df.columns:
        st.subheader("🏷️ Top Brands")
        fig3, ax3 = plt.subplots()
        df["brand"].value_counts().head(10).plot(kind="bar", ax=ax3)
        st.pyplot(fig3)

# ---------------- TAB 3 ----------------
with tab3:

    st.subheader("🔍 Feature Availability per Watch")

    display_cols = ["name", "brand", "current price"] + feature_cols
    display_cols = [c for c in display_cols if c in df.columns]

    st.dataframe(df[display_cols])

    # -------- FEATURE FILTER --------
    st.subheader("🎯 Filter by Features")

    selected_features = st.multiselect(
        "Select Features",
        feature_cols
    )

    filtered_df = df.copy()

    for feat in selected_features:
        filtered_df = filtered_df[filtered_df[feat] == "Yes"]

    st.write(f"Matching Watches: {len(filtered_df)}")
    st.dataframe(filtered_df[display_cols])

    # -------- FEATURE COUNT --------
    st.subheader("📊 Feature Availability Count")

    counts = {}
    for col in feature_cols:
        counts[col] = (df[col] == "Yes").sum()

    st.bar_chart(pd.DataFrame.from_dict(counts, orient="index", columns=["Count"]))

    # -------- OUTLIER DETECTION --------
    st.subheader("🚨 Outliers (IQR)")

    numeric_df = df.select_dtypes(include=["int64", "float64"])

    for col in numeric_df.columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]
        st.write(f"{col}: {len(outliers)} outliers")

    # Boxplot
    st.subheader("📦 Boxplot")
    fig4, ax4 = plt.subplots()
    sns.boxplot(data=numeric_df, ax=ax4)
    st.pyplot(fig4)