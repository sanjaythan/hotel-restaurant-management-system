
import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta
from decimal import Decimal

st.set_page_config(
    page_title="Haven | Hotel & Restaurant Management",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PREMIUM UI THEME — custom CSS for Streamlit
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root { --ink:#172b3a; --muted:#657786; --teal:#0f766e; --teal2:#14b8a6; --sand:#f5f2eb; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(135deg,#f7f8fa 0%,#f4f7f6 100%); color:var(--ink); }
[data-testid="stHeader"] { background:rgba(247,248,250,.85); }
.block-container { padding-top:1.6rem; padding-bottom:2.5rem; max-width:1450px; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#102b3a 0%,#173f4b 100%); }
[data-testid="stSidebar"] * { color:#f4f8f8 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { border-radius:10px; padding:.45rem .65rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:rgba(255,255,255,.10); }
[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,.18); }
.hero { background:linear-gradient(120deg,#102b3a 0%,#17645f 68%,#1b9384 100%); padding:1.7rem 2rem; border-radius:22px; color:white; margin-bottom:1.4rem; box-shadow:0 14px 35px rgba(16,43,58,.15); }
.hero h1 { font-family:'Playfair Display',serif; font-size:2.25rem; margin:0 0 .35rem 0; color:white; letter-spacing:-.4px; }
.hero p { color:#d6e9e7; margin:0; font-size:1rem; }
.eyebrow { text-transform:uppercase; letter-spacing:2px; font-size:.72rem; font-weight:700; color:#a8e4dc; margin-bottom:.6rem; }
.section-kicker { color:#0f766e; text-transform:uppercase; font-size:.72rem; font-weight:700; letter-spacing:1.5px; }
h1,h2,h3 { color:#173747; }
h2 { font-weight:700; letter-spacing:-.4px; }
[data-testid="stMetric"] { background:#fff; border:1px solid #e4ebeb; padding:1rem 1.1rem; border-radius:16px; box-shadow:0 4px 16px rgba(19,51,61,.045); }
[data-testid="stMetricLabel"] { color:#657786; font-weight:600; }
[data-testid="stMetricValue"] { color:#123b45; font-weight:700; }
[data-testid="stForm"], [data-testid="stExpander"] { background:#fff; border:1px solid #e2e9e8; border-radius:16px; padding:.5rem; }
[data-testid="stDataFrame"] { border:1px solid #e0e8e7; border-radius:14px; overflow:hidden; }
.stButton > button, [data-testid="stFormSubmitButton"] button { background:linear-gradient(120deg,#0f766e,#13978a); color:white; border:0; border-radius:10px; padding:.55rem 1rem; font-weight:700; transition:all .2s ease; }
.stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover { background:linear-gradient(120deg,#0b5f59,#0f766e); color:white; border:0; transform:translateY(-1px); box-shadow:0 5px 14px rgba(15,118,110,.2); }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stNumberInput"] input { border-radius:10px; }
[data-baseweb="select"] > div { border-radius:10px; }
[data-testid="stAlert"] { border-radius:12px; }
hr { border-color:#e1e8e7; }
.small-note { color:#71818a; font-size:.86rem; }
@media (max-width: 700px) { .hero { padding:1.2rem; } .hero h1 { font-size:1.65rem; } }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">Hospitality, made seamless</div>
  <h1>Haven · Hotel & Restaurant</h1>
  <p>A unified workspace for guest stays, room bookings, dining, payments and service.</p>
</div>
""", unsafe_allow_html=True)
with st.sidebar:
    st.markdown("# 🏨 HAVEN")
    st.caption("HOTEL & RESTAURANT MANAGEMENT")
    st.divider()
    st.markdown("**PROJECT TEAM**")
    st.caption("Sanjay Thandeeswaran · 25BCE2759")
    st.caption("Monish Kumar T O · 25BCE2819")
    st.divider()
# ============================================================
# 1. CLOUD DATABASE CONNECTION
# ============================================================


def get_connection():
    """Connect using Streamlit Cloud Secrets in the [mysql] section.

    Expected Secrets keys: host, port, database, username (or user), password.
    The hostname is a VALUE under host, never a st.secrets key itself.
    """
    if "mysql" not in st.secrets:
        raise RuntimeError(
            'Missing [mysql] section in Streamlit Cloud → App settings → Secrets.'
        )

    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],                 # TiDB hostname goes here via Secrets
        port=int(cfg.get("port", 4000)), # TiDB Cloud commonly uses 4000
        database=cfg["database"],         # e.g. test
        user=cfg.get("username", cfg.get("user")),
        password=cfg["password"],
        connection_timeout=15,
        ssl_disabled=False
    )

def fetch_all(sql, params=()):
