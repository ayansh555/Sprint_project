import pandas as pd
import numpy as np
import re


INPUT_FILE = "data/amazon-products.csv"
OUTPUT_FILE = "data/amazon_products_converted.csv"


def clean_text(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


def clean_number(value):
    """
    Converts values such as:
    "57.79"
    '"57.79"'
    57.79
    "$57.79"
    "1,299"
    into float.
    """

    if pd.isna(value):
        return 0.0

    value = str(value).strip()

    if not value:
        return 0.0

    # Remove quotes
    value = value.replace('"', "")
    value = value.replace("'", "")

    # Remove currency symbols and commas
    value = re.sub(r"[^0-9.\-]", "", value)

    try:
        return float(value)
    except ValueError:
        return 0.0


def clean_integer(value):
    if pd.isna(value):
        return 0

    value = str(value).strip()

    if not value:
        return 0

    value = value.replace('"', "")
    value = value.replace("'", "")
    value = value.replace(",", "")

    numbers = re.findall(r"\d+", value)

    if not numbers:
        return 0

    try:
        return int(numbers[0])
    except ValueError:
        return 0


print("Reading Amazon dataset...")

df = pd.read_csv(
    INPUT_FILE,
    keep_default_na=False
)

print("Amazon products:", len(df))


converted = pd.DataFrame()


# ============================================================
# BASIC PRODUCT INFORMATION
# ============================================================

converted["Product_ID"] = (
    df["asin"]
    .apply(clean_text)
)

converted["Product_Name"] = (
    df["title"]
    .apply(clean_text)
)

converted["Product_Brand_Name"] = (
    df["brand"]
    .apply(clean_text)
)

converted["Product_Category"] = (
    df["categories"]
    .apply(clean_text)
)

converted["Product_Description"] = (
    df["description"]
    .apply(clean_text)
)

converted["User_Reviews"] = (
    df["top_review"]
    .apply(clean_text)
)


# ============================================================
# NUMERIC INFORMATION
# ============================================================

converted["Rating"] = (
    df["rating"]
    .apply(clean_number)
)

converted["Price_of_Product"] = (
    df["final_price"]
    .apply(clean_number)
)

# If final price is missing/zero, use initial price
initial_prices = (
    df["initial_price"]
    .apply(clean_number)
)

converted.loc[
    converted["Price_of_Product"] <= 0,
    "Price_of_Product"
] = initial_prices[
    converted["Price_of_Product"] <= 0
]


converted["Quantity_Sold"] = (
    df["bought_past_month"]
    .apply(clean_integer)
)


# ============================================================
# WEBSITE INFORMATION
# ============================================================

converted["Sold_On_Websites"] = "Amazon"

converted["Warranty"] = ""

converted["Product_In_Sites"] = "Amazon"

converted["Sites_Available"] = "Amazon"


# ============================================================
# RATING LEVEL
# ============================================================

converted["Rating_Level"] = converted["Rating"].apply(
    lambda x:
        "High" if x >= 4.0
        else "Medium" if x >= 3.0
        else "Low"
)


# ============================================================
# PRICE LEVEL
# ============================================================

def get_price_level(price):

    if price <= 0:
        return "Unknown"

    if price < 50:
        return "Low"

    if price < 200:
        return "Medium"

    return "High"


converted["Price_Level"] = (
    converted["Price_of_Product"]
    .apply(get_price_level)
)


# ============================================================
# REVIEW SUMMARY
# ============================================================

converted["Overall_Product_Review"] = (
    converted["Rating"].apply(
        lambda x:
            "Excellent" if x >= 4.5
            else "Very Good" if x >= 4.0
            else "Good" if x >= 3.0
            else "Average"
    )
)


converted["Average_Product_Ordered"] = (
    converted["Quantity_Sold"]
)


# ============================================================
# RECOMMENDATION SCORE
# ============================================================

converted["Recommendation_Score"] = (
    converted["Rating"] * 20
    + np.log1p(
        converted["Quantity_Sold"]
    ) * 5
).round(2)


converted["Product_Recommendation"] = (
    converted["Recommendation_Score"].apply(
        lambda x:
            "Highly Recommended"
            if x >= 90
            else "Recommended"
            if x >= 75
            else "Consider"
    )
)


# ============================================================
# SEARCH TEXT
# ============================================================

converted["Search_Text"] = (
    converted["Product_Name"]
    + " "
    + converted["Product_Brand_Name"]
    + " "
    + converted["Product_Category"]
    + " "
    + converted["Product_Description"]
    + " "
    + converted["User_Reviews"]
).str.replace(
    r"\s+",
    " ",
    regex=True
).str.strip()


# ============================================================
# REAL IMAGE + PRODUCT URL
# ============================================================

converted["Image_URL"] = (
    df["image_url"]
    .apply(clean_text)
)

converted["Product_URL"] = (
    df["url"]
    .apply(clean_text)
)


# ============================================================
# SAVE
# ============================================================

converted.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# VERIFICATION
# ============================================================

print()
print("=" * 60)
print("CONVERSION COMPLETED")
print("=" * 60)

print(
    "Total products:",
    len(converted)
)

print(
    "Products with price:",
    (converted["Price_of_Product"] > 0).sum()
)

print(
    "Products with images:",
    converted["Image_URL"].ne("").sum()
)

print(
    "Products with product URLs:",
    converted["Product_URL"].ne("").sum()
)

print(
    "Products with zero price:",
    (converted["Price_of_Product"] == 0).sum()
)

print("=" * 60)