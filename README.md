# 📈 Stock Analyzer & ML Price Predictor

> Real-time stock analysis, technical indicators, and next-day price forecasting — powered by Python, Streamlit, and Machine Learning.

---

## 🌟 Versions

| Version | File | Description |
|--------|------|-------------|
| v1 | `app_v1.py` | Original release — Matplotlib charts, flat layout |
| v2 | `app_v2.py` | Upgraded to Plotly, interactive MACD crossover signals |
| **v3 ⭐ Pro** | `app_v3.py` | **Full redesign** — custom dark UI, tabbed layout, ATR, CI range, smart caching |

> **`app_v3.py` is the Pro version** — a production-grade dashboard with a fintech-style UI built with custom CSS (`app_v3_style.py`), a live KPI bar, prediction confidence intervals, candlestick charts, and significantly better performance through smart caching.

---

## 🚀 Features

### Core (All Versions)
- 📡 Live stock data via **Yahoo Finance**
- 📊 Technical indicators: **RSI, MACD, MA20, MA50**
- 🤖 **Random Forest** next-day return prediction
- 📉 Actual vs. Predicted return visualization
- 📐 Model metrics: **RMSE & R² Score**
- 🔮 Next-day closing price forecast

### ⭐ Pro Version (v3) Exclusive
- 📌 Live **KPI bar** — Last Close, RSI signal, ATR-14, R², Tomorrow's forecast
- 🕯️ **Candlestick chart** toggle (Line + MAs ↔ Candlestick)
- 📦 Color-coded **volume subplot** synced with price chart
- 🃏 **3-card prediction panel** — Last Close · Tomorrow Forecast · 90% CI Range
- 🎯 **BULLISH / BEARISH / NEUTRAL** signal badge on forecast
- 📏 **ATR-14** volatility indicator
- 🔒 **Confidence Interval** based on 20-day rolling volatility
- 💾 **CSV download** button for historical data
- ⚡ Smart caching with `ttl=300` + `@st.cache_resource` for the trained model

---

## 🖥️ Demo

https://github.com/user-attachments/assets/3d826474-fbb4-4f75-80c1-4cffae5f996f

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Data | `pandas`, `numpy`, `yfinance` |
| Visualization | `plotly` (v1 also uses `matplotlib`) |
| Machine Learning | `scikit-learn` — Random Forest Regressor |
| UI | `streamlit` |
| Styling (v3) | Custom CSS via `app_v3_style.py` |

---

## 📂 Project Structure

```
Stock-Analyzer/
│
├── app_v1.py           # v1 — Original (Matplotlib)
├── app_v2.py           # v2 — Plotly upgrade
├── app_v3.py           # v3 PRO — Full redesign ⭐
├── app_v3_style.py     # Custom CSS for Pro version
├── ticker_list.py      # Preset tickers (US + Indian markets)
├── requirements.txt    # Dependencies
└── README.md
```

---

## 📊 Machine Learning Workflow

```
Historical Data  →  Feature Engineering  →  Time-Series Split
      ↓                                              ↓
  yFinance                MA20, MA50,           80% Train
                          Lags 1-3,             20% Test
                          OHLCV                     ↓
                                           Random Forest (400 trees)
                                                    ↓
                                      Predict next-day return → price
```

**Why Random Forest?**
- Handles noisy, non-stationary financial data
- Captures nonlinear market patterns
- Naturally resistant to overfitting via ensemble averaging

---

## 📐 Evaluation Metrics

| Metric | What it measures |
|--------|-----------------|
| **RMSE** | Average magnitude of prediction error (as % return) |
| **R² Score** | How well the model explains return variance |


---

## ▶️ How to Run

### 1. Clone the repository
```bash
git clone https://github.com/your-username/Stock-Analyzer.git
cd Stock-Analyzer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
# Pro Version (Recommended)
streamlit run app_v3.py

# v2
streamlit run app_v2.py

# v1
streamlit run app_v1.py
```

---

## 📌 Usage

1. Enter a stock ticker in the sidebar (e.g., `NVDA`, `AAPL`, `TCS.NS`)
2. Choose historical data range (1–5 years)
3. Explore the **Price & Volume**, **Indicators**, **ML Forecast**, and **Data** tabs
4. Get the next-day predicted closing price with a BULLISH/BEARISH/NEUTRAL signal
5. Download the processed data as CSV

---

## 🗺️ Version History

| Version | Key Changes |
|---------|------------|
| **v1** | Baseline app with Matplotlib static charts, basic RSI & MACD |
| **v2** | Replaced Matplotlib with Plotly; added interactive MACD crossover markers; improved return annotations |
| **v3 Pro** | Complete UI overhaul with custom CSS; tabbed layout; ATR-14; candlestick toggle; confidence interval; smart caching; Market Cap & P/E in sidebar; CSV export |

---

## 🔭 Future Improvements

- [ ] LSTM / Transformer deep learning models
- [ ] Multi-ticker portfolio tracker
- [ ] Real-time intraday data & live predictions
- [ ] Backtesting engine with P&L simulation
- [ ] Cloud deployment (Streamlit Cloud / AWS)
- [ ] Email/SMS price alert system

---

## ⚠️ Disclaimer

This project is for **educational purposes only**.
Predictions are not financial advice. Always do your own research before making investment decisions.

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute with attribution.

