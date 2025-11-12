import streamlit as st
from typing import Any

from modules.models.loader import ModelNames
from modules.data.assignment_data import GroupData, SplitManager


# Helper Class


class SessionDataManager:
    """Generic and safe session state manager for Streamlit."""

    def __init__(self, state_name: str, default: Any = None):
        self.state_name = state_name
        self.default = default

    # ------------------------------
    def get(self) -> Any:
        """Get value from Streamlit session, create default if missing."""
        if self.state_name not in st.session_state:
            st.session_state[self.state_name] = self.default
        return st.session_state[self.state_name]

    # ------------------------------
    def set(self, value: Any) -> None:
        """Set or overwrite session state."""
        st.session_state[self.state_name] = value

    # ------------------------------
    def reset(self) -> None:
        """Reset session value to default."""
        st.session_state[self.state_name] = self.default

    # ------------------------------
    def get_once(self) -> Any:
        """Get once and reset after retrieval."""
        val = self.get()
        self.reset()
        return val


# Session Variables (Global App State)

# Model & App Settings
model_name = SessionDataManager("model_name", ModelNames.GEMINI)
currency = SessionDataManager("currency", "IDR")

# Receipt Upload
uploaded_receipt = SessionDataManager("uploaded_receipt")
receipt_image = SessionDataManager("receipt_image")

# Splitting & Participants
group_data = SessionDataManager("group_data", GroupData(name="Default Group"))
split_manager = SessionDataManager("split_manager", SplitManager([], {}))

# Report
report = SessionDataManager("report")

# Flow Control / UI State
current_page = SessionDataManager("current_page", "upload")
view1_auto_next_page = SessionDataManager("view1_auto_next_page", False)


# Helper Functions

def reset_all() -> None:
    """Reset all user session states (for restart)."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def reset_receipt_data() -> None:
    """Reset data when user uploads a new receipt."""
    uploaded_receipt.reset()
    split_manager.reset()
    report.reset()
    group_data.reset()