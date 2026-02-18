import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# ---------------- UI SETUP ----------------
st.set_page_config(page_title="Stock ML Predictor Pro", layout="wide")
st.title("📈 Stock Market Analyzer & ML Predictor")
ticker = st.sidebar.text_input("Enter Stock Ticker Symbol", "NVDA").upper()
years = st.sidebar.slider("Historical Data (Years)", 1, 5, 2)

# ---------------- MARKET INFO ----------------
@st.cache_data
def get_stock_info(ticker):
    info = yf.Ticker(ticker).info
    exchange = info.get("exchange", "N/A")
    timezone = info.get("exchangeTimezoneName", "N/A")
    currency = info.get("currency", "N/A")
    MARKET_HOURS = {
        "NMS": ("09:30 AM", "04:00 PM"),  # NASDAQ
        "NYQ": ("09:30 AM", "04:00 PM"),  # NYSE
        "NSI": ("09:15 AM", "03:30 PM"),  # NSE India
        "BSE": ("09:15 AM", "03:30 PM"),}

    open_time, close_time = MARKET_HOURS.get(exchange, ("N/A", "N/A"))
    return currency,exchange,timezone, open_time, close_time

currency, exchange, timezone, open_t, close_t = get_stock_info(ticker)
SYMBOLS = {"USD": "$", "INR": "₹", "EUR": "€"}
currency_symbol = SYMBOLS.get(currency, currency)

st.sidebar.markdown("## Market Information")
st.sidebar.markdown(f"""
**Ticker:** {ticker}  
**Exchange:** {exchange}  
**Currency:** {currency}  
**Timezone:** {timezone}  
**Market Hours:** {open_t} – {close_t}""")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data(ticker, years):
    df = yf.download(ticker, period=f"{years}y", interval="1d")
    if df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

stock_raw = load_data(ticker, years)
if stock_raw is None or stock_raw.empty:
    st.error("Invalid Ticker or No Data Found.")
    st.stop()
stock=stock_raw.copy()


# ---------------- TECHNICAL INDICATORS ----------------
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

stock["Return"] = stock["Close"].pct_change()
stock["RSI"] = calculate_rsi(stock["Close"])

# MACD
ema12 = stock["Close"].ewm(span=12, adjust=False).mean()
ema26 = stock["Close"].ewm(span=26, adjust=False).mean()
stock["MACD"] = ema12 - ema26
stock["Signal"] = stock["MACD"].ewm(span=9, adjust=False).mean()
stock["Histogram"] = stock["MACD"] - stock["Signal"]

# MACD crossover signals
stock["MACD_prev"] = stock["MACD"].shift(1)
stock["Signal_prev"] = stock["Signal"].shift(1)

stock["Bullish"] = (
    (stock["MACD_prev"] < stock["Signal_prev"]) & (stock["MACD"] > stock["Signal"]))
stock["Bearish"] = (
    (stock["MACD_prev"] > stock["Signal_prev"]) & (stock["MACD"] < stock["Signal"]))

stock["Lag1"] = stock["Return"].shift(1)
stock["Lag2"] = stock["Return"].shift(2)
stock["Lag3"] = stock["Return"].shift(3)
stock["MA20"] = stock["Close"].rolling(20).mean()
stock["MA50"] = stock["Close"].rolling(50).mean()
# Target = NEXT DAY RETURN 
stock["Target"] = stock["Return"].shift(-1)
stock.dropna(inplace=True)

# ---------------- PREPARE ML DATA ----------------
features = ["Lag1","Lag2", "Lag3", "MA20", "MA50","Open","High","Low","Volume"]
X = stock[features]
y = stock["Target"]

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,shuffle=False)
# ---------------- MODEL ----------------
model = RandomForestRegressor(n_estimators=400,max_depth=10,
    min_samples_leaf=10,random_state=42)
model.fit(X_train, y_train)
pred_return = model.predict(X_test)

# ---------------- TOMORROW PRICE PREDICTION ----------------
latest_features = X.iloc[[-1]]
latest_return_pred = model.predict(latest_features)[0]
last_close = stock["Close"].iloc[-1]
next_price = last_close * (1 + latest_return_pred)
next_price=float(next_price)


#=================================UI DISPLAY========================================

# ---------------- PRICE TREND ----------------
st.subheader("Stock Price Trend")
fig = go.Figure()
fig.add_trace(go.Scatter(x=stock.index, y=stock['Close'], name="Close Price"))
fig.add_trace(go.Scatter(x=stock.index, y=stock['MA20'], name="MA20", line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=stock.index, y=stock['MA50'], name="MA50", line=dict(dash='dot')))
fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=True, height=500)
st.plotly_chart(fig, use_container_width=True)

# ---------------- DATA PREVIEW ----------------
st.subheader("📊 Data Preview")
OHLCV=["Open", "High", "Low", "Close", "Volume","Return","RSI"]
st.dataframe(pd.concat([stock[OHLCV].head(), stock[OHLCV].tail()]))

# ---------------- RSI ----------------
st.subheader("📊 RSI Indicator")
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=stock.index,y=stock["RSI"],mode="lines",name="RSI"))

fig_rsi.add_hline(y=70,line_dash="dash",opacity=0.6,
    annotation_text="Overbought (70)",annotation_position="top left")

fig_rsi.add_hline(y=30,line_dash="dash",opacity=0.6,
    annotation_text="Oversold (30)", annotation_position="bottom left")

fig_rsi.update_layout(xaxis_title="Date",yaxis_title="RSI",
    template="plotly_dark",height=400)
st.plotly_chart(fig_rsi, use_container_width=True)


# ---------------- MACD ----------------
st.subheader("📊 MACD Indicator")
fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=stock.index,y=stock["MACD"],mode="lines",name="MACD"))
fig_macd.add_trace(go.Scatter(x=stock.index,y=stock["Signal"],mode="lines",name="Signal Line"))
fig_macd.add_trace(go.Bar(x=stock.index,y=stock["Histogram"],name="Histogram",opacity=0.7))

fig_macd.add_trace(go.Scatter(x=stock.index[stock["Bullish"]],
    y=stock.loc[stock["Bullish"], "MACD"],
    mode="markers",name="Bullish Signal",
    marker=dict(symbol="triangle-up", size=10)))

fig_macd.add_trace(go.Scatter(x=stock.index[stock["Bearish"]],
    y=stock.loc[stock["Bearish"], "MACD"],
    mode="markers", name="Bearish Signal",
    marker=dict(symbol="triangle-down", size=10)))

fig_macd.update_layout(template="plotly_dark",height=400)
st.plotly_chart(fig_macd, use_container_width=True)


# ---------------- METRICS ----------------
rmse = np.sqrt(mean_squared_error(y_test, pred_return))
r2 = r2_score(y_test, pred_return)
st.subheader("📊 Model Performance (Return Prediction)")
col1, col2 = st.columns(2)
col1.metric("RMSE", f"{rmse*100:.2f}%")
col2.metric("R² Score", f"{r2:.3f}")

# ---------------- ACTUAL vs PREDICTED RETURNS ----------------
# Extract returns
prev_return = stock["Return"].iloc[-1]*100
pred_return_pct = pred_return[-1] * 100

prev_color = "green" if prev_return >= 0 else "red"
pred_color = "green" if pred_return_pct >= 0 else "red"
prev_arrow = "↑" if prev_return >= 0 else "↓"
pred_arrow = "↑" if pred_return_pct >= 0 else "↓"

# Display metrics
st.subheader("📊 Return Summary")
col1, col2 = st.columns(2)
col1.markdown(
    f"""
    **Previous Day Return**  
    <span style="color:{prev_color}; font-size:28px;">
    {prev_return:.2f}% {prev_arrow}
    </span>""",unsafe_allow_html=True)

col2.markdown(
    f"""
    **Predicted Next-Day Return**  
    <span style="color:{pred_color}; font-size:28px;">
    {pred_return_pct:.2f}% {pred_arrow}
    </span>""",unsafe_allow_html=True)

#Predicted vs Actual Returns Graph
fig_pred = go.Figure()
fig_pred.add_trace(go.Scatter(x=y_test.index, y=y_test.values, mode="lines", name="Actual Return"))
fig_pred.add_trace(go.Scatter(x=y_test.index,y=pred_return,mode="lines",name="Predicted Return"))

fig_pred.add_annotation(xref="paper", yref="paper", x=0.01, y=0.95,
    text=f"Previous Return: {prev_arrow} {prev_return:.2f}%", 
    showarrow=False, font=dict(color=prev_color, size=13))

fig_pred.add_annotation(xref="paper", yref="paper", x=0.01, y=0.90,
    text=f"Predicted Return: {pred_arrow} {pred_return_pct:.2f}%",
    showarrow=False, font=dict(color=pred_color, size=13))

fig_pred.update_layout(title="Return Prediction Performance", template="plotly_dark",
    xaxis_title="Date", yaxis_title="Return",height=500)
st.plotly_chart(fig_pred, use_container_width=True)

# TOMORROW PRICE PREDICTION 
st.subheader("Tomorrow Price Prediction")
st.success(f"Predicted Closing Price: {currency_symbol}{next_price:.2f} ({currency})")

