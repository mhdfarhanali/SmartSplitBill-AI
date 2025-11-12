import streamlit as st
from babel.numbers import format_currency

# Custom Exceptions

class SettingsError(Exception):
    """Raised when there is a configuration or API key issue."""
    pass


class AIError(Exception):
    """Raised when an AI model fails to produce or parse output."""
    pass


# Currency Utilities


CURRENCY_LIST = {
    "IDR": "Indonesian Rupiah",
    "USD": "US Dollar",
    "EUR": "Euro",
    "JPY": "Japanese Yen",
    "GBP": "British Pound",
    "SGD": "Singapore Dollar",
    "MYR": "Malaysian Ringgit",
    "THB": "Thai Baht",
}


def format_number_to_currency(value: float, currency: str = "IDR") -> str:
    """Format float number to readable currency string."""
    try:
        return format_currency(value, currency, locale="id_ID")
    except Exception:
        return f"{currency} {value:,.2f}"


def format_currency(value: float, currency: str = "IDR") -> str:
    """Simplified alias for consistency."""
    return format_number_to_currency(value, currency)


# Lazy Import Utilities


def get_current_currency():
    """Safely retrieve currency code from Streamlit session."""
    try:
        from modules.data import session_data
        return session_data.currency.get()
    except Exception:
        return "IDR"


def reset_all_states():
    """Utility to clear session (debug or restart)."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]