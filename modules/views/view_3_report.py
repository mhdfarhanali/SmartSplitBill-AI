import streamlit as st
import pandas as pd
from modules.utils import format_currency
from modules.data import session_data


def controller():
    """Main controller for the final report view."""

    st.header("📊 Final Bill Report")
    st.caption("Review each participant’s contribution and final total.")
    st.markdown("---")

    # Validasi Data Session

    if not st.session_state.get("split_confirmed", False):
        st.warning("⚠️ Please complete 'Assign Participants' before viewing the report.")
        return

    receipt = st.session_state.get("uploaded_receipt", None)
    manager = session_data.split_manager.get()

    if not receipt or not manager:
        st.error("❌ Missing data. Please start from the upload page again.")
        return

    # Generate Report Data

    report_data = []

    for pid, participant in manager.participants.items():
        assigned_items = manager.get_assignments(pid)

        # Hitung subtotal per orang
        subtotal = sum(a.total_price for a in assigned_items)
        proportion = subtotal / receipt.subtotal if receipt.subtotal > 0 else 0
        total = round(proportion * receipt.total, 2)

        report_data.append({
            "Participant": participant.name,
            "Subtotal": subtotal,
            "Total": total,
        })

    df = pd.DataFrame(report_data)
    if not df.empty:
        df["Subtotal"] = df["Subtotal"].apply(format_currency)
        df["Total"] = df["Total"].apply(format_currency)

    # Display Report

    st.success("Split completed successfully! Here's the breakdown:")

    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        column_config={
            "Participant": "👤 Participant",
            "Subtotal": "🧾 Subtotal",
            "Total": "💰 Final Total"
        },
    )

    # Total Summary

    st.markdown("---")
    st.subheader("📈 Summary")

    st.markdown(f"**Subtotal (Items):** {format_currency(receipt.subtotal)}")
    st.markdown(f"**Grand Total (with tax/services):** {format_currency(receipt.total)}")

    if round(receipt.subtotal, 2) != round(receipt.total, 2):
        diff = round(receipt.total - receipt.subtotal, 2)
        st.caption(f"*(Includes additional charges of {format_currency(diff)})*")