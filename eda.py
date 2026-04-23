import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- LOAD DATA ----------------
df = pd.read_csv("fit_watches_flipkart.csv")

print("Columns in dataset:")
print(df.columns)

# ---------------- CLEAN COLUMN NAMES ----------------
df.columns = df.columns.str.strip().str.lower()

# ---------------- CLEAN PRICE ----------------
if "current price" in df.columns:
    df["current price"] = (
        df["current price"]
        .astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df["current price"] = pd.to_numeric(df["current price"], errors="coerce")

# ---------------- CLEAN DISCOUNT ----------------
if "discount %" in df.columns:
    df["discount %"] = (
        df["discount %"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )
    df["discount %"] = pd.to_numeric(df["discount %"], errors="coerce")

# ---------------- DROP NULLS ----------------
if "current price" in df.columns:
    df = df.dropna(subset=["current price"])

# ---------------- STYLE ----------------
sns.set_style("whitegrid")

# ---------------- PRICE DISTRIBUTION ----------------
if "current price" in df.columns:
    plt.figure()
    sns.histplot(df["current price"], bins=20, kde=True)
    plt.title("Price Distribution")
    plt.show()

# ---------------- DISCOUNT VS PRICE ----------------
if "discount %" in df.columns and "current price" in df.columns:
    plt.figure()
    sns.scatterplot(x="discount %", y="current price", data=df)
    plt.title("Discount vs Price")
    plt.show()

# ---------------- BRAND DISTRIBUTION ----------------
brand_col = None
for col in ["brand", "brands", "company"]:
    if col in df.columns:
        brand_col = col
        break

if brand_col:
    plt.figure()
    df[brand_col].value_counts().head(10).plot(kind="bar")
    plt.title("Top Brands")
    plt.xticks(rotation=45)
    plt.show()

# ---------------- CATEGORY DISTRIBUTION ----------------
cat_col = None
for col in ["category", "type"]:
    if col in df.columns:
        cat_col = col
        break

if cat_col:
    plt.figure()
    df[cat_col].value_counts().plot(kind="bar")
    plt.title("Category Distribution")
    plt.xticks(rotation=45)
    plt.show()

# ---------------- CORRELATION HEATMAP ----------------
numeric_df = df.select_dtypes(include=["int64", "float64"])

if not numeric_df.empty:
    plt.figure(figsize=(10,6))
    sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm")
    plt.title("Correlation Heatmap")
    plt.show()

# ================= OUTLIER DETECTION (FIXED) =================

print("\n🔎 Identifying Outliers using IQR Method:")

numeric_cols = numeric_df.columns
outliers_found = False

for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    column_outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

    if not column_outliers.empty:
        outliers_found = True
        print(f"\nColumn: {col}")
        print(f"Outliers count: {len(column_outliers)}")

# If no outliers
if not outliers_found:
    print("No outliers found.")

# ---------------- BOXPLOT (VISUAL OUTLIERS) ----------------
if not numeric_df.empty:
    plt.figure(figsize=(10,5))
    sns.boxplot(data=numeric_df)
    plt.title("Boxplot for Outlier Detection")
    plt.xticks(rotation=45)
    plt.show()