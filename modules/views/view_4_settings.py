import os
import streamlit as st
from dotenv import load_dotenv, set_key
from babel.numbers import get_currency_name

from modules.data import session_data
from modules.models.loader import ModelNames
from modules.utils import CURRENCY_LIST

# Load environment variables
load_dotenv()

def controller():
    """Main controller for Settings view (secure API handling)."""

    st.header("⚙️ Settings")
    st.caption("Configure your currency, AI model, and API keys securely.")
    st.markdown("---")

    # Currency Selection

    st.subheader("💱 Currency")

    currencies = list(CURRENCY_LIST.keys())
    current_currency = session_data.currency.get()
    current_idx = currencies.index(current_currency) if current_currency in currencies else 0

    selected_currency = st.selectbox(
        "Choose your preferred currency",
        currencies,
        format_func=lambda x: f"{x} — {get_currency_name(x)}",
        index=current_idx,
    )

    # AI Model Selection

    st.subheader("🧠 AI Model")

    model_options = list(ModelNames)
    current_model = session_data.model_name.get()
    model_choice = st.radio(
        "Select AI model for reading receipts:",
        model_options,
        format_func=lambda x: f"{x.value}",
        index=model_options.index(current_model)
        if current_model in model_options
        else 0,
        horizontal=True
    )

    # Secure API Key Handling (Hidden)

    if model_choice == ModelNames.GEMINI:
        st.subheader("🔐 Google API Key (Secure Storage)")
        st.caption("For privacy, your saved key will never be displayed. You can replace it anytime.")

        key_is_set = bool(os.getenv("GOOGLE_API_KEY"))
        if key_is_set:
            st.info("✅ API key already configured securely in your environment.")
        else:
            st.warning("⚠️ No API key detected — please enter your Google API key below.")

        new_key = st.text_input(
            "Enter new Google API Key (optional)",
            type="password",
            placeholder="••••••••••••••••••••••••••••••"
        )
    else:
        new_key = ""

    # Apply Settings

    st.markdown("---")
    if st.button("Apply Settings", use_container_width=True, type="primary"):
        # Update session data
        session_data.currency.set(selected_currency)
        if model_choice != session_data.model_name.get():
            session_data.model.reset()
        session_data.model_name.set(model_choice)

        # Store new API key securely
        if new_key.strip():
            set_key(".env", "GOOGLE_API_KEY", new_key.strip())
            os.environ["GOOGLE_API_KEY"] = new_key.strip()
            st.success("Google API Key securely saved to .env file.")
        elif model_choice == ModelNames.GEMINI and not key_is_set:
            st.error("❌ Gemini model requires a valid API key.")
            return

        st.success(f"Settings applied successfully! Using **{model_choice.value}** model.")
        st.balloons()

    # Current Settings Summary

    st.markdown("---")
    st.subheader("Current Settings Summary")

    st.write(f"**Currency:** {selected_currency} ({get_currency_name(selected_currency)})")
    st.write(f"**AI Model:** {model_choice.value}")

    if model_choice == ModelNames.GEMINI:
        if os.getenv("GOOGLE_API_KEY"):
            st.caption("🔐 Google API Key: **Configured (hidden for security)**")
        else:
            st.caption("⚠️ No API key detected — Gemini may not work properly.")