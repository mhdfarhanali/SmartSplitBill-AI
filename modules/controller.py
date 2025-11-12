import streamlit as st

# Import semua view page
from modules.views import (
    view_1_receipt_upload,
    view_2_assign_participants,
    view_3_report,
    view_4_settings,
    view_5_chat_assistant,
    view_6_history_analytics,
    view_7_comparator,
)

# Daftar Halaman

PAGES = {
    "📤 Upload Receipt": view_1_receipt_upload,
    "👥 Assign Participants": view_2_assign_participants,
    "📊 Report": view_3_report,
    "💬 Chat Assistant": view_5_chat_assistant,
    "📈 History & Analytics": view_6_history_analytics,
    "🧾 Receipt Comparator": view_7_comparator,
    "⚙️ Settings": view_4_settings,
}

# Fungsi Tema Hijau Global

def inject_theme():
    """Inject custom CSS hijau elegan ke seluruh halaman."""
    st.markdown("""
        <style>
        :root {
            --primary-color: #228B22;
            --primary-dark: #1d6e1d;
            --bg-light: #f0fff0;
            --text-color: #1a1a1a;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--bg-light);
            border-right: 2px solid #cdeccd;
        }

        /* Tombol umum */
        .stButton>button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
        }

        .stButton>button:hover {
            background-color: var(--primary-dark);
            transform: scale(1.02);
        }

        /* Header warna utama */
        h2, h3, h4, h5 {
            color: var(--primary-color);
            font-weight: 700;
        }

        /* Table customization */
        .stDataFrame {
            border: 1px solid #cdeccd;
            border-radius: 10px;
        }

        /* Scrollbar soft hijau */
        ::-webkit-scrollbar-thumb {
            background-color: #77c577;
            border-radius: 10px;
        }

        /* Remove default Streamlit footer */
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# Fungsi Sidebar

def sidebar_branding():
    """Render branding elegan tanpa gambar aset."""
    st.markdown(
        """
        <div style='text-align:center; padding-top: 0.5rem;'>
            <h2 style='color:#228B22; margin-bottom:0;'>💵 SmartSplitBill AI</h2>
            <p style='color:gray; font-size:0.9rem; margin-top:0;'>
                AI-Powered Receipt Splitting System
            </p>
        </div>
        <hr style='border:1px solid #cdeccd;'>
        """,
        unsafe_allow_html=True
    )

# Fungsi Utama Controller

def controller():
    """Main controller untuk navigasi & routing antar halaman."""

    # Inject tema hijau global
    inject_theme()

    # Sidebar navigasi
    with st.sidebar:
        sidebar_branding()

        # Menu navigasi radio
        selected_page = st.radio(
            "Navigation",
            list(PAGES.keys()),
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("Developed by **Muhammad Farhan Ali**")

    # Tampilkan halaman berdasarkan pilihan user
    current_view = PAGES[selected_page]
    current_view.controller()