# Market AI Analyzer

একটি educational/paper-trading market analyzer। এটি CSV OHLC data থেকে EMA, RSI এবং MACD হিসাব করে Bullish/Bearish/Neutral assessment দেখায়।

## চালানোর নিয়ম

Python 3.10+ ইনস্টল করে:

```bash
pip install -r requirements.txt
streamlit run app.py
```

তারপর browser-এ দেখানো local address খুলুন।

## CSV format

প্রয়োজনীয় columns:
- Open
- High
- Low
- Close

ঐচ্ছিক:
- Date
- Volume

## গুরুত্বপূর্ণ

এটি কোনো guaranteed prediction engine নয় এবং real-money trade/order execute করে না। আগে paper trading ও historical backtesting দিয়ে পরীক্ষা করা উচিত।
