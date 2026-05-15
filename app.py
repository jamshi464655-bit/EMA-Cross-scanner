import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

# Page Configuration
st.set_page_config(page_title="EMA Squeeze Pro Scanner", layout="wide")

# Custom UI Styling
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
    .stDataFrame {
        border: 1px solid #e6e9ef;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_symbols_list():
    # ആദ്യം നിഫ്റ്റി 50 ഇൻഡക്സ്, പിന്നെ പ്രധാന സ്റ്റോക്കുകൾ
    return [
        "NIFTY_50", "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "ITC", "SBIN", 
        "BHARTIARTL", "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "TITAN",
        "SUNPHARMA", "ULTRACEMCO", "BAJFINANCE", "NESTLEIND", "HCLTECH", "WIPRO", "ADANIENT",
        "JINDALSTEL", "TATASTEEL", "TATAMOTORS", "COALINDIA", "HINDALCO", "GRASIM", "JSWSTEEL",
        "APOLLOHOSP", "CIPLA", "DRREDDY", "DIVISLAB", "BPCL", "ONGC", "POWERGRID", "NTPC",
        "TATACONSUM", "HEROMOTOCO", "BAJAJ-AUTO", "EICHERMOT", "INDUSINDBK", "HDFCLIFE", "SBILIFE",
        "BEL", "HAL", "RVNL", "IRCON", "ZOMATO", "DLF", "BHEL", "PNB", "CANBK", "TRENT", "DIXON",
        "POLYCAB", "TATAPOWER", "MAZDOCK", "JIOFIN", "SUZLON", "PFC", "RECLTD"
    ]

def scan_ema_squeeze(symbols, count):
    results = []
    # Yahoo Finance ടിക്കറുകൾ തയ്യാറാക്കുന്നു
    tickers = []
    for s in symbols[:count]:
        if s == "NIFTY_50":
            tickers.append("^NSEI")
        else:
            tickers.append(f"{s}.NS")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # ഒന്നിച്ച് ഡാറ്റ ഡൗൺലോഡ് ചെയ്യുന്നു (Speed മെച്ചപ്പെടുത്താൻ)
    data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', progress=False)
    
    for idx, s in enumerate(symbols[:count]):
        try:
            status_text.text(f"🔍 Analyzing: {s}")
            progress_bar.progress((idx + 1) / len(tickers))
            
            ticker_key = "^NSEI" if s == "NIFTY_50" else f"{s}.NS"
            df = data[ticker_key].copy().dropna()
            
            if len(df) < 60: continue
            
            # EMA കണക്കുകൂട്ടലുകൾ
            ema8 = ta.ema(df['Close'], length=8).iloc[-1]
            ema13 = ta.ema(df['Close'], length=13).iloc[-1]
            ema21 = ta.ema(df['Close'], length=21).iloc[-1]
            ema55 = ta.ema(df['Close'], length=55).iloc[-1]
            
            # RSI
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            
            # EMA Spread (Narrow Range %)
            emas = [ema8, ema13, ema21, ema55]
            ema_spread = (max(emas) - min(emas)) / min(emas) * 100
            
            # Volume Ratio
            vol_ma20 = df['Volume'].rolling(20).mean().iloc[-1]
            curr_vol = df['Volume'].iloc[-1]
            vol_ratio = round(curr_vol / vol_ma20, 2) if vol_ma20 > 0 else 0
            
            ltp = round(df['Close'].iloc[-1], 2)
            
            # --- നിബന്ധനകൾ (Conditions) ---
            # 1. EMA Spread < 1.5% (Tight Squeeze)
            # 2. RSI 48 - 56 (Consolidation phase)
            if ema_spread < 1.5 and 48 <= rsi <= 56:
                
                # TradingView ലിങ്ക്
                tv_symbol = "NIFTY" if s == "NIFTY_50" else f"NSE:{s}"
                chart_url = f"https://www.tradingview.com/chart/?symbol={tv_symbol}"
                
                results.append({
                    "Symbol": s,
                    "LTP": ltp,
                    "RSI": round(rsi, 2),
                    "EMA Spread %": round(ema_spread, 2),
                    "Vol Ratio": vol_ratio,
                    "View Chart": chart_url,
                    "Signal": "🎯 SQUEEZE"
                })
        except:
            continue
            
    progress_bar.empty()
    status_text.empty()
    return results

# UI ഭാഗം
st.markdown("<div class='main-header'><h1>🚀 EMA Squeeze Pro Scanner</h1><p>Nifty 50 & Stocks | EMA 8, 13, 21, 55 Narrow Range + RSI 50</p></div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Scanner Settings")
    scan_count = st.slider("എത്ര സ്റ്റോക്കുകൾ പരിശോധിക്കണം?", 10, 500, 100)
    run_btn = st.button("🔍 START SCANNING")
    st.info("ഇൻഡക്സും (Nifty 50) ഈ സ്കാനറിൽ ഉൾപ്പെടുത്തിയിട്ടുണ്ട്.")

if run_btn:
    symbols = get_symbols_list()
    found_stocks = scan_ema_squeeze(symbols, scan_count)
    
    if found_stocks:
        st.success(f"🎯 {len(found_stocks)} ബ്രേക്ക്ഔട്ട് സാധ്യതയുള്ളവ കണ്ടെത്തി!")
        df_final = pd.DataFrame(found_stocks)
        
        # ടേബിൾ ഡിസ്‌പ്ലേ
        st.dataframe(
            df_final, 
            column_config={
                "View Chart": st.column_config.LinkColumn(
                    "TradingView Link",
                    display_text="Open Chart 📈"
                )
            },
            use_container_width=True,
            hide_index=True
        )
        
        # ഡൗൺലോഡ് ബട്ടൺ
        csv = df_final.to_csv(index=False)
        st.download_button("📥 Download Results", csv, "ema_squeeze_results.csv", "text/csv")
    else:
        st.warning("നിലവിൽ നിബന്ധനകൾ പാലിക്കുന്ന സ്റ്റോക്കുകളോ ഇൻഡക്സോ ലഭ്യമല്ല.")
