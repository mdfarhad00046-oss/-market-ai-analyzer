import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Market AI Analyzer", page_icon="📊", layout="wide")

st.title("📊 Market AI Analyzer")
st.caption("Educational / paper-trading analysis — not a guaranteed prediction or financial advice.")

uploaded = st.file_uploader(
    "OHLC CSV আপলোড করুন",
    type=["csv"],
    help="Columns: Date, Open, High, Low, Close, Volume (Volume optional)"
)

def analyze(df):
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    required = ["open", "high", "low", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    for c in required + (["volume"] if "volume" in df.columns else []):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=required).reset_index(drop=True)

    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()

    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))

    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    last = df.iloc[-1]
    score = 0

    if last["ema9"] > last["ema21"]:
        score += 1
    else:
        score -= 1

    if last["macd"] > last["signal"]:
        score += 1
    else:
        score -= 1

    if pd.notna(last["rsi"]):
        if 50 <= last["rsi"] <= 70:
            score += 1
        elif 30 <= last["rsi"] < 50:
            score -= 1
        elif last["rsi"] > 70:
            score -= 1

    if score >= 2:
        label = "BULLISH / UP SCENARIO"
    elif score <= -2:
        label = "BEARISH / DOWN SCENARIO"
    else:
        label = "NEUTRAL / WAIT"

    confidence = min(90, 50 + abs(score) * 13)

    return df, last, label, confidence, score

if uploaded:
    try:
        data = pd.read_csv(uploaded)
        df, last, label, confidence, score = analyze(data)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Close", f"{last['close']:.4f}")
        c2.metric("RSI", f"{last['rsi']:.2f}" if pd.notna(last["rsi"]) else "N/A")
        c3.metric("EMA 9 / 21", f"{last['ema9']:.4f} / {last['ema21']:.4f}")
        c4.metric("AI Confidence", f"{confidence}%")

        st.subheader("AI Market Assessment")
        st.info(label)

        st.write("**Indicator summary**")
        st.write(
            f"- EMA: {'Bullish' if last['ema9'] > last['ema21'] else 'Bearish'}\n"
            f"- MACD: {'Positive' if last['macd'] > last['signal'] else 'Negative'}\n"
            f"- RSI: {last['rsi']:.2f} — interpreted together with the other indicators"
        )

        st.warning(
            "এটি কেবল indicator-based educational analysis। "
            "এটি ভবিষ্যৎ নিশ্চিতভাবে বলতে পারে না এবং এখানে কোনো real-money order পাঠানো হয় না।"
        )

        chart = df[["close", "ema9", "ema21"]].tail(150)
        st.line_chart(chart)

        with st.expander("শেষ 20টি candle দেখুন"):
            st.dataframe(df.tail(20), use_container_width=True)

    except Exception as e:
        st.error(f"CSV পড়তে সমস্যা: {e}")
else:
    st.markdown("""
### কীভাবে ব্যবহার করবেন
1. আপনার broker/exchange থেকে OHLC candle data CSV হিসেবে export করুন।
2. এখানে CSV upload করুন।
3. App EMA, RSI ও MACD হিসাব করে একটি **Bullish / Bearish / Neutral** assessment দেখাবে।
4. আগে paper-trading/backtesting-এ পরীক্ষা করুন।

**CSV উদাহরণ**
`Date,Open,High,Low,Close,Volume`
""")
    st.code("""Date,Open,High,Low,Close,Volume
2026-10-01,100,102,99,101,1200
2026-10-02,101,104,100,103,1500
2026-10-03,103,105,101,104,1800""")
