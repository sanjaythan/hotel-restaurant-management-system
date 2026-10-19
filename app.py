import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
import altair as alt
from datetime import date, timedelta
from decimal import Decimal

st.set_page_config(
    page_title="Haven | Hotel & Restaurant Management",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Theme part
FOREST = "#1f4a3d"
MINT = "#d9eee5"
ACCENT = "#b4d9c9"
GOLD = "#d9a441"
CORAL = "#d9765b"

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{
  --ink:#16211e; --muted:#6f7c77; --line:#e5e9e3; --paper:#f6f7f3; --card:#ffffff;
  --forest:#1f4a3d; --forest-dark:#153a2f; --mint:#d9eee5; --accent:#b4d9c9;
  --gold:#d9a441; --coral:#d9765b; --radius:16px;
}
html, body, [class*="css"]{ font-family:'DM Sans',sans-serif; }
.stApp{ background:var(--paper); color:var(--ink); }
[data-testid="stHeader"]{ background:rgba(246,247,243,.85); backdrop-filter:blur(8px); }
.block-container{ max-width:1500px; padding-top:1.4rem; padding-bottom:3rem; }
#MainMenu, footer{ visibility:hidden; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"]{ background:linear-gradient(180deg,#14302a 0%,#183b33 100%); border-right:1px solid rgba(255,255,255,.06); }
[data-testid="stSidebar"] *{ color:#eef4f0; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{ color:#9fb5ad !important; }
[data-testid="stSidebar"] hr{ border-color:rgba(255,255,255,.1); }
[data-testid="stSidebar"] [data-testid="stRadio"] > label{ display:none; }
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]{ gap:.25rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label{
  border:1px solid transparent; border-radius:12px; padding:.62rem .8rem; width:100%;
  transition:all .15s ease; cursor:pointer;
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label > div:first-child{ display:none; }
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover{ background:rgba(255,255,255,.07); transform:translateX(2px); }
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked){
  background:linear-gradient(90deg,#2e5a4d,#27503f); border-color:#4a7a6a; box-shadow:0 4px 14px rgba(0,0,0,.18);
}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p{ font-size:.92rem; font-weight:500; }
.brand-lockup{ display:flex; align-items:center; gap:12px; padding:.3rem 0 .5rem; }
.brand-mark{ display:grid; place-items:center; width:44px; height:44px; border-radius:14px;
  background:linear-gradient(135deg,#d9eee5,#a9d4c1); color:#183d35; font-size:1.35rem; box-shadow:0 6px 16px rgba(0,0,0,.2); }
.brand-name{ font-family:'Manrope',sans-serif; font-size:1.4rem; font-weight:800; letter-spacing:-.8px; color:#fff; line-height:1.1; }
.brand-sub{ font-size:.62rem; color:#9fb5ad; letter-spacing:1.5px; text-transform:uppercase; margin-top:4px; }
.side-label{ font-size:.66rem; letter-spacing:1.5px; color:#9fb5ad; font-weight:700; margin:.2rem 0 .4rem; }

/* ---------- Hero / page header ---------- */
.hero{ background:linear-gradient(115deg,#143a31 0%,#235a4a 60%,#3b7f68 100%); padding:1.9rem 2.1rem; border-radius:22px;
  color:#fff; margin-bottom:1.4rem; box-shadow:0 14px 34px rgba(24,61,53,.14); position:relative; overflow:hidden; }
.hero:after{ content:''; position:absolute; width:260px; height:260px; right:-60px; top:-110px; border:1px solid rgba(255,255,255,.14);
  border-radius:50%; box-shadow:0 0 0 30px rgba(255,255,255,.035),0 0 0 62px rgba(255,255,255,.025); }
.hero .eyebrow{ text-transform:uppercase; letter-spacing:2px; font-size:.68rem; font-weight:700; color:#c0e5d5; margin-bottom:.6rem; }
.hero h1{ font-family:'Manrope',sans-serif; font-size:clamp(1.6rem,3vw,2.3rem); line-height:1.15; margin:0 0 .45rem; color:#fff; letter-spacing:-1.1px; }
.hero p{ color:#d9e9e1; margin:0; font-size:.96rem; max-width:640px; line-height:1.6; }
.hero .chips{ display:flex; gap:.5rem; margin-top:1rem; flex-wrap:wrap; }
.chip{ background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.18); padding:.3rem .75rem; border-radius:999px; font-size:.78rem; color:#eaf5ef; }
.page-head{ margin-bottom:1.2rem; padding-bottom:.9rem; border-bottom:1px solid var(--line); }
.page-head .eyebrow{ text-transform:uppercase; letter-spacing:1.8px; font-size:.66rem; font-weight:700; color:#5f8f7e; margin-bottom:.25rem; }
.page-head h1{ font-family:'Manrope',sans-serif; font-size:1.85rem; margin:0; color:#17332b; letter-spacing:-1px; font-weight:800; }
.page-head p{ color:var(--muted); margin:.25rem 0 0; font-size:.94rem; }

h1,h2,h3{ font-family:'Manrope',sans-serif; color:#203b34; letter-spacing:-.5px; }
h3{ font-size:1.15rem !important; font-weight:700; }
.section-title{ font-family:'Manrope',sans-serif; font-weight:700; font-size:1.05rem; color:#203b34; margin:1.4rem 0 .6rem; display:flex; align-items:center; gap:.5rem; }
.section-title:before{ content:''; width:4px; height:18px; background:var(--forest); border-radius:4px; display:inline-block; }

/* ---------- KPI cards ---------- */
.kpi{ background:var(--card); border:1px solid var(--line); border-radius:var(--radius); padding:1.1rem 1.2rem; box-shadow:0 3px 14px rgba(23,47,43,.04);
  transition:transform .18s ease, box-shadow .18s ease; height:100%; position:relative; overflow:hidden; }
.kpi:hover{ transform:translateY(-3px); box-shadow:0 12px 26px rgba(23,47,43,.09); }
.kpi:before{ content:''; position:absolute; left:0; top:0; bottom:0; width:4px; background:var(--tone,#1f4a3d); }
.kpi-top{ display:flex; justify-content:space-between; align-items:center; }
.kpi-label{ color:#6f7c77; font-size:.8rem; font-weight:600; letter-spacing:.2px; }
.kpi-icon{ width:34px; height:34px; border-radius:10px; display:grid; place-items:center; font-size:1.05rem; background:var(--tint,#d9eee5); }
.kpi-value{ font-family:'Manrope',sans-serif; font-weight:800; font-size:1.75rem; color:#17332b; letter-spacing:-1px; margin:.45rem 0 .1rem; }
.kpi-sub{ font-size:.78rem; color:#85918c; }

/* ---------- Panels ---------- */
.panel{ background:#fff; border:1px solid var(--line); border-radius:var(--radius); padding:1rem 1.2rem; box-shadow:0 3px 14px rgba(23,47,43,.03); }
.panel-title{ font-family:'Manrope',sans-serif; font-weight:700; color:#203b34; font-size:.98rem; margin-bottom:.2rem; }
.panel-sub{ color:#85918c; font-size:.8rem; margin-bottom:.4rem; }
.activity{ display:flex; align-items:center; gap:.75rem; padding:.6rem 0; border-bottom:1px dashed #e8ece6; }
.activity:last-child{ border-bottom:none; }
.avatar{ width:34px; height:34px; border-radius:50%; background:var(--mint); color:#1f4a3d; display:grid; place-items:center; font-weight:700; font-size:.85rem; flex:none; }
.act-main{ font-weight:600; font-size:.9rem; color:#1d3a32; }
.act-sub{ font-size:.77rem; color:#8a958f; }
.pill{ margin-left:auto; padding:.15rem .6rem; border-radius:999px; font-size:.72rem; font-weight:700; }
.pill.in{ background:#dff3e8; color:#1f6b45; } .pill.out{ background:#fbe9e2; color:#a8492f; }
.empty{ color:#9aa5a0; font-size:.88rem; padding:.8rem 0; text-align:center; }

/* ---------- Native widgets ---------- */
[data-testid="stMetric"]{ background:#fff; border:1px solid var(--line); padding:1rem 1.1rem; border-radius:var(--radius); box-shadow:0 3px 12px rgba(23,47,43,.03); }
[data-testid="stMetricLabel"]{ color:#78837e; font-size:.82rem; font-weight:600; }
[data-testid="stMetricValue"]{ color:#1d4338; font-family:'Manrope',sans-serif; font-weight:800; letter-spacing:-.8px; }
[data-testid="stForm"], [data-testid="stExpander"]{ background:#fff; border:1px solid var(--line); border-radius:var(--radius); padding:.7rem .9rem; box-shadow:0 3px 14px rgba(23,47,43,.025); }
[data-testid="stExpander"] summary{ font-weight:650; }
[data-testid="stDataFrame"]{ border:1px solid var(--line); border-radius:14px; overflow:hidden; background:#fff; box-shadow:0 3px 14px rgba(23,47,43,.025); }

/* ---------- Buttons ---------- */
.stButton > button, [data-testid="stFormSubmitButton"] button{
  border-radius:11px; min-height:2.6rem; padding:.5rem 1.15rem; font-weight:650; font-size:.9rem; letter-spacing:.1px;
  transition:transform .12s ease, box-shadow .16s ease, background .16s ease, border-color .16s ease;
}
/* primary */
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"],
.stButton > button[data-testid="stBaseButton-primary"], [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primaryFormSubmit"]{
  background:linear-gradient(135deg,#2a5f4f,#1f4a3d); color:#fff; border:1px solid #1f4a3d; box-shadow:0 4px 12px rgba(31,74,61,.22);
}
.stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover, [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-primaryFormSubmit"]:hover{
  background:linear-gradient(135deg,#235143,#173a31); transform:translateY(-1px); box-shadow:0 8px 18px rgba(31,74,61,.3); color:#fff;
}
/* secondary */
.stButton > button[kind="secondary"], [data-testid="stFormSubmitButton"] button[kind="secondaryFormSubmit"],
.stButton > button[data-testid="stBaseButton-secondary"], [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-secondaryFormSubmit"]{
  background:#fff; color:#1f4a3d; border:1.5px solid #c9d8d0; box-shadow:none;
}
.stButton > button[kind="secondary"]:hover, [data-testid="stFormSubmitButton"] button[kind="secondaryFormSubmit"]:hover,
.stButton > button[data-testid="stBaseButton-secondary"]:hover, [data-testid="stFormSubmitButton"] button[data-testid="stBaseButton-secondaryFormSubmit"]:hover{
  background:#f1f7f4; border-color:#1f4a3d; color:#153a2f; transform:translateY(-1px);
}
.stButton > button:active, [data-testid="stFormSubmitButton"] button:active{ transform:translateY(0); }
.stButton > button:focus-visible, [data-testid="stFormSubmitButton"] button:focus-visible{ box-shadow:0 0 0 3px rgba(180,217,201,.8); outline:none; }
.stButton > button:disabled, [data-testid="stFormSubmitButton"] button:disabled{ background:#e9ede9; color:#9aa39e; border-color:#e9ede9; box-shadow:none; }
/* destructive: any button whose label starts with a warning sign */
.danger-zone .stButton > button, .danger-zone [data-testid="stFormSubmitButton"] button{ color:#a8492f !important; border-color:#efc9bd !important; background:#fff !important; }
.danger-zone .stButton > button:hover, .danger-zone [data-testid="stFormSubmitButton"] button:hover{ background:#fdf1ed !important; border-color:#d9765b !important; }

/* inputs */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stNumberInput"] input, [data-testid="stDateInput"] input{
  border-radius:10px; border-color:#dde4de; background:#fff; }
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus, [data-testid="stNumberInput"] input:focus{
  border-color:#6d9d89; box-shadow:0 0 0 2px rgba(109,157,137,.25); }
[data-baseweb="select"] > div{ border-radius:10px; border-color:#dde4de; }
[data-testid="stAlert"]{ border-radius:12px; }
[data-testid="stTabs"] button{ font-weight:650; }
hr{ border-color:var(--line); }
.small-note{ color:#77827e; font-size:.86rem; }
@media (max-width:700px){ .hero{ padding:1.25rem; border-radius:17px; } .hero h1{ font-size:1.55rem; } .block-container{ padding-left:1rem; padding-right:1rem; } }
</style>
""",
    unsafe_allow_html=True,
)


# UI part
def page_head(eyebrow, title, subtitle):
    st.markdown(
        f"""<div class="page-head"><div class="eyebrow">{eyebrow}</div>
        <h1>{title}</h1><p>{subtitle}</p></div>""",
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def kpi(col, label, value, sub="", icon="•", tone=FOREST, tint=MINT):
    col.markdown(
        f"""<div class="kpi" style="--tone:{tone};--tint:{tint}">
        <div class="kpi-top"><span class="kpi-label">{label}</span><span class="kpi-icon">{icon}</span></div>
        <div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>""",
        unsafe_allow_html=True,
    )


def money(x):
    return f"₹{float(x or 0):,.2f}"


def show_table(rows, **kwargs):
    """Render a dataframe; works across Streamlit versions."""
    try:
        st.dataframe(rows, width="stretch", hide_index=True, **kwargs)
    except TypeError:
        st.dataframe(rows, use_container_width=True, hide_index=True, **kwargs)


def to_df(rows):
    df = pd.DataFrame(rows)
    for c in df.columns:
        if df[c].map(lambda v: isinstance(v, Decimal)).any():
            df[c] = df[c].astype(float)
    return df


def chart_theme(chart):
    return (
        chart.configure_view(strokeWidth=0)
        .configure_axis(labelColor="#6f7c77", titleColor="#6f7c77", gridColor="#edf0ec", domainColor="#dfe5df")
        .configure_legend(labelColor="#44524d", titleColor="#44524d")
    )


def initials(name):
    parts = (name or "?").split()
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


# Connecting to cloud database
def get_connection():
    """Connect using Streamlit Cloud Secrets in the [mysql] section.

    Expected Secrets keys: host, port, database, username (or user), password.
    """
    if "mysql" not in st.secrets:
        raise RuntimeError("Missing [mysql] section in Streamlit Cloud → App settings → Secrets.")

    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 4000)),
        database=cfg["database"],
        user=cfg.get("username", cfg.get("user")),
        password=cfg["password"],
        connection_timeout=15,
        ssl_disabled=False,
    )


def fetch_all(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()


def execute(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        result = cur.lastrowid
        cur.close()
        return result
    finally:
        conn.close()


# Creating tables
SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS Guest (
        Guest_ID INT AUTO_INCREMENT PRIMARY KEY,
        Guest_Name VARCHAR(100) NOT NULL,
        Phone VARCHAR(20) NOT NULL UNIQUE,
        Email VARCHAR(100) UNIQUE,
        Address VARCHAR(255)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Room (
        Room_ID INT AUTO_INCREMENT PRIMARY KEY,
        Room_Number VARCHAR(10) NOT NULL UNIQUE,
        Room_Type VARCHAR(50) NOT NULL,
        Price_Per_Night DECIMAL(10,2) NOT NULL,
        Status VARCHAR(20) NOT NULL DEFAULT 'Available'
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Reservation (
        Reservation_ID INT AUTO_INCREMENT PRIMARY KEY,
        Guest_ID INT NOT NULL,
        Room_ID INT NOT NULL,
        Check_In_Date DATE NOT NULL,
        Check_Out_Date DATE NOT NULL,
        Number_of_Guests INT NOT NULL DEFAULT 1,
        Reservation_Status VARCHAR(20) NOT NULL DEFAULT 'Confirmed',
        FOREIGN KEY (Guest_ID) REFERENCES Guest(Guest_ID),
        FOREIGN KEY (Room_ID) REFERENCES Room(Room_ID)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Restaurant (
        Restaurant_ID INT AUTO_INCREMENT PRIMARY KEY,
        Restaurant_Name VARCHAR(100) NOT NULL,
        Location VARCHAR(100)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Menu_Item (
        Menu_Item_ID INT AUTO_INCREMENT PRIMARY KEY,
        Restaurant_ID INT NOT NULL,
        Item_Name VARCHAR(100) NOT NULL,
        Category VARCHAR(50),
        Price DECIMAL(10,2) NOT NULL,
        Availability VARCHAR(20) DEFAULT 'Available',
        FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS `Food_Order` (
        Order_ID INT AUTO_INCREMENT PRIMARY KEY,
        Guest_ID INT NOT NULL,
        Restaurant_ID INT NOT NULL,
        Order_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
        Order_Status VARCHAR(30) DEFAULT 'Placed',
        FOREIGN KEY (Guest_ID) REFERENCES Guest(Guest_ID),
        FOREIGN KEY (Restaurant_ID) REFERENCES Restaurant(Restaurant_ID)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Order_Item (
        Order_Item_ID INT AUTO_INCREMENT PRIMARY KEY,
        Order_ID INT NOT NULL,
        Menu_Item_ID INT NOT NULL,
        Quantity INT NOT NULL,
        Unit_Price DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (Order_ID) REFERENCES `Food_Order`(Order_ID),
        FOREIGN KEY (Menu_Item_ID) REFERENCES Menu_Item(Menu_Item_ID)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Payment (
        Payment_ID INT AUTO_INCREMENT PRIMARY KEY,
        Guest_ID INT NOT NULL,
        Reservation_ID INT NULL,
        Amount DECIMAL(10,2) NOT NULL,
        Payment_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
        Payment_Method VARCHAR(30) DEFAULT 'Cash',
        Payment_Status VARCHAR(30) DEFAULT 'Paid',
        FOREIGN KEY (Guest_ID) REFERENCES Guest(Guest_ID),
        FOREIGN KEY (Reservation_ID) REFERENCES Reservation(Reservation_ID)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Staff (
        Staff_ID INT AUTO_INCREMENT PRIMARY KEY,
        Staff_Name VARCHAR(100) NOT NULL,
        Role VARCHAR(50) NOT NULL,
        Phone VARCHAR(20),
        Salary DECIMAL(10,2)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Service_Request (
        Request_ID INT AUTO_INCREMENT PRIMARY KEY,
        Guest_ID INT NOT NULL,
        Staff_ID INT NULL,
        Request_Type VARCHAR(100) NOT NULL,
        Request_Description VARCHAR(255),
        Request_Status VARCHAR(30) DEFAULT 'Pending',
        Request_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (Guest_ID) REFERENCES Guest(Guest_ID),
        FOREIGN KEY (Staff_ID) REFERENCES Staff(Staff_ID)
    )
    """,
    """
    CREATE OR REPLACE VIEW View_Active_Billing_Summary AS
    SELECT
        g.Guest_ID,
        g.Guest_Name,
        COALESCE(SUM(p.Amount), 0) AS Total_Paid
    FROM Guest g
    LEFT JOIN Payment p
        ON g.Guest_ID = p.Guest_ID
        AND p.Payment_Status = 'Paid'
    GROUP BY g.Guest_ID, g.Guest_Name
    """,
]


@st.cache_resource(show_spinner="Connecting to your database…")
def initialize_database():
    """Runs once per server process instead of on every rerun."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        for statement in SCHEMA:
            cur.execute(statement)
        conn.commit()
        cur.close()
    finally:
        conn.close()
    return True


# Sidebar and starting page
with st.sidebar:
    st.markdown(
        """
    <div class="brand-lockup">
      <div class="brand-mark">✦</div>
      <div><div class="brand-name">SMHR</div><div class="brand-sub">Hospitality suites and restaurant</div></div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown('<div class="side-label">PROJECT TEAM</div>', unsafe_allow_html=True)
    st.markdown("Sanjay Thandeeswaran · 25BCE2759")
    st.markdown("Monish Kumar T O · 25BCE2819")

try:
    initialize_database()
except Exception as e:
    st.error("Unable to connect to or initialize your cloud database.")
    st.write("Check your host, database name, username, password and database permissions.")
    st.code(str(e))
    st.stop()

with st.sidebar:
    st.markdown('<div class="side-label">WORKSPACE</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        [
            "📊 Dashboard",
            "👥 Guest Management",
            "🛏️ Room Management",
            "📅 Reservations",
            "🍽️ Restaurant & Menu",
            "🧾 Food Orders",
            "💳 Payments",
            "🧰 Staff & Service Requests",
            "📈 SQL Analytics & Views",
            "⚙️ Test Database Connection",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    

page = page.split(" ", 1)[1] if " " in page else page


# Dashboard creation
if page == "Dashboard":
    today = date.today()
    st.markdown(
        f"""
    <div class="hero">
      <div class="eyebrow">{today.strftime('%A, %d %B %Y')}</div>
      <h1>Every stay, thoughtfully managed.</h1>
      <p>One calm, connected workspace for guest experiences, room reservations, dining, payments and service operations.</p>
      <div class="chips"><span class="chip">🏨 Rooms</span><span class="chip">🍽️ Dining</span>
      <span class="chip">💳 Billing</span><span class="chip">🧰 Service</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    try:
        one = lambda q, p=(): fetch_all(q, p)[0]["n"]
        guests_n = one("SELECT COUNT(*) AS n FROM Guest")
        rooms_n = one("SELECT COUNT(*) AS n FROM Room")
        avail_n = one("SELECT COUNT(*) AS n FROM Room WHERE Status='Available'")
        confirmed_n = one("SELECT COUNT(*) AS n FROM Reservation WHERE Reservation_Status='Confirmed'")
        in_house_n = one(
            "SELECT COUNT(*) AS n FROM Reservation WHERE Reservation_Status='Confirmed' "
            "AND Check_In_Date <= %s AND Check_Out_Date > %s", (today, today))
        revenue = one("SELECT COALESCE(SUM(Amount),0) AS n FROM Payment WHERE Payment_Status='Paid'")
        pending_pay = one("SELECT COALESCE(SUM(Amount),0) AS n FROM Payment WHERE Payment_Status='Pending'")
        food_rev = one("SELECT COALESCE(SUM(Quantity*Unit_Price),0) AS n FROM Order_Item")
        open_req = one("SELECT COUNT(*) AS n FROM Service_Request WHERE Request_Status IN ('Pending','In Progress')")
        occ_pct = (in_house_n / rooms_n * 100) if rooms_n else 0

        r1 = st.columns(4)
        kpi(r1[0], "Total guests", f"{guests_n:,}", "Registered profiles", "👥", FOREST, MINT)
        kpi(r1[1], "Occupancy today", f"{occ_pct:.0f}%", f"{in_house_n} of {rooms_n} rooms in-house", "🛏️", "#3b7f68", "#dcefe6")
        kpi(r1[2], "Payments received", money(revenue), f"{money(pending_pay)} pending", "💳", GOLD, "#f8ecd0")
        kpi(r1[3], "Open requests", f"{open_req}", "Pending or in progress", "🧰", CORAL, "#fae3db")
        st.write("")
        r2 = st.columns(4)
        kpi(r2[0], "Rooms available", f"{avail_n}", f"{rooms_n} rooms total", "🔑", "#3b7f68", "#dcefe6")
        kpi(r2[1], "Confirmed bookings", f"{confirmed_n}", "Upcoming and active", "📅", FOREST, MINT)
        kpi(r2[2], "Dining sales", money(food_rev), "All restaurant orders", "🍽️", GOLD, "#f8ecd0")
        kpi(r2[3], "Avg. room rate", money(one("SELECT COALESCE(AVG(Price_Per_Night),0) AS n FROM Room")), "Per night", "🏷️", "#6f7c77", "#e8ecea")

        # charts
        section("Performance")
        c1, c2 = st.columns([3, 2])

        with c1:
            st.markdown('<div class="panel"><div class="panel-title">Revenue trend</div>'
                        '<div class="panel-sub">Paid amounts per day, last 30 days</div></div>', unsafe_allow_html=True)
            trend = fetch_all(
                "SELECT DATE(Payment_Date) AS Day, SUM(Amount) AS Revenue FROM Payment "
                "WHERE Payment_Status='Paid' AND Payment_Date >= %s GROUP BY DATE(Payment_Date) ORDER BY Day",
                (today - timedelta(days=30),))
            if trend:
                df = to_df(trend)
                df["Day"] = pd.to_datetime(df["Day"])
                base = alt.Chart(df).encode(
                    x=alt.X("Day:T", title=None),
                    y=alt.Y("Revenue:Q", title=None),
                    tooltip=[alt.Tooltip("Day:T"), alt.Tooltip("Revenue:Q", format=",.2f")])
                chart = base.mark_area(
                    line={"color": FOREST, "strokeWidth": 2.5},
                    color=alt.Gradient(gradient="linear", stops=[
                        alt.GradientStop(color="#b4d9c9", offset=0), alt.GradientStop(color="#ffffff", offset=1)],
                        x1=1, x2=1, y1=1, y2=0), interpolate="monotone") + base.mark_circle(color=FOREST, size=55)
                st.altair_chart(chart_theme(chart.properties(height=260)), use_container_width=True)
            else:
                st.markdown('<div class="empty">No paid payments in the last 30 days yet.</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="panel"><div class="panel-title">Room status</div>'
                        '<div class="panel-sub">Current inventory split</div></div>', unsafe_allow_html=True)
            rs = fetch_all("SELECT Status, COUNT(*) AS Rooms FROM Room GROUP BY Status")
            if rs:
                df = to_df(rs)
                chart = alt.Chart(df).mark_arc(innerRadius=62, outerRadius=105, cornerRadius=4).encode(
                    theta="Rooms:Q",
                    color=alt.Color("Status:N", scale=alt.Scale(
                        domain=["Available", "Occupied", "Maintenance"], range=[FOREST, GOLD, CORAL]),
                        legend=alt.Legend(orient="bottom", title=None)),
                    tooltip=["Status", "Rooms"])
                st.altair_chart(chart_theme(chart.properties(height=260)), use_container_width=True)
            else:
                st.markdown('<div class="empty">Add rooms to see availability.</div>', unsafe_allow_html=True)

        c3, c4, c5 = st.columns(3)
        with c3:
            st.markdown('<div class="panel"><div class="panel-title">Payments by method</div>'
                        '<div class="panel-sub">Paid transactions</div></div>', unsafe_allow_html=True)
            pm = fetch_all("SELECT Payment_Method AS Method, SUM(Amount) AS Total FROM Payment "
                           "WHERE Payment_Status='Paid' GROUP BY Payment_Method ORDER BY Total DESC")
            if pm:
                chart = alt.Chart(to_df(pm)).mark_bar(cornerRadiusEnd=6, color=FOREST, size=22).encode(
                    y=alt.Y("Method:N", sort="-x", title=None), x=alt.X("Total:Q", title=None),
                    tooltip=["Method", alt.Tooltip("Total:Q", format=",.2f")])
                st.altair_chart(chart_theme(chart.properties(height=230)), use_container_width=True)
            else:
                st.markdown('<div class="empty">No payment data yet.</div>', unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="panel"><div class="panel-title">Restaurant revenue</div>'
                        '<div class="panel-sub">Sales per venue</div></div>', unsafe_allow_html=True)
            rr = fetch_all("""
                SELECT r.Restaurant_Name AS Restaurant, COALESCE(SUM(oi.Quantity*oi.Unit_Price),0) AS Revenue
                FROM Restaurant r
                LEFT JOIN `Food_Order` fo ON fo.Restaurant_ID=r.Restaurant_ID
                LEFT JOIN Order_Item oi ON oi.Order_ID=fo.Order_ID
                GROUP BY r.Restaurant_ID, r.Restaurant_Name ORDER BY Revenue DESC""")
            if rr:
                chart = alt.Chart(to_df(rr)).mark_bar(cornerRadiusEnd=6, color="#3b7f68", size=22).encode(
                    y=alt.Y("Restaurant:N", sort="-x", title=None), x=alt.X("Revenue:Q", title=None),
                    tooltip=["Restaurant", alt.Tooltip("Revenue:Q", format=",.2f")])
                st.altair_chart(chart_theme(chart.properties(height=230)), use_container_width=True)
            else:
                st.markdown('<div class="empty">Add a restaurant to see sales.</div>', unsafe_allow_html=True)

        with c5:
            st.markdown('<div class="panel"><div class="panel-title">Service requests</div>'
                        '<div class="panel-sub">By status</div></div>', unsafe_allow_html=True)
            sq = fetch_all("SELECT Request_Status AS Status, COUNT(*) AS Requests FROM Service_Request GROUP BY Request_Status")
            if sq:
                chart = alt.Chart(to_df(sq)).mark_bar(cornerRadiusEnd=6, size=22).encode(
                    y=alt.Y("Status:N", sort="-x", title=None), x=alt.X("Requests:Q", title=None),
                    color=alt.Color("Status:N", legend=None, scale=alt.Scale(
                        domain=["Pending", "In Progress", "Completed", "Cancelled"],
                        range=[GOLD, "#3b7f68", FOREST, "#aab4af"])),
                    tooltip=["Status", "Requests"])
                st.altair_chart(chart_theme(chart.properties(height=230)), use_container_width=True)
            else:
                st.markdown('<div class="empty">No service requests yet.</div>', unsafe_allow_html=True)

        # stats
        section("Today at the property")
        a1, a2 = st.columns(2)
        movements = fetch_all("""
            SELECT g.Guest_Name, rm.Room_Number, 'Check-in' AS Kind
            FROM Reservation r JOIN Guest g ON g.Guest_ID=r.Guest_ID JOIN Room rm ON rm.Room_ID=r.Room_ID
            WHERE r.Reservation_Status='Confirmed' AND r.Check_In_Date=%s
            UNION ALL
            SELECT g.Guest_Name, rm.Room_Number, 'Check-out' AS Kind
            FROM Reservation r JOIN Guest g ON g.Guest_ID=r.Guest_ID JOIN Room rm ON rm.Room_ID=r.Room_ID
            WHERE r.Reservation_Status='Confirmed' AND r.Check_Out_Date=%s""", (today, today))

        def render_list(items, kind, css):
            rows = [m for m in items if m["Kind"] == kind]
            if not rows:
                return f'<div class="empty">No {kind.lower()}s today.</div>'
            return "".join(
                f'<div class="activity"><div class="avatar">{initials(m["Guest_Name"])}</div>'
                f'<div><div class="act-main">{m["Guest_Name"]}</div><div class="act-sub">Room {m["Room_Number"]}</div></div>'
                f'<span class="pill {css}">{kind}</span></div>' for m in rows)

        with a1:
            st.markdown(f'<div class="panel"><div class="panel-title">Arrivals</div>{render_list(movements, "Check-in", "in")}</div>',
                        unsafe_allow_html=True)
        with a2:
            st.markdown(f'<div class="panel"><div class="panel-title">Departures</div>{render_list(movements, "Check-out", "out")}</div>',
                        unsafe_allow_html=True)

        section("Recent reservations")
        show_table(fetch_all("""
            SELECT r.Reservation_ID, g.Guest_Name, rm.Room_Number,
                   r.Check_In_Date, r.Check_Out_Date, r.Reservation_Status
            FROM Reservation r
            JOIN Guest g ON r.Guest_ID=g.Guest_ID
            JOIN Room rm ON r.Room_ID=rm.Room_ID
            ORDER BY r.Reservation_ID DESC LIMIT 10"""))

    except Exception as e:
        st.error(str(e))



# Guest management part
elif page == "Guest Management":
    page_head("Guests", "Guest management", "Create guest profiles and keep contact details up to date.")

    with st.expander("➕ Add new guest", expanded=False):
        with st.form("add_guest", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Guest name *")
            phone = c2.text_input("Phone *")
            email = c1.text_input("Email")
            address = c2.text_input("Address")
            submitted = st.form_submit_button("Add guest", type="primary")

        if submitted:
            if not name.strip() or not phone.strip():
                st.warning("Guest name and phone are required.")
            else:
                try:
                    execute("INSERT INTO Guest (Guest_Name,Phone,Email,Address) VALUES (%s,%s,%s,%s)",
                            (name.strip(), phone.strip(), email.strip() or None, address.strip() or None))
                    st.success("Guest added successfully!")
                    st.rerun()
                except Error as e:
                    st.error(f"Unable to add guest: {e}")

    section("Guest records")
    search = st.text_input("Search", placeholder="🔍  Search by name, phone or email", label_visibility="collapsed")

    try:
        guests = fetch_all("""
            SELECT * FROM Guest
            WHERE Guest_Name LIKE %s OR Phone LIKE %s OR COALESCE(Email,'') LIKE %s
            ORDER BY Guest_ID DESC""", (f"%{search}%",) * 3)

        st.caption(f"{len(guests)} guest(s)")
        show_table(guests)

        if guests:
            section("Edit or remove a guest")
            guest_map = {f'{g["Guest_ID"]} - {g["Guest_Name"]}': g for g in guests}
            selected = st.selectbox("Select a guest", list(guest_map))
            guest = guest_map[selected]

            with st.form("edit_guest"):
                c1, c2 = st.columns(2)
                new_name = c1.text_input("Name", guest["Guest_Name"])
                new_phone = c2.text_input("Phone", guest["Phone"])
                new_email = c1.text_input("Email", guest["Email"] or "")
                new_address = c2.text_input("Address", guest["Address"] or "")
                update = st.form_submit_button("Save changes", type="primary")

            if update:
                try:
                    execute("UPDATE Guest SET Guest_Name=%s, Phone=%s, Email=%s, Address=%s WHERE Guest_ID=%s",
                            (new_name.strip(), new_phone.strip(), new_email.strip() or None,
                             new_address.strip() or None, guest["Guest_ID"]))
                    st.success("Guest updated.")
                    st.rerun()
                except Error as e:
                    st.error(str(e))

            st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
            confirm = st.checkbox(f"I understand deleting {guest['Guest_Name']} cannot be undone")
            if st.button("🗑️ Delete guest", disabled=not confirm):
                try:
                    execute("DELETE FROM Guest WHERE Guest_ID=%s", (guest["Guest_ID"],))
                    st.success("Guest deleted.")
                    st.rerun()
                except Error as e:
                    st.error("This guest may have related records. " + str(e))
            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(str(e))


#Room management part
elif page == "Room Management":
    page_head("Inventory", "Rooms & inventory", "Manage room types, nightly rates and availability status.")

    try:
        rooms_all = fetch_all("SELECT * FROM Room ORDER BY Room_Number")
        counts = {s: sum(1 for r in rooms_all if r["Status"] == s) for s in ("Available", "Occupied", "Maintenance")}
        m = st.columns(4)
        kpi(m[0], "Total rooms", len(rooms_all), "", "🛏️")
        kpi(m[1], "Available", counts["Available"], "", "✅", "#3b7f68", "#dcefe6")
        kpi(m[2], "Occupied", counts["Occupied"], "", "🔒", GOLD, "#f8ecd0")
        kpi(m[3], "Maintenance", counts["Maintenance"], "", "🛠️", CORAL, "#fae3db")
    except Exception as e:
        rooms_all = []
        st.error(str(e))

    with st.expander("➕ Add new room"):
        with st.form("add_room", clear_on_submit=True):
            c1, c2 = st.columns(2)
            room_no = c1.text_input("Room number")
            room_type = c2.selectbox("Room type", ["Single", "Double", "Deluxe", "Suite", "Family", "Other"])
            price = c1.number_input("Price per night (₹)", min_value=0.01, value=1500.0, step=100.0)
            status = c2.selectbox("Status", ["Available", "Occupied", "Maintenance"])
            add = st.form_submit_button("Add room", type="primary")

        if add:
            if not room_no.strip():
                st.warning("Room number is required.")
            else:
                try:
                    execute("INSERT INTO Room (Room_Number,Room_Type,Price_Per_Night,Status) VALUES (%s,%s,%s,%s)",
                            (room_no.strip(), room_type, price, status))
                    st.success("Room added.")
                    st.rerun()
                except Error as e:
                    st.error(str(e))

    section("Room inventory")
    show_table(rooms_all, column_config={
        "Price_Per_Night": st.column_config.NumberColumn("Price / night", format="₹%.2f")})

    section("Change room status")
    if rooms_all:
        room_map = {f'{r["Room_Number"]} ({r["Status"]})': r for r in rooms_all}
        c1, c2, c3 = st.columns([2, 2, 1])
        choice = c1.selectbox("Room", list(room_map))
        new_status = c2.selectbox("New status", ["Available", "Occupied", "Maintenance"])
        c3.write("")
        c3.write("")
        if c3.button("Update status", type="primary"):
            try:
                execute("UPDATE Room SET Status=%s WHERE Room_ID=%s", (new_status, room_map[choice]["Room_ID"]))
                st.success("Room status updated.")
                st.rerun()
            except Error as e:
                st.error(str(e))


# Reservations part
elif page == "Reservations":
    page_head("Bookings", "Reservations", "Plan guest stays and prevent overlapping room bookings.")

    guests = fetch_all("SELECT Guest_ID, Guest_Name FROM Guest ORDER BY Guest_Name")
    rooms = fetch_all("SELECT Room_ID, Room_Number, Room_Type, Price_Per_Night FROM Room "
                      "WHERE Status='Available' ORDER BY Room_Number")

    if not guests:
        st.info("Add a guest before creating a reservation.")
    elif not rooms:
        st.info("No rooms are currently marked Available.")
    else:
        guest_map = {f'{g["Guest_ID"]} - {g["Guest_Name"]}': g["Guest_ID"] for g in guests}
        room_map = {f'{r["Room_Number"]} - {r["Room_Type"]} (₹{r["Price_Per_Night"]})': r for r in rooms}

        with st.expander("➕ New reservation", expanded=True):
            with st.form("reservation_form"):
                c1, c2 = st.columns(2)
                guest_label = c1.selectbox("Guest", list(guest_map))
                room_label = c2.selectbox("Room", list(room_map))
                checkin = c1.date_input("Check-in", value=date.today())
                checkout = c2.date_input("Check-out", value=date.today() + timedelta(days=1))
                number_guests = c1.number_input("Number of guests", min_value=1, max_value=20, value=1)
                submit = st.form_submit_button("Create reservation", type="primary")

        if submit:
            if checkout <= checkin:
                st.error("Check-out must be after check-in.")
            else:
                room = room_map[room_label]
                overlap = fetch_all("""
                    SELECT COUNT(*) AS n FROM Reservation
                    WHERE Room_ID=%s AND Reservation_Status='Confirmed'
                      AND Check_In_Date < %s AND Check_Out_Date > %s""",
                    (room["Room_ID"], checkout, checkin))[0]["n"]
                if overlap:
                    st.error("That room is already reserved for those dates.")
                else:
                    try:
                        execute("""
                            INSERT INTO Reservation
                            (Guest_ID,Room_ID,Check_In_Date,Check_Out_Date,Number_of_Guests,Reservation_Status)
                            VALUES (%s,%s,%s,%s,%s,'Confirmed')""",
                            (guest_map[guest_label], room["Room_ID"], checkin, checkout, number_guests))
                        nights = (checkout - checkin).days
                        total = Decimal(str(room["Price_Per_Night"])) * nights
                        st.success(f"Reservation created · {nights} night(s) · estimated {money(total)}")
                        st.rerun()
                    except Error as e:
                        st.error(str(e))

    section("Reservation records")
    try:
        show_table(fetch_all("""
            SELECT r.Reservation_ID, g.Guest_Name, rm.Room_Number,
                   r.Check_In_Date, r.Check_Out_Date, r.Number_of_Guests, r.Reservation_Status
            FROM Reservation r
            JOIN Guest g ON r.Guest_ID=g.Guest_ID
            JOIN Room rm ON r.Room_ID=rm.Room_ID
            ORDER BY r.Reservation_ID DESC"""))

        reservation_ids = fetch_all("SELECT Reservation_ID FROM Reservation WHERE Reservation_Status='Confirmed'")
        if reservation_ids:
            section("Cancel a reservation")
            c1, c2 = st.columns([2, 1])
            rid = c1.selectbox("Reservation", [r["Reservation_ID"] for r in reservation_ids],
                               label_visibility="collapsed")
            st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
            if c2.button("Cancel reservation"):
                execute("UPDATE Reservation SET Reservation_Status='Cancelled' WHERE Reservation_ID=%s", (rid,))
                st.success("Reservation cancelled.")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(str(e))



# Restaurant and Menu management part

elif page == "Restaurant & Menu":
    page_head("Dining", "Restaurant & menu", "Manage dining venues and the items available to guests.")

    with st.expander("➕ Add restaurant"):
        with st.form("add_restaurant", clear_on_submit=True):
            c1, c2 = st.columns(2)
            restaurant_name = c1.text_input("Restaurant name")
            location = c2.text_input("Location")
            add_restaurant = st.form_submit_button("Add restaurant", type="primary")
        if add_restaurant:
            if not restaurant_name.strip():
                st.warning("Restaurant name is required.")
            else:
                try:
                    execute("INSERT INTO Restaurant (Restaurant_Name,Location) VALUES (%s,%s)",
                            (restaurant_name.strip(), location.strip() or None))
                    st.success("Restaurant added.")
                    st.rerun()
                except Error as e:
                    st.error(str(e))

    restaurants = fetch_all("SELECT Restaurant_ID, Restaurant_Name FROM Restaurant ORDER BY Restaurant_Name")

    if restaurants:
        restaurant_map = {f'{r["Restaurant_ID"]} - {r["Restaurant_Name"]}': r["Restaurant_ID"] for r in restaurants}

        with st.expander("➕ Add menu item"):
            with st.form("add_menu_item", clear_on_submit=True):
                c1, c2 = st.columns(2)
                restaurant_label = c1.selectbox("Restaurant", list(restaurant_map))
                item_name = c2.text_input("Menu item name")
                category = c1.selectbox("Category", ["Breakfast", "Starter", "Main Course", "Dessert", "Beverage", "Other"])
                item_price = c2.number_input("Price (₹)", min_value=0.01, value=100.0, step=10.0)
                availability = c1.selectbox("Availability", ["Available", "Unavailable"])
                add_item = st.form_submit_button("Add menu item", type="primary")
            if add_item:
                if not item_name.strip():
                    st.warning("Item name is required.")
                else:
                    try:
                        execute("INSERT INTO Menu_Item (Restaurant_ID,Item_Name,Category,Price,Availability) "
                                "VALUES (%s,%s,%s,%s,%s)",
                                (restaurant_map[restaurant_label], item_name.strip(), category, item_price, availability))
                        st.success("Menu item added.")
                        st.rerun()
                    except Error as e:
                        st.error(str(e))

    section("Menu items")
    try:
        show_table(fetch_all("""
            SELECT m.Menu_Item_ID, r.Restaurant_Name, m.Item_Name, m.Category, m.Price, m.Availability
            FROM Menu_Item m JOIN Restaurant r ON r.Restaurant_ID=m.Restaurant_ID
            ORDER BY r.Restaurant_Name, m.Item_Name"""),
            column_config={"Price": st.column_config.NumberColumn("Price", format="₹%.2f")})
    except Exception as e:
        st.error(str(e))



# Food ordering part
elif page == "Food Orders":
    page_head("Dining", "Dining orders", "Create orders and review item subtotals and order history.")

    guests = fetch_all("SELECT Guest_ID, Guest_Name FROM Guest ORDER BY Guest_Name")
    restaurants = fetch_all("SELECT Restaurant_ID, Restaurant_Name FROM Restaurant ORDER BY Restaurant_Name")

    if not guests:
        st.info("Add a guest first.")
    elif not restaurants:
        st.info("Add a restaurant and menu items first.")
    else:
        guest_map = {f'{g["Guest_ID"]} - {g["Guest_Name"]}': g["Guest_ID"] for g in guests}
        restaurant_map = {f'{r["Restaurant_ID"]} - {r["Restaurant_Name"]}': r["Restaurant_ID"] for r in restaurants}

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        guest_label = c1.selectbox("Guest", list(guest_map))
        restaurant_label = c2.selectbox("Restaurant", list(restaurant_map))

        menu = fetch_all("""
            SELECT Menu_Item_ID, Item_Name, Category, Price FROM Menu_Item
            WHERE Restaurant_ID=%s AND Availability='Available' ORDER BY Item_Name""",
            (restaurant_map[restaurant_label],))

        if menu:
            item_map = {f'{m["Item_Name"]} - ₹{m["Price"]}': m for m in menu}
            c3, c4, c5 = st.columns([3, 1, 1])
            item_label = c3.selectbox("Menu item", list(item_map))
            quantity = c4.number_input("Quantity", min_value=1, value=1, step=1)
            item = item_map[item_label]
            subtotal = Decimal(str(item["Price"])) * quantity
            c5.metric("Subtotal", money(subtotal))
            place = st.button("Place food order", type="primary")
            st.markdown("</div>", unsafe_allow_html=True)

            if place:
                conn = None
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("INSERT INTO `Food_Order` (Guest_ID,Restaurant_ID,Order_Status) VALUES (%s,%s,'Placed')",
                                (guest_map[guest_label], restaurant_map[restaurant_label]))
                    order_id = cur.lastrowid
                    cur.execute("INSERT INTO Order_Item (Order_ID,Menu_Item_ID,Quantity,Unit_Price) VALUES (%s,%s,%s,%s)",
                                (order_id, item["Menu_Item_ID"], quantity, item["Price"]))
                    conn.commit()
                    cur.close()
                    st.success(f"Order #{order_id} created. Subtotal: {money(subtotal)}")
                    st.rerun()
                except Exception as e:
                    if conn:
                        conn.rollback()
                    st.error(str(e))
                finally:
                    if conn:
                        conn.close()
        else:
            st.markdown("</div>", unsafe_allow_html=True)
            st.info("No available menu items for this restaurant.")

    section("Order history")
    try:
        show_table(fetch_all("""
            SELECT fo.Order_ID, g.Guest_Name, r.Restaurant_Name, fo.Order_Date, fo.Order_Status,
                   COALESCE(SUM(oi.Quantity*oi.Unit_Price),0) AS Subtotal
            FROM `Food_Order` fo
            JOIN Guest g ON g.Guest_ID=fo.Guest_ID
            JOIN Restaurant r ON r.Restaurant_ID=fo.Restaurant_ID
            LEFT JOIN Order_Item oi ON oi.Order_ID=fo.Order_ID
            GROUP BY fo.Order_ID, g.Guest_Name, r.Restaurant_Name, fo.Order_Date, fo.Order_Status
            ORDER BY fo.Order_ID DESC"""),
            column_config={"Subtotal": st.column_config.NumberColumn("Subtotal", format="₹%.2f")})
    except Exception as e:
        st.error(str(e))



# Payments part
elif page == "Payments":
    page_head("Billing", "Payments & billing", "Record payments and review transaction history.")

    guests = fetch_all("SELECT Guest_ID, Guest_Name FROM Guest ORDER BY Guest_Name")
    reservations = fetch_all("SELECT Reservation_ID, Guest_ID FROM Reservation ORDER BY Reservation_ID DESC")

    try:
        t = fetch_all("""SELECT
            COALESCE(SUM(CASE WHEN Payment_Status='Paid' THEN Amount END),0) AS paid,
            COALESCE(SUM(CASE WHEN Payment_Status='Pending' THEN Amount END),0) AS pending,
            COALESCE(SUM(CASE WHEN Payment_Status='Refunded' THEN Amount END),0) AS refunded,
            COALESCE(SUM(CASE WHEN Payment_Status='Failed' THEN Amount END),0) AS failed
            FROM Payment""")[0]
        m = st.columns(4)
        kpi(m[0], "Paid", money(t["paid"]), "", "✅", "#3b7f68", "#dcefe6")
        kpi(m[1], "Pending", money(t["pending"]), "", "⏳", GOLD, "#f8ecd0")
        kpi(m[2], "Refunded", money(t["refunded"]), "", "↩️", "#6f7c77", "#e8ecea")
        kpi(m[3], "Failed", money(t["failed"]), "", "⚠️", CORAL, "#fae3db")
    except Exception as e:
        st.error(str(e))

    if guests:
        guest_map = {f'{g["Guest_ID"]} - {g["Guest_Name"]}': g["Guest_ID"] for g in guests}
        reservation_map = {"No reservation linked": None}
        for r in reservations:
            reservation_map[f'Reservation #{r["Reservation_ID"]}'] = r["Reservation_ID"]

        with st.expander("➕ Record a payment", expanded=False):
            with st.form("payment_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                guest_label = c1.selectbox("Guest", list(guest_map))
                reservation_label = c2.selectbox("Reservation (optional)", list(reservation_map))
                amount = c1.number_input("Amount (₹)", min_value=0.01, value=100.0, step=50.0)
                method = c2.selectbox("Payment method", ["Cash", "Card", "UPI", "Bank Transfer", "Other"])
                payment_status = c1.selectbox("Payment status", ["Paid", "Pending", "Failed", "Refunded"])
                submit_payment = st.form_submit_button("Record payment", type="primary")

            if submit_payment:
                try:
                    execute("INSERT INTO Payment (Guest_ID,Reservation_ID,Amount,Payment_Method,Payment_Status) "
                            "VALUES (%s,%s,%s,%s,%s)",
                            (guest_map[guest_label], reservation_map[reservation_label], amount, method, payment_status))
                    st.success("Payment recorded.")
                    st.rerun()
                except Error as e:
                    st.error(str(e))
    else:
        st.info("Add a guest before recording a payment.")

    section("Payment history")
    try:
        show_table(fetch_all("""
            SELECT p.Payment_ID, g.Guest_Name, p.Reservation_ID, p.Amount,
                   p.Payment_Date, p.Payment_Method, p.Payment_Status
            FROM Payment p JOIN Guest g ON g.Guest_ID=p.Guest_ID
            ORDER BY p.Payment_ID DESC"""),
            column_config={"Amount": st.column_config.NumberColumn("Amount", format="₹%.2f")})
    except Exception as e:
        st.error(str(e))



# Service and stff part
elif page == "Staff & Service Requests":
    page_head("Operations", "Staff & service", "Coordinate team assignments and guest requests.")

    with st.expander("➕ Add staff member"):
        with st.form("add_staff", clear_on_submit=True):
            c1, c2 = st.columns(2)
            staff_name = c1.text_input("Staff name")
            role = c2.text_input("Role")
            phone = c1.text_input("Staff phone")
            salary = c2.number_input("Salary (₹)", min_value=0.0, value=0.0, step=500.0)
            add_staff = st.form_submit_button("Add staff", type="primary")
        if add_staff:
            if not staff_name.strip() or not role.strip():
                st.warning("Staff name and role are required.")
            else:
                try:
                    execute("INSERT INTO Staff (Staff_Name,Role,Phone,Salary) VALUES (%s,%s,%s,%s)",
                            (staff_name.strip(), role.strip(), phone.strip() or None, salary or None))
                    st.success("Staff member added.")
                    st.rerun()
                except Error as e:
                    st.error(str(e))

    guests = fetch_all("SELECT Guest_ID, Guest_Name FROM Guest ORDER BY Guest_Name")
    staff = fetch_all("SELECT Staff_ID, Staff_Name FROM Staff ORDER BY Staff_Name")

    if guests:
        guest_map = {f'{g["Guest_ID"]} - {g["Guest_Name"]}': g["Guest_ID"] for g in guests}
        staff_map = {"Unassigned": None}
        for s in staff:
            staff_map[f'{s["Staff_ID"]} - {s["Staff_Name"]}'] = s["Staff_ID"]

        with st.expander("➕ Create service request", expanded=False):
            with st.form("request_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                guest_label = c1.selectbox("Guest", list(guest_map))
                staff_label = c2.selectbox("Assign staff", list(staff_map))
                request_type = c1.selectbox("Request type", ["Housekeeping", "Room Service", "Maintenance", "Restaurant", "Other"])
                status = c2.selectbox("Status", ["Pending", "In Progress", "Completed", "Cancelled"])
                description = st.text_area("Description")
                submit_request = st.form_submit_button("Create request", type="primary")

            if submit_request:
                try:
                    execute("INSERT INTO Service_Request (Guest_ID,Staff_ID,Request_Type,Request_Description,Request_Status) "
                            "VALUES (%s,%s,%s,%s,%s)",
                            (guest_map[guest_label], staff_map[staff_label], request_type,
                             description.strip() or None, status))
                    st.success("Service request created.")
                    st.rerun()
                except Error as e:
                    st.error(str(e))
    else:
        st.info("Add a guest first.")

    tab1, tab2 = st.tabs(["🛎️ Service requests", "👔 Staff directory"])
    with tab1:
        try:
            show_table(fetch_all("""
                SELECT sr.Request_ID, g.Guest_Name, s.Staff_Name, sr.Request_Type,
                       sr.Request_Description, sr.Request_Status, sr.Request_Date
                FROM Service_Request sr
                JOIN Guest g ON g.Guest_ID=sr.Guest_ID
                LEFT JOIN Staff s ON s.Staff_ID=sr.Staff_ID
                ORDER BY sr.Request_ID DESC"""))

            reqs = fetch_all("SELECT Request_ID, Request_Type, Request_Status FROM Service_Request "
                             "WHERE Request_Status IN ('Pending','In Progress') ORDER BY Request_ID DESC")
            if reqs:
                section("Update request status")
                req_map = {f'#{r["Request_ID"]} · {r["Request_Type"]} ({r["Request_Status"]})': r["Request_ID"] for r in reqs}
                c1, c2, c3 = st.columns([2, 2, 1])
                req_choice = c1.selectbox("Request", list(req_map))
                new_stat = c2.selectbox("New status", ["In Progress", "Completed", "Cancelled"])
                c3.write("")
                c3.write("")
                if c3.button("Update", type="primary"):
                    execute("UPDATE Service_Request SET Request_Status=%s WHERE Request_ID=%s",
                            (new_stat, req_map[req_choice]))
                    st.success("Request updated.")
                    st.rerun()
        except Exception as e:
            st.error(str(e))
    with tab2:
        try:
            show_table(fetch_all("SELECT Staff_ID, Staff_Name, Role, Phone, Salary FROM Staff ORDER BY Staff_Name"),
                       column_config={"Salary": st.column_config.NumberColumn("Salary", format="₹%.2f")})
        except Exception as e:
            st.error(str(e))


#analytics part
elif page == "SQL Analytics & Views":
    page_head("Insights", "Analytics & reports",
              "Explore operational insights with joins, aggregates, subqueries and views.")

    analytics = {
        "Payments by Guest (JOIN + GROUP BY)": """
            SELECT g.Guest_ID, g.Guest_Name, COALESCE(SUM(p.Amount),0) AS Total_Payments
            FROM Guest g
            LEFT JOIN Payment p ON p.Guest_ID=g.Guest_ID AND p.Payment_Status='Paid'
            GROUP BY g.Guest_ID,g.Guest_Name
            ORDER BY Total_Payments DESC
        """,
        "Menu Category Analysis (GROUP BY + HAVING)": """
            SELECT Category, COUNT(*) AS Item_Count, AVG(Price) AS Average_Price
            FROM Menu_Item
            GROUP BY Category
            HAVING COUNT(*) >= 1
            ORDER BY Item_Count DESC
        """,
        "Food Items by Units Sold": """
            SELECT m.Item_Name, SUM(oi.Quantity) AS Units_Sold, SUM(oi.Quantity*oi.Unit_Price) AS Sales
            FROM Order_Item oi
            JOIN Menu_Item m ON m.Menu_Item_ID=oi.Menu_Item_ID
            GROUP BY m.Menu_Item_ID,m.Item_Name
            ORDER BY Units_Sold DESC
        """,
        "Restaurant Revenue": """
            SELECT r.Restaurant_Name, COALESCE(SUM(oi.Quantity*oi.Unit_Price),0) AS Revenue
            FROM Restaurant r
            LEFT JOIN `Food_Order` fo ON fo.Restaurant_ID=r.Restaurant_ID
            LEFT JOIN Order_Item oi ON oi.Order_ID=fo.Order_ID
            GROUP BY r.Restaurant_ID,r.Restaurant_Name
            ORDER BY Revenue DESC
        """,
        "Rooms Above Average Price (Subquery)": """
            SELECT Room_ID,Room_Number,Room_Type,Price_Per_Night
            FROM Room
            WHERE Price_Per_Night > (SELECT AVG(Price_Per_Night) FROM Room)
            ORDER BY Price_Per_Night DESC
        """,
        "Billing Summary View": """
            SELECT * FROM View_Active_Billing_Summary
            ORDER BY Total_Paid DESC
        """,
        "Reservations with Guest and Room": """
            SELECT r.Reservation_ID,g.Guest_Name,rm.Room_Number,
                   r.Check_In_Date,r.Check_Out_Date,r.Reservation_Status
            FROM Reservation r
            JOIN Guest g ON g.Guest_ID=r.Guest_ID
            JOIN Room rm ON rm.Room_ID=r.Room_ID
            ORDER BY r.Check_In_Date
        """,
    }

    choice = st.selectbox("Choose an SQL query", list(analytics))
    st.code(analytics[choice].strip(), language="sql")

    if st.button("▶ Run selected query", type="primary"):
        try:
            show_table(fetch_all(analytics[choice]))
        except Error as e:
            st.error(str(e))

    st.divider()
    section("Custom SELECT query")
    st.caption("For safety, this tool allows only SELECT or WITH queries.")
    custom_sql = st.text_area("Enter SQL", "SELECT * FROM Guest LIMIT 20", height=120)

    if st.button("▶ Run custom query"):
        cleaned = custom_sql.strip().lower()
        if not (cleaned.startswith("select") or cleaned.startswith("with")):
            st.warning("Only SELECT or WITH queries are allowed.")
        elif ";" in cleaned.rstrip(";"):
            st.warning("Please enter one query at a time.")
        else:
            try:
                show_table(fetch_all(custom_sql))
            except Error as e:
                st.error(str(e))


#creative connectivity part
elif page == "Test Database Connection":
    page_head("System", "Test cases & database connection", "Verify connectivity and review the project test plan.")

    st.markdown(
        """
    | Test | Expected result |
    |---|---|
    | Add guest with valid details | Guest saved |
    | Add duplicate phone number | Error shown |
    | Create valid reservation | Reservation saved |
    | Check-out before check-in | Reservation rejected |
    | Reserve overlapping room dates | Reservation rejected |
    | Place a food order | Order and order item saved |
    | Record payment | Payment appears in history |
    | Run analytics | SQL result displayed |
    """
    )

    section("Test cloud database")
    if st.button("Test connection now", type="primary"):
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT DATABASE(), VERSION()")
            database_name, version = cur.fetchone()
            st.success(f"Connected successfully to database: {database_name}")
            st.write(f"Database server version: {version}")
            cur.close()
        except Exception as e:
            st.error("Connection failed. Check your cloud database settings.")
            st.code(str(e))
        finally:
            if conn is not None and conn.is_connected():
                conn.close()

    section("Subtotal calculator")
    c1, c2, c3 = st.columns(3)
    unit_price = c1.number_input("Unit price", min_value=0.0, value=100.0)
    qty = c2.number_input("Quantity", min_value=1, value=1)
    c3.metric("Subtotal", money(unit_price * qty))


#foot
st.divider()
st.caption("Hotel and Restaurant Management System | Database Systems Project")
