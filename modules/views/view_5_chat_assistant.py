import streamlit as st
from modules.data import session_data
from modules.pipeline.insights_engine import analyze_receipt_with_ai
from modules.utils import format_currency


def controller():
    """Main controller for Chat Assistant view."""

    st.header("💬 Receipt Chat Assistant")
    st.caption("Ask anything about your receipt — from totals to insights!")
    st.markdown("---")

    # Load Last Uploaded Receipt

    receipt = st.session_state.get("uploaded_receipt", None)
    if not receipt:
        st.warning("⚠️ Please upload and confirm a receipt first on the main page.")
        return

    # Initialize Chat History

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Chat Input Section

    st.subheader("Ask Your Question")
    user_query = st.text_input(
        "Type your question here",
        placeholder="e.g. What’s the most expensive item?",
        key="chat_query",
    )

    if st.button("🔍 Ask", use_container_width=True):
        if not user_query.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Thinking... 🤔"):
                try:
                    # FIX: convert ReceiptData
                    answer = analyze_receipt_with_ai(receipt.to_dict(), user_query)

                    # Save to session chat log
                    st.session_state["chat_history"].append(
                        {"role": "user", "content": user_query}
                    )
                    st.session_state["chat_history"].append(
                        {"role": "assistant", "content": str(answer)}
                    )

                    st.success("Answer generated!")
                except Exception as e:
                    st.error(f"AI failed to respond: {e}")

    # Chat History Display

    if st.session_state["chat_history"]:
        st.markdown("---")
        st.subheader("🗂️ Chat History")

        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.markdown(f"**🧍 You:** {msg['content']}")
            else:
                st.markdown(f"**🤖 AI:** {msg['content']}")
    else:
        st.info("Start chatting with your receipt assistant!")

    # Quick Insights Section

    st.markdown("---")
    st.subheader("✨ Quick Insights")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💸 Most Expensive Item", use_container_width=True):
            show_insight("most_expensive", receipt)
    with col2:
        if st.button("🍽️ Category Summary", use_container_width=True):
            show_insight("category_summary", receipt)
    with col3:
        if st.button("📊 Total Spending", use_container_width=True):
            show_insight("total_summary", receipt)


# Quick Insight Helper


def show_insight(insight_type: str, receipt):
    """Handle Quick Insights button logic."""

    if insight_type == "most_expensive":
        item = receipt.get_most_expensive()
        st.success(f"💎 Most expensive item: **{item.name}** — {format_currency(item.price)}")

    elif insight_type == "category_summary":
        df = receipt.get_category_summary()
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.info("📘 Summary by category (auto-tagged).")

    elif insight_type == "total_summary":
        st.success(
            f"🧾 Subtotal: {format_currency(receipt.subtotal)} | "
            f"Grand Total: {format_currency(receipt.total)}"
        )