import os
import pickle
import streamlit as st
import pandas as pd
import plotly.express as px

from modules.data import session_data
from modules.data.receipt_data import ReceiptData, ItemData
from modules.pipeline.insights_engine import analyze_receipt_with_ai
from modules.utils import format_number_to_currency


# Safe Receipt Loader


def load_latest_receipt():
    """
    Load receipt safely from session or fallback JSON/pickle cache.
    Uses dict serialization to prevent PicklingError on Streamlit reload.
    """
    receipt = session_data.uploaded_receipt.get()

    # Save latest receipt to cache as dict
    if receipt:
        os.makedirs("data", exist_ok=True)
        with open("data/temp_receipt.pkl", "wb") as f:
            pickle.dump(receipt.to_dict(), f) 
        return receipt

    # Fallback: load last saved receipt
    if os.path.exists("data/temp_receipt.pkl"):
        try:
            with open("data/temp_receipt.pkl", "rb") as f:
                data = pickle.load(f)

            # Rebuild object only if dict structure is valid
            if isinstance(data, dict) and "items" in data:
                items = {
                    f"item_{i:03d}": ItemData(
                        d.get("name", ""),
                        d.get("price", 0),
                        d.get("category", "Others"),
                    )
                    for i, d in enumerate(data.get("items", []))
                }
                receipt = ReceiptData(items=items, total=data.get("total", 0.0))
                st.session_state["uploaded_receipt"] = receipt
                st.info("📂 Loaded last uploaded receipt from local cache.")
                return receipt
            else:
                st.warning("⚠️ Invalid cache format — please upload again.")
        except Exception as e:
            st.error(f"❌ Failed to load saved receipt: {e}")
            return None

    return None


# Main Analytics View


def show_analytics():
    """Display interactive analytics and AI-generated insights."""
    st.title("📊 History & Spending Analytics")
    st.caption("Visualize your spending breakdown, highlights, and AI insights.")
    st.markdown("---")

    # Load receipt
    receipt = load_latest_receipt()
    if not receipt:
        st.warning("⚠️ Please upload a receipt first.")
        return

    # Run AI-based analysis
    try:
        df_summary = analyze_receipt_with_ai(receipt.to_dict())
    except Exception as e:
        st.error(f"❌ Failed to analyze receipt: {e}")
        return

    if df_summary is None or df_summary.empty:
        st.info("ℹ️ No items found in the current receipt.")
        return

    # Category Breakdown (Pie Chart)

    st.subheader("💡 Category Breakdown")
    try:
        fig = px.pie(
            df_summary,
            names="category",
            values="total_spent",
            title="Expense Breakdown by Category",
            color_discrete_sequence=px.colors.sequential.Greens,
        )
        fig.update_traces(textinfo="percent+label", pull=[0.05] * len(df_summary))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ Could not render pie chart: {e}")

    #  Highlight — Most Expensive Item

    st.subheader("🏆 Highlight")
    try:
        top_item = df_summary.sort_values(
            "most_expensive_price", ascending=False
        ).iloc[0]
        st.success(
            f"**Most Expensive Item:** {top_item['most_expensive']} — "
            f"{format_number_to_currency(top_item['most_expensive_price'])}"
        )
    except Exception:
        st.info("No valid item data available for highlight section.")

    # Detailed Summary Table

    st.subheader("🧾 Detailed Summary")
    df_display = df_summary.copy()
    df_display["total_spent"] = df_display["total_spent"].apply(
        format_number_to_currency
    )
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Total Summary

    st.markdown("---")
    total_spent = df_summary.get("receipt_total", pd.Series([0])).iloc[0]
    st.markdown(f"### 💰 Total Spent: {format_number_to_currency(total_spent)}")

    # AI Insights Summary

    st.markdown("---")
    st.subheader("🤖 AI Insights Summary")

    try:
        major_category = df_summary.loc[
            df_summary["total_spent"].idxmax(), "category"
        ]
        major_percent = (
            df_summary.loc[df_summary["total_spent"].idxmax(), "total_spent"]
            / total_spent
        ) * 100
        st.info(
            f"💡 Your biggest spending category is **{major_category}**, "
            f"accounting for approximately **{major_percent:.1f}%** of total expenses."
        )
    except Exception:
        st.caption("AI summary unavailable — not enough category data.")


# Controller

def controller() -> bool:
    """Controller for the Analytics Page."""
    show_analytics()
    return False