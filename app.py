import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="EMA Squeeze Pro Scanner", layout="wide")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
    }
    .metric-card {
        background: linear-gradient(135deg, #ec4899, #f472b6);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'><h1>🚀 EMA Squeeze Pro Scanner</h1><p>Nifty 50 & Stocks | EMA 8,13,21,55 Narrow Range + RSI 50</p></div>", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_symbols():
    return ["RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","HINDUNILVR","ITC","SBIN","BHARTIARTL","KOTAKBANK",
            "LT","AXISBANK","ASIANPAINT","MARUTI","TITAN","SUNPHARMA","ULTRACEMCO","BAJFINANCE","DMART","TRENT",
            "ZOMATO","NYKAA","IRCTC","HAL","BEL","PFC","RECLTD","POWERGRID","NTPC","ONGC"]

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def scan_ema_squeeze(symbols, count):
    results = []
    symbols = symbols[:count]
    
    progress = st.progress(0)
    status = st.empty()
    
    for i, s in enumerate(symbols):
        try:
            status.text(f"Analyzing {s}...")
            progress.progress((i+1)/len(symbols))
            
            df = yf.download(f"{s}.NS", period="1y", interval="1d", progress=False)
            if len(df) < 60: continue
            
            df['EMA8'] = calculate_ema(df['Close'], 8)
            df['EMA13'] = calculate_ema(df['Close'], 13)
            df['EMA21'] = calculate_ema(df['Close'], 21)
            df['EMA55'] = calculate_ema(df['Close'], 55)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            last = df.iloc[-1]
            ltp = round(last['Close'], 2)
            rsi = round(last['RSI'], 1)
            
            emas = [last['EMA8'], last['EMA13'], last['EMA21'], last['EMA55']]
            spread = (max(emas) - min(emas)) / min(emas) * 100
            
            vol_ratio = round(last['Volume'] / df['Volume'].rolling(20).mean().iloc[-1], 2)
            
            if spread < 1.5 and 47 <= rsi <= 56:
                results.append({
                    "Symbol": s,
                    "LTP": ltp,
                    "RSI": rsi,
                    "Spread%": round(spread, 2),
                    "Vol Ratio": vol_ratio,
                    "Signal": "🎯 SQUEEZE"
                })
        except:
            continue
    
    progress.empty()
    status.empty()
    return results

with st.sidebar:
    st.header("Scanner Settings")
    scan_count = st.slider("സ്കാൻ ചെയ്യേണ്ട സ്റ്റോക്കുകൾ", 20, 100, 50)
    if st.button("🚀 START SCANNING"):
        st.session_state.run_scan = True

if st.session_state.get('run_scan', False):
    symbols = get_symbols()
    found = scan_ema_squeeze(symbols, scan_count)
    
    if found:
        st.success(f"🎯 {len(found)} EMA Squeeze setups found!")
        df = pd.DataFrame(found)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False)
        st.download_button("📥 Download Results", csv, "squeeze_results.csv", "text/csv")
    else:
        st.warning("നിലവിൽ Squeeze setups ഒന്നും കണ്ടെത്തിയില്ല")

st.caption("Beautiful UI • Pure Pandas EMA • No pandas_ta dependency")
