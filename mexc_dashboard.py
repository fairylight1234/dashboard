
import streamlit as st
import pandas as pd
import requests
import pandas_ta as ta

# Dashboard configuration
st.set_page_config(page_title="MEXC Futures Dashboard", layout="wide")

st.title("🚀 MEXC Real-Time Futures Trading Dashboard")

# Selected coins for scalping
coins = ['PEPEUSDT', '1000SATSUSDT', 'ORDIUSDT', 'DOGEUSDT', 'WIFUSDT']

# Trading Parameters per coin
params = {
    'PEPEUSDT': {'leverage': 50, 'tp': 5, 'sl': 2.5, 'p_win': 0.7},
    '1000SATSUSDT': {'leverage': 75, 'tp': 6, 'sl': 2, 'p_win': 0.75},
    'ORDIUSDT': {'leverage': 25, 'tp': 4, 'sl': 2, 'p_win': 0.65},
    'DOGEUSDT': {'leverage': 30, 'tp': 3, 'sl': 1.5, 'p_win': 0.7},
    'WIFUSDT': {'leverage': 50, 'tp': 5, 'sl': 2.5, 'p_win': 0.68},
}

# Function to fetch current price and volume
def fetch_price_volume(symbol):
    url = f"https://api.mexc.com/api/v3/ticker/24hr?symbol={symbol}"
    try:
        r = requests.get(url).json()
        return float(r['lastPrice']), float(r['volume'])
    except:
        return None, None

# Function to fetch historical klines
def fetch_klines(symbol):
    url = f"https://api.mexc.com/api/v3/klines?symbol={symbol}&interval=1m&limit=100"
    try:
        df = pd.DataFrame(requests.get(url).json())
        df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', '_1', '_2', '_3', '_4', '_5', '_6']
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        return df
    except:
        return pd.DataFrame()

# Analysis for each coin
results = []
for symbol in coins:
    df = fetch_klines(symbol)
    price, vol_now = fetch_price_volume(symbol)
    if df.empty or not price:
        continue

    vol_avg = df['volume'].mean()
    rsi_val = ta.rsi(df['close'], length=14).iloc[-1]
    macd = ta.macd(df['close'])
    macd_diff = macd['MACD_12_26_9'].iloc[-1] - macd['MACDs_12_26_9'].iloc[-1]
    rsi_delta = abs(rsi_val - 50)
    candle_strength = 1.1  # estimated from price action

    tp = params[symbol]['tp']
    sl = params[symbol]['sl']
    p_win = params[symbol]['p_win']
    lev = params[symbol]['leverage']

    # Custom formulas
    epp = (tp * p_win) - (sl * (1 - p_win))
    lrl = round(1 / (sl * lev / 100), 2)
    tcs = round((vol_now / vol_avg) + (macd_diff / rsi_delta) + candle_strength, 2)
    trade_ok = epp > 0 and tcs > 2.5

    results.append({
        'Coin': symbol,
        'Price': price,
        'EPP': round(epp, 2),
        'LRL': lrl,
        'TCS': tcs,
        'TRADE_OK ✅': '✅' if trade_ok else '❌'
    })

# Show results
st.dataframe(pd.DataFrame(results))
