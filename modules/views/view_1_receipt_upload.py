import streamlit as st
from PIL import Image
import pickle, os
import pandas as pd

from modules.models.gemini import GeminiModel
from modules.utils import format_currency


def controller():
    """Main controller for Upload & AI Receipt Reader view."""

    # Header Section

    st.header("📤 Upload Receipt")
    st.caption("Upload your receipt image — AI will extract all items automatically, and you can edit them if needed.")
    st.markdown("---")

    # Upload Section

    uploaded_file = st.file_uploader(
        "Upload a receipt image (JPG / PNG):",
        type=["jpg", "jpeg", "png"],
    )

    if not uploaded_file:
        st.info("Please upload your receipt image to begin.")
        return

    # Display Preview

    image = Image.open(uploaded_file)
    st.image(image, caption="🧾 Uploaded Receipt", use_container_width=True)
    st.markdown("---")

    # Run Gemini AI for Extraction

    with st.spinner("🤖 Reading receipt using Gemini AI..."):
        try:
            model = GeminiModel()
            receipt = model.run(image)
        except Exception as e:
            st.error(f"Failed to read receipt: {e}")
            return

    # Display Extracted Result (Editable)

    st.success("Receipt successfully analyzed by AI!")

    df = receipt.to_dataframe().copy()

    st.info("✏️ You can edit the table below if AI misread any items (e.g., wrong name, price, or category).")

    # Editable Table
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "name": st.column_config.TextColumn("Item Name"),
            "price": st.column_config.NumberColumn("Price", format="Rp %d"),
            "category": st.column_config.TextColumn("Category")
        },
        key="editable_receipt_table",
    )

    # Update Edited Data

    if not edited_df.equals(df):
        st.info("💾 You have unsaved edits — click the button below to apply changes.")
        if st.button("💾 Save Edits", type="primary"):
            try:
                # Update ke objek receipt
                receipt.items.clear()
                for _, row in edited_df.iterrows():
                    # pastikan field tetap sinkron
                    receipt.add_item(
                        name=str(row["name"]),
                        price=float(row["price"]),
                        category=str(row["category"])
                    )

                # Recalculate total/subtotal jika ada fungsi internal
                if hasattr(receipt, "recalculate_total"):
                    receipt.recalculate_total()

                # Save ulang ke file cache
                os.makedirs("data", exist_ok=True)
                with open("data/temp_receipt.pkl", "wb") as f:
                    pickle.dump(receipt, f)

                st.success("Edits saved successfully!")
            except Exception as e:
                st.error(f"Failed to apply edits: {e}")

    # Display Totals

    st.markdown("---")
    st.markdown(f"**Subtotal:** {format_currency(receipt.subtotal)}")
    st.markdown(f"**Total:** {format_currency(receipt.total)}")

    # Confirm & Continue

    st.markdown("---")
    col1, col2 = st.columns([4, 2])
    with col1:
        st.info("Verify or edit items above. When done, confirm to proceed.")
    with col2:
        if st.button("Confirm & Continue", use_container_width=True):
            st.session_state["uploaded_receipt"] = receipt
            st.session_state["receipt_uploaded"] = True

            os.makedirs("data", exist_ok=True)
            with open("data/temp_receipt.pkl", "wb") as f:
                pickle.dump(receipt, f)

            st.success("Receipt confirmed and saved! You can now move to 'Assign Participants' page.")