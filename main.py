import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

ticker=input("Enter Stock Symbol: ")
stock = yf.download(ticker, period="2y", interval="1d")

# Data Exploration
preview = pd.concat([stock.head(), stock.tail()])
print(preview,end="\n\n")
print(stock.describe(),end="\n\n")

# Features and Target Variable
stock["MA20"] = stock["Close"].rolling(20).mean()
stock["MA50"] = stock["Close"].rolling(50).mean()
stock["Return"] = stock["Close"].pct_change()
stock["Target"] = stock["Return"].shift(-1)

# Visualization of Closing Price and Moving Averages
plt.figure(figsize=(12,6))
plt.plot(stock.index, stock["Close"], label="Closing Price")
plt.plot(stock.index, stock["MA20"], label="20-Day Moving Average", color="orange")
plt.plot(stock.index, stock["MA50"], label="50-Day Moving Average", color="green")
plt.title("NVIDIA Stock Price with 20-Day and 50-Day Moving Averages")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)
plt.show()
 
#cleaning dta
stock.dropna(inplace=True)

# Prepare data for modeling
X = stock[["Open","High","Low","Volume","MA20","MA50","Return"]].dropna()
y = stock["Close"].shift(-1).dropna()

X = X.iloc[:-1] 

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2)

#Random Forest Regression
model = RandomForestRegressor(n_estimators=400, random_state=42,max_depth=10)
model.fit(X_train, y_train)
prediction = model.predict(X_test)


rmse = np.sqrt(mean_squared_error(y_test, prediction))
r2 = r2_score(y_test, prediction)
print(f"R2 Score: {r2:.3f}")
print(f"Root Mean Squared Error: ${rmse:.2f}")
print(f"Next day predicted closing price: ${prediction[-1]:.2f}")

plt.figure(figsize=(12,6))
plt.plot(y_test.values, label="Actual Price")
plt.plot(prediction, label="Predicted Price")
plt.title("Actual vs Predicted Stock Price")
plt.xlabel("Days")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.show()
