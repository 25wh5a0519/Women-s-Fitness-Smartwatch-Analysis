import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="FitWatch Studio",
    page_icon="⌚",
    layout="wide"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"]{
    font-family: 'Poppins', sans-serif;
}

.stApp{
    background:
    linear-gradient(135deg,#0f172a,#111827,#1e1b4b,#3b0764);
    color:white;
}

/* MAIN */
.main .block-container{
    padding-top:2rem;
    max-width:1400px;
}

/* SIDEBAR */
section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#1e1b4b,#0f172a);
    border-right:2px solid rgba(255,255,255,0.08);
}

/* HERO */
.hero-box{
    background:
    linear-gradient(135deg,#ff0080,#7928ca,#00c6ff);
    padding:3rem;
    border-radius:28px;
    box-shadow:0 0 40px rgba(255,255,255,0.15);
    margin-bottom:2rem;
}

.hero-title{
    font-size:60px;
    font-weight:700;
    color:white;
}

.hero-sub{
    font-size:18px;
    color:#f3f4f6;
    line-height:1.8;
}

/* KPI CARDS */
.kpi-card{
    padding:1.5rem;
    border-radius:24px;
    text-align:center;
    color:white;
    margin-bottom:1rem;
    box-shadow:0 10px 30px rgba(0,0,0,0.3);
    transition:0.3s;
}

.kpi-card:hover{
    transform:translateY(-5px) scale(1.02);
}

/* DATAFRAME */
.stDataFrame{
    border-radius:18px;
    overflow:hidden;
    border:1px solid rgba(255,255,255,0.1);
}

/* TABS */
[data-baseweb="tab-list"]{
    gap:12px;
}

[data-baseweb="tab"]{
    background:#111827;
    border-radius:14px;
    color:#cbd5e1;
    padding:12px 25px;
    font-weight:600;
}

[aria-selected="true"][data-baseweb="tab"]{
    background:linear-gradient(135deg,#ff0080,#7928ca);
    color:white;
}

/* BUTTON */
.stButton button{
    background:linear-gradient(135deg,#00c6ff,#0072ff);
    color:white;
    border:none;
    border-radius:14px;
    padding:10px 24px;
    font-weight:bold;
}

/* SECTION TITLE */
.section-title{
    font-size:28px;
    font-weight:700;
    margin-top:1rem;
    margin-bottom:1rem;
}

/* METRIC COLORS */
.pink{
    color:#ff4ecd;
}

.blue{
    color:#38bdf8;
}

.green{
    color:#4ade80;
}

.orange{
    color:#fbbf24;
}

/* FEATURE BOX */
.feature-box{
    background:rgba(255,255,255,0.06);
    border:1px solid rgba(255,255,255,0.08);
    padding:1.2rem;
    border-radius:20px;
    margin-bottom:1rem;
}

/* FOOTER */
.footer{
    text-align:center;
    color:#d1d5db;
    padding:2rem;
    font-size:15px;
}

</style>
""", unsafe_allow_html=True)

# ================= LOAD DATA =================
@st.cache_data
def load_data():

    df = pd.read_csv("fit_watches_flipkart.csv")

    df.columns = df.columns.str.strip().str.lower()

    # CLEAN PRICE
    df["current price"] = (
        df["current price"]
        .astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
    )

    df["current price"] = pd.to_numeric(
        df["current price"],
        errors="coerce"
    )

    # CLEAN DISCOUNT
    if "discount %" in df.columns:
        df["discount %"] = (
            df["discount %"]
            .astype(str)
            .str.replace("%", "")
        )

        df["discount %"] = pd.to_numeric(
            df["discount %"],
            errors="coerce"
        )

    df = df.dropna(subset=["current price"])

    # FEATURE PROCESSING
    for col in [
        "heart rate monitor",
        "health features",
        "smart functions",
        "step count",
        "calorie count"
    ]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower()

    df["Heart Rate"] = df["heart rate monitor"].str.contains("yes|heart|hr", na=False)
    df["Step Count"] = df["step count"].str.contains("yes|step", na=False)
    df["Calorie Count"] = df["calorie count"].str.contains("yes|calorie", na=False)
    df["Sleep Tracking"] = df["health features"].str.contains("sleep", na=False)
    df["Stress Tracking"] = df["health features"].str.contains("stress", na=False)
    df["Female Cycle"] = df["health features"].str.contains("cycle|period", na=False)
    df["Sports Modes"] = df["smart functions"].str.contains("sport|mode", na=False)

    feature_cols = [
        "Heart Rate",
        "Step Count",
        "Calorie Count",
        "Sleep Tracking",
        "Stress Tracking",
        "Female Cycle",
        "Sports Modes"
    ]

    for col in feature_cols:
        df[col] = df[col].map({
            True: "Yes",
            False: "No"
        })

    return df, feature_cols

df, feature_cols = load_data()

# ================= SIDEBAR =================
with st.sidebar:

    st.markdown("""
    <center>
        <h1 style='color:#ff4ecd;'>⌚ FitWatch</h1>
        
    </center>
    """, unsafe_allow_html=True)

    brands = st.multiselect(
        "🏷️ Select Brand",
        options=sorted(df["brand"].unique()),
        default=sorted(df["brand"].unique())
    )

    min_price = int(df["current price"].min())
    max_price = int(df["current price"].max())

    price_range = st.slider(
        "💰 Price Range",
        min_price,
        max_price,
        (min_price, max_price)
    )

# ================= FILTER DATA =================
filtered_df = df.copy()

filtered_df = filtered_df[
    filtered_df["brand"].isin(brands)
]

filtered_df = filtered_df[
    (filtered_df["current price"] >= price_range[0]) &
    (filtered_df["current price"] <= price_range[1])
]

# ================= HERO SECTION =================
st.markdown(f"""
<div class="hero-box">

<div class="hero-title">
⌚ FitWatch Studio
</div>

<div class="hero-sub">

Explore premium women's smartwatch analytics with stylish visuals,
interactive watch filtering,
smart feature discovery,
and colorful insights dashboard.

</div>

</div>
""", unsafe_allow_html=True)

# ================= KPI SECTION =================
total = len(filtered_df)
avg_price = int(filtered_df["current price"].mean())
max_price = int(filtered_df["current price"].max())
min_price = int(filtered_df["current price"].min())

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card"
    style="background:linear-gradient(135deg,#ff0080,#ff4ecd);">

    <h1>⌚</h1>

    <h2>{total:,}</h2>

    <p>Total Watches</p>

    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card"
    style="background:linear-gradient(135deg,#00c6ff,#0072ff);">

    <h1>💰</h1>

    <h2>₹{avg_price:,}</h2>

    <p>Average Price</p>

    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card"
    style="background:linear-gradient(135deg,#00ff87,#60efff);">

    <h1>🏆</h1>

    <h2>₹{max_price:,}</h2>

    <p>Highest Price</p>

    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card"
    style="background:linear-gradient(135deg,#ffb347,#ffcc33);">

    <h1>🛒</h1>

    <h2>₹{min_price:,}</h2>

    <p>Lowest Price</p>

    </div>
    """, unsafe_allow_html=True)

# ================= TABS =================
tab1, tab2, tab3 = st.tabs([
    "📄 Smartwatch Data",
    "📊 Analytics",
    "🚀 Features"
])

# ==================================================
# TAB 1
# ==================================================
with tab1:

    st.markdown("""
    <div class="section-title pink">
    📄 Smartwatch 
    </div>
    """, unsafe_allow_html=True)

    search = st.text_input("🔍 Search Watch")

    view_df = filtered_df.copy()

    if search:

        mask = view_df.apply(
            lambda row: row.astype(str).str.contains(
                search,
                case=False
            ).any(),
            axis=1
        )

        view_df = view_df[mask]

    st.dataframe(
        view_df,
        use_container_width=True,
        height=500
    )

# ==================================================
# TAB 2
# ==================================================
with tab2:

    st.markdown("""
    <div class="section-title blue">
    💰 Price Distribution
    </div>
    """, unsafe_allow_html=True)

    fig1, ax1 = plt.subplots(figsize=(10,4))

    sns.histplot(
        filtered_df["current price"],
        kde=True,
        color="#00c8ffb4",
        ax=ax1
    )

    st.pyplot(fig1)

    # TOP BRANDS
    st.markdown("""
    <div class="section-title green">
    🏷️ Top Brands
    </div>
    """, unsafe_allow_html=True)

    fig2, ax2 = plt.subplots(figsize=(10,5))

    filtered_df["brand"].value_counts().head(10).plot(
        kind="bar",
        color=[
            "#a94eff",
            "#00ffb7",
            "#00ffea",
            "#be3dff",
            "#dd4ec5",
            "#ff6ba6",
            "#38cff8",
            "#f472b6",
            "#15fad4",
            "#4ade80b2"
        ],
        ax=ax2
    )

    st.pyplot(fig2)

    # SCATTER
    if "discount %" in filtered_df.columns:

        st.markdown("""
        <div class="section-title orange">
        📉 Discount vs Price
        </div>
        """, unsafe_allow_html=True)

        fig3, ax3 = plt.subplots(figsize=(8,5))

        sns.scatterplot(
            x="discount %",
            y="current price",
            data=filtered_df,
            color="#ff4ecdda",
            s=100,
            ax=ax3
        )

        st.pyplot(fig3)

# ==================================================
# TAB 3
# ==================================================
with tab3:

    st.markdown("""
    <div class="section-title pink">
    🚀 Feature Availability
    </div>
    """, unsafe_allow_html=True)

    counts = {}

    for col in feature_cols:
        counts[col] = (filtered_df[col] == "Yes").sum()

    chart_df = pd.DataFrame({
        "Feature": list(counts.keys()),
        "Count": list(counts.values())
    })

    fig4, ax4 = plt.subplots(figsize=(10,5))

    sns.barplot(
        x="Count",
        y="Feature",
        data=chart_df,
        palette=[
            "#ff0080",
            "#00c6ff",
            "#00ff87",
            "#ffd93d",
            "#9d4edd",
            "#ff6b6bb1",
            "#38bdf8"
        ],
        ax=ax4
    )

    st.pyplot(fig4)

    # FEATURE FILTER
    st.markdown("""
    <div class="section-title green">
    🎯 Filter Watches By Features
    </div>
    """, unsafe_allow_html=True)

    selected_features = st.multiselect(
        "Select Features",
        feature_cols
    )

    feature_df = filtered_df.copy()

    for feat in selected_features:
        feature_df = feature_df[
            feature_df[feat] == "Yes"
        ]

    display_cols = [
        "name",
        "brand",
        "current price"
    ] + feature_cols

    display_cols = [
        c for c in display_cols
        if c in feature_df.columns
    ]

    st.dataframe(
        feature_df[display_cols],
        use_container_width=True,
        height=400
    )

# ================= FOOTER =================
st.markdown("""
<div class="footer">

💎 FITWATCH STUDIO 

</div>
""", unsafe_allow_html=True)