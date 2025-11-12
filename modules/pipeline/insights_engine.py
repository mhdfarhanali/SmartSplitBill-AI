import pandas as pd
from modules.utils import format_number_to_currency

# BASIC INSIGHTS + CHAT SUPPORT


def analyze_receipt_with_ai(receipt_dict: dict, query: str = None):
    """
    Analyze receipt data for insights or answer AI chat queries.

    Parameters
    ----------
    receipt_dict : dict
        Dictionary containing receipt structure {items, total, ...}
    query : str, optional
        Natural language question (e.g. 'What’s the most expensive item?')

    Returns
    -------
    pd.DataFrame | str
        - DataFrame (for analytics view)
        - String response (for chat assistant)
    """
    items = pd.DataFrame(receipt_dict.get("items", []))

    if items.empty:
        return "❌ No items detected in this receipt." if query else pd.DataFrame([{"message": "No items detected"}])

    if "price" not in items.columns:
        raise ValueError("Invalid receipt format: missing 'price' column.")

    if "category" not in items.columns:
        items["category"] = "Others"

    # Base Summary
    summary = (
        items.groupby("category", as_index=False)["price"]
        .sum()
        .rename(columns={"price": "total_spent"})
        .sort_values("total_spent", ascending=False)
    )

    top_item = items.loc[items["price"].idxmax()]
    summary["most_expensive"] = top_item["name"]
    summary["most_expensive_price"] = top_item["price"]
    summary["receipt_total"] = receipt_dict.get("total", items["price"].sum())
    summary["num_items"] = len(items)


    # CHAT QUERY HANDLER
    if query:
        q = query.lower().strip()

        if "expensive" in q or "most expensive" in q:
            return f"💰 The most expensive item is **{top_item['name']}**, priced at {format_number_to_currency(top_item['price'])}."

        elif "total" in q or "spent" in q:
            total = receipt_dict.get("total", items['price'].sum())
            return f"🧾 Your total spending is **{format_number_to_currency(total)}**."

        elif "category" in q or "most" in q:
            top_cat = summary.iloc[0]
            return f"📊 You spent the most on **{top_cat['category']}**, totaling {format_number_to_currency(top_cat['total_spent'])}."

        elif "average" in q:
            avg_price = items['price'].mean()
            return f"📈 The average item price is **{format_number_to_currency(avg_price)}**."

        elif "how many" in q or "count" in q:
            return f"🧮 There are **{len(items)} items** in this receipt."

        else:
            return "🤖 I'm still learning to answer that question, but I can show your spending insights!"

    # Default return (DataFrame)

    return summary


# RECEIPT COMPARATOR

def compare_receipts_ai(receipt_a: dict, receipt_b: dict) -> pd.DataFrame:
    """
    Compare two receipts and highlight price differences per item.
    """
    df_a = pd.DataFrame(receipt_a.get("items", []))
    df_b = pd.DataFrame(receipt_b.get("items", []))

    if df_a.empty or df_b.empty:
        return pd.DataFrame([{"message": "❌ One or both receipts are empty"}])

    # Normalize names
    df_a["name"] = df_a["name"].str.lower().str.strip()
    df_b["name"] = df_b["name"].str.lower().str.strip()

    # Merge
    merged = pd.merge(df_a, df_b, on="name", how="outer", suffixes=("_old", "_new"))

    # Calculate diff
    merged["price_old"] = merged["price_old"].fillna(0)
    merged["price_new"] = merged["price_new"].fillna(0)
    merged["price_diff"] = merged["price_new"] - merged["price_old"]
    merged["status"] = merged["price_diff"].apply(
        lambda x: "⬆️ Increased" if x > 0 else ("⬇️ Decreased" if x < 0 else "➡️ Same")
    )

    return merged[["name", "price_old", "price_new", "price_diff", "status"]].sort_values(
        "price_diff", ascending=False
    )