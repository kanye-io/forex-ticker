import streamlit as st
from streamlit_autorefresh import st_autorefresh
import requests
from datetime import datetime
import pytz
import yfinance as yf

# — Must be first —
st.set_page_config(layout="wide", page_title="📈 Market Ticker by KashhKanye")

# — Auto-refresh selection —
interval_ms = st.selectbox("Refresh every:", [1000, 3000, 5000, 8000], format_func=lambda x: f"{x//1000}s")
st_autorefresh(interval=interval_ms, key="ticker_refresh")

# — Courier New styling —
st.markdown("""
<style>
html, body, [class*="css"] { font-family: "Courier New", Courier, monospace !important; }
marquee, h2, h3, h4, span {
  font-family: "Courier New", monospace;
}
</style>""", unsafe_allow_html=True)

# — Header & Theme --}}
st.title("💹 Live FX, Metals & Indices Ticker by KashhKanye")
mode = st.radio("Display mode:", ["Dark Mode", "Light Mode"])
bg, fg = ("black","white") if mode=="Dark Mode" else ("white","black")
timefmt = st.radio("Time format:", ["24-Hour", "12-Hour"])

# — Asset selection —
available = [
    'EURUSD','USDJPY','GBPUSD','AUDUSD','USDCHF','USDCAD','NZDUSD',
    'EURJPY','GBPJPY','AUDJPY','CHFJPY','EURGBP','EURAUD','EURCHF','EURCAD',
    'GBPCAD','AUDCAD','CADJPY','NZDJPY','XAUUSD','XAGUSD',
    'US30USD','SPX500USD','NAS100USD'
]
selected = st.multiselect("Select assets:", available, default=['EURUSD','US30USD'])

# — Market session clocks —
now = datetime.utcnow().replace(tzinfo=pytz.utc)
zones = [("New York","America/New_York"),("London","Europe/London"),("Tokyo","Asia/Tokyo")]
st.markdown("### ⏰ Market Sessions")
for city, tz in zones:
    loc = now.astimezone(pytz.timezone(tz))
    fmt = loc.strftime("%I:%M %p") if timefmt=="12-Hour" else loc.strftime("%H:%M")
    st.markdown(f"**{city}:** {fmt}")
st.markdown("---")

# — Data extractors —
def fetch_fx(sym):
    base, quote = sym[:3], sym[3:]
    try:
        data = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=5).json().get("rates", {})
        return data.get(quote)
    except:
        return None

def fetch_index(sym):
    ticker = {"US30USD":"^DJI","SPX500USD":"^GSPC","NAS100USD":"^IXIC"}[sym]
    hist = yf.Ticker(ticker).history(period="1d")
    return hist['Close'].iloc[-1] if not hist.empty else None

def get_price(sym):
    if sym in ["US30USD","SPX500USD","NAS100USD"]:
        return fetch_index(sym)
    return fetch_fx(sym)

# — Scrolling ticker —
texts = []
for sym in selected:
    val = get_price(sym)
    texts.append(f"{sym} {val:.2f}" if val else f"{sym}: N/A")
st.markdown(
    f"<marquee style='color:{fg}; background:{bg}; font-family:\"Courier New\",monospace'>{' | '.join(texts)}</marquee>",
    unsafe_allow_html=True
)

# — Detailed panel display —
for sym in selected:
    val = get_price(sym)
    if val is None:
        st.markdown(f"<span style='color:red;'>{sym}: N/A</span>", unsafe_allow_html=True)
        continue
    open_val = val * 0.995
    diff = val - open_val
    arrow, clr = ("▲","green") if diff>=0 else ("▼","red")
    pct = diff/open_val*100
    st.markdown(f"""
      <div style='color:{fg};background:{bg};padding:8px;margin:4px 0;border:1px solid #555;'>
        <h2>{sym}</h2>
        <h3>{val:.5f}</h3>
        <h4 style='color:{clr}'>{arrow} {diff:.5f} ({pct:.2f}%)</h4>
      </div>
    """, unsafe_allow_html=True)

st.markdown(f"🔁 Auto-refresh every **{interval_ms//1000}s**")
