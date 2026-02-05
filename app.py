import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

# ---------------- UI SETUP ----------------
st.set_page_config(page_title="Stock ML Predictor", layout="centered")
st.title("📈 Stock Analyzer and Price Predictor")

ticker = st.text_input("Enter Stock Symbol", "NVDA")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data(ticker):
    return yf.download(ticker, period="2y", interval="1d")
stock = load_data(ticker)

st.subheader("📊 Data Preview")
preview = pd.concat([stock.head(), stock.tail()], ignore_index=True)
st.dataframe(preview)

st.subheader("📈 Statistical Summary")
st.dataframe(stock.describe())

# ---------------- FEATURE ENGINEERING ----------------

stock["MA20"] = stock["Close"].rolling(20).mean()
stock["MA50"] = stock["Close"].rolling(50).mean()
stock["Return"] = stock["Close"].pct_change()
stock["Target"] = stock["Close"].shift(-1)

stock.dropna(inplace=True)

# ---------------- VISUALIZATION ----------------

st.subheader("📉 Stock Price Trend")

fig1, ax1 = plt.subplots(figsize=(12,6))
ax1.plot(stock.index, stock["Close"], label="Close")
ax1.plot(stock.index, stock["MA20"], label="MA20")
ax1.plot(stock.index, stock["MA50"], label="MA50")
ax1.set_title(f"{ticker} Stock Price with Moving Averages")
ax1.set_xlabel("Date")
ax1.set_ylabel("Price")
ax1.legend()
ax1.grid(True)
st.pyplot(fig1)

# ---------------- PREPARE DATA ----------------
X = stock[["Open","High","Low","Volume","MA20","MA50","Return"]]
y = stock["Close"].shift(-1).dropna()

X = X.iloc[:-1] 

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2)

#Random Forest Regression
model = RandomForestRegressor(n_estimators=400, random_state=42,max_depth=10)
model.fit(X_train, y_train)
prediction = model.predict(X_test)

# ---------------- METRICS ----------------

rmse = np.sqrt(mean_squared_error(y_test, prediction))
r2 = r2_score(y_test, prediction)

st.subheader("📊 Model Performance")
col1, col2 = st.columns(2)
col1.metric("RMSE", f"{rmse:.2f}")
col2.metric("R² Score", f"{r2:.3f}")

# ---------------- PREDICTION CHART ----------------

st.subheader("📉 Actual vs Predicted Price")

fig2, ax2 = plt.subplots(figsize=(12,6))
ax2.plot(y_test.values, label="Actual")
ax2.plot(prediction, label="Predicted")
ax2.set_xlabel("Days")
ax2.set_ylabel("Price")
ax2.set_title("Model Prediction Performance")
ax2.legend()
ax2.grid(True)
st.pyplot(fig2)

# ---------------- TOMORROW PREDICTION ----------------
latest_data = X.iloc[-1:].values
next_price = model.predict(latest_data)[0]

st.subheader("🔮 Tomorrow Price Prediction")
st.success(f"Predicted Closing Price: ${next_price:.2f}")
