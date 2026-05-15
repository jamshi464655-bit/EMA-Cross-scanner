import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime

st.set_page_config(page_title="EasyCharts Pro - Ultra Scanner", layout="wide", page_icon="🚀")

# ====================== BEAUTIFUL UI ======================
st.markdown("""
<style>
    .header {
        background: linear-gradient(135deg, #6b46c1, #7c3aed);
        padding: 35px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #ec4899, #f472b6);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        color: white;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        height: 130px;
        transition: transform 0.3s;
    }
    .metric-card:hover { transform: scale(1.05); }
    .panel-title {
        background: linear-gradient(135deg, #f59e0b, #fb923c);
        color: white;
        padding: 12px;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
        margin: 15px 0 10px 0;
    }
    .positive { color: #4ade80; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>🚀 EasyCharts Pro - Ultra Scanner</h1>
    <p>AI-Powered Multi-Indicator NSE Stock Scanner</p>
</div>
""", unsafe_allow_html=True)

# ================== SETTINGS ==================
st.sidebar.header("⚙️ Scanner Settings")
scan_limit = st.sidebar.slider("സ്കാൻ ചെയ്യേണ്ട സ്റ്റോക്കുകളുടെ എണ്ണം", 30, 200, 80)
auto_refresh = st.sidebar.checkbox("Auto Refresh (60 sec)", value=True)

# ================== SYMBOLS ==================
symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", "LT", "HINDUNILVR",
           "AXISBANK", "KOTAKBANK", "ADANIENT", "SUNPHARMA", "TITAN", "ULTRACEMCO", "ASIANPAINT", "BAJFINANCE",
           "DMART", "TRENT", "ZOMATO", "NYKAA", "IRCTC", "HAL", "BEL", "PFC", "RECLTD", "POWERGRID", "NTPC", "ONGC"]

def scan_ema_squeeze(symbols, limit):
    results = []
    tickers = [f"{s}.NS" for s in symbols[:limit]]
    
    progress = st.progress(0)
    status = st.empty()
    
    data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', progress=False)
    
    for i, s in enumerate(symbols[:limit]):
        try:
            status.text(f"Analyzing {s}...")
            progress.progress((i+1)/limit)
            
            df = data[f"{s}.NS"].copy().dropna()
            if len(df) < 60: continue
            
            ltp = round(df['Close'].iloc[-1], 2)
            change = round(((ltp - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100, 2)
            
            ema8 = ta.ema(df['Close'], length=8).iloc[-1]
            ema13 = ta.ema(df['Close'], length=13).iloc[-1]
            ema21 = ta.ema(df['Close'], length=21).iloc[-1]
            ema55 = ta.ema(df['Close'], length=55).iloc[-1]
            
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            emas = [ema8, ema13, ema21, ema55]
            spread = (max(emas) - min(emas)) / min(emas) * 100
            vol_ratio = round(df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1], 2)
            
            if spread < 1.5 and 47 <= rsi <= 56:
                results.append({
                    "Symbol": s,
                    "LTP": ltp,
                    "%Change": change,
                    "RSI": round(rsi, 1),
                    "Spread%": round(spread, 2),
                    "Vol Ratio": vol_ratio,
                    "Signal": "🎯 SQUEEZE"
                })
        except:
            continue
            
    progress.empty()
    status.empty()
    return results

# ================== MAIN BUTTON ==================
if st.button("🚀 START MARKET SCAN", type="primary", use_container_width=True):
    with st.spinner("Scanning Market..."):
        found = scan_ema_squeeze(symbols, scan_limit)
        df = pd.DataFrame(found)
        
        # ====================== METRIC CARDS ======================
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #ec4899, #db2777);">
                <h1 style="margin:0;">{len(df)}</h1>
                <p>EMA Squeeze Setups</p>
            </div>
            """, unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #22c55e, #4ade80); color:black;">
                <h1 style="margin:0;color:black;">{len(df[df['RSI'] > 55])}</h1>
                <p style="color:black;">Live Breakouts</p>
            </div>
            """, unsafe_allow_html=True)
        
        with c3:
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #a855f7, #c084fc);">
                <h1 style="margin:0;">{len(df[df['Vol Ratio'] > 1.8])}</h1>
                <p>Strong Momentum</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.success(f"✅ Scan Completed at {datetime.now().strftime('%I:%M:%S %p')}")
        
else:
    st.info("👆 'START MARKET SCAN' ബട്ടൺ ക്ലിക്ക് ചെയ്ത് സ്കാൻ തുടങ്ങൂ")

st.caption("Beautiful UI • EMA Squeeze Strategy • Powered by yfinance")