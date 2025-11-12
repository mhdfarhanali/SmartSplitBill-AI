import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

from modules.models.gemini import GeminiModel
from modules.pipeline.insights_engine import compare_receipts_ai


def controller() -> bool:
    """UI controller for the Receipt Comparator."""
    st.title("⚔️ AI Receipt Comparator")
    st.caption("Upload two receipts (images or JSON) to compare their item prices.")
    st.markdown("---")

    # Upload Section

    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("📂 Upload First Receipt", type=["jpg", "jpeg", "png", "json"], key="file1")
    with col2:
        file2 = st.file_uploader("📂 Upload Second Receipt", type=["jpg", "jpeg", "png", "json"], key="file2")

    if not (file1 and file2):
        st.info("Please upload two receipts to start comparison.")
        return False

    # Load or Extract Data

    def read_receipt(file):
        """Auto-detect format (JSON or image)."""
        if file.name.lower().endswith(".json"):
            try:
                return pd.read_json(file).to_dict()
            except Exception as e:
                st.error(f"Failed to read JSON: {e}")
                return None
        else:
            # Process image with AI model
            try:
                st.write("🤖 Analyzing receipt with Gemini AI...")
                model = GeminiModel()
                receipt_obj = model.run(Image.open(file))
                return receipt_obj.to_dict()
            except Exception as e:
                st.error(f"❌ AI failed to read receipt: {e}")
                return None

    receipt1 = read_receipt(file1)
    receipt2 = read_receipt(file2)

    if not receipt1 or not receipt2:
        st.error("❌ Could not process both receipts. Please check your files.")
        return False

    st.success("Both receipts processed successfully!")

    # AI Comparison

    comparison = compare_receipts_ai(receipt1, receipt2)
    if comparison is None or comparison.empty:
        st.warning("⚠️ Nothing to compare or invalid data.")
        return False

    # Display Comparison
  
    st.subheader("💸 Price Comparison Table")
    st.dataframe(comparison, use_container_width=True)

    # Visualization

    if "price_diff" in comparison.columns:
        st.subheader("📊 Price Difference Visualization")

        fig = px.bar(
            comparison,
            x="name",
            y="price_diff",
            color="status",
            color_discrete_map={
                "⬆️ Increased": "#E53935",
                "⬇️ Decreased": "#00C853",
                "➡️ Same": "#BDBDBD",
            },
            title="Item Price Changes Between Receipts",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No significant price differences detected.")

    return False