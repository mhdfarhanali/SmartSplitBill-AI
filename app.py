import os
import streamlit as st
from dotenv import load_dotenv
from modules.controller import controller

# Load Environment Variables

load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    st.warning("GOOGLE_API_KEY belum ditemukan di file .env")

# Streamlit Page Configuration

st.set_page_config(
    page_title="SmartSplitBill AI 🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global UI Styling

st.markdown("""
    <style>
        /* Warna Tema */
        :root {
            --primary-color: #2E8B57;
            --primary-dark: #246b46;
            --background-light: #F1FFF1;
            --text-color: #1a1a1a;
        }

        /* Body Utama */
        .stApp {
            background-color: var(--background-light);
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #E8F5E9;
            border-right: 2px solid #b6e3b6;
        }

        /* Tombol Utama */
        .stButton>button {
            background-color: var(--primary-color);
            color: white !important;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.5rem 1.1rem;
            transition: all 0.2s ease-in-out;
        }

        /* Tombol Hover */
        .stButton>button:hover {
            background-color: var(--primary-dark);
            transform: scale(1.02);
        }

        /* Header */
        h1, h2, h3, h4, h5 {
            color: var(--primary-color);
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
        }

        /* Divider */
        hr {
            border: 1px solid var(--primary-color);
            width: 60%;
            margin: 1rem auto;
        }

        /* Footer kecil */
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Fungsi Utama Aplikasi

def main():
    """
    Fungsi utama aplikasi Streamlit.
    Menampilkan header dan memanggil controller() utama.
    """

    # Header Aplikasi
    st.markdown(
        """
        <div style='text-align:center; margin-top: -20px;'>
            <h1>💵 SmartSplitBill AI</h1>
            <p style='color: grey; font-size: 1.1rem;'>
                AI-Powered Receipt Splitting & Expense Insights
            </p>
        </div>
        <hr>
        """,
        unsafe_allow_html=True
    )

    # Jalankan controller (routing utama)
    controller()

    # Footer Credit
    st.markdown(
        """
        <div style='text-align:center; margin-top: 2rem; color: grey; font-size: 0.9rem;'>
            Made by <b>Muhammad Farhan Ali</b>
        </div>
        """,
        unsafe_allow_html=True
    )

# Entry Point

if __name__ == "__main__":
    main()