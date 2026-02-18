# 📈 Stock Analyzer & Price Predictor using Machine Learning

A real-time stock analysis and next-day price prediction web application built using **Python, Streamlit, and Machine Learning**. The app fetches live market data, performs technical analysis, trains an ML model, and predicts the upcoming stock price.

---

## 🚀 Features

* 📊 Live stock data from Yahoo Finance
* 📈 Technical indicators (Moving Averages, Returns)
* 🤖 Machine Learning price prediction (Random Forest)
* 📉 Actual vs Predicted visualization
* 📐 Model performance metrics (RMSE & R²)
* 🖥️ Interactive web UI with Streamlit
* 🔮 Next-day stock price forecast

---

https://github.com/user-attachments/assets/3d826474-fbb4-4f75-80c1-4cffae5f996f

## 🛠️ Tech Stack

| Layer            | Tools                   |
| ---------------- | ----------------------- |
| Data             | Pandas, NumPy, yFinance |
| Visualization    | Matplotlib              |
| Machine Learning | Scikit-Learn            |
| UI               | Streamlit               |

---

## 📂 Project Structure

```
Stock-Analyzer/
│
├── app.v1.py
├── app.v2.py
├── README.md
└── requirements.txt
```

---

## 📊 Machine Learning Workflow

1. Fetch historical stock data
2. Feature engineering (MA20, MA50, Returns)
3. Time-series train/test split
4. Random Forest model training
5. Performance evaluation
6. Next-day price prediction

---

## 📈 Model Used

**Random Forest Regressor**

Why?

* Handles noisy stock data well
* Captures nonlinear market patterns
* Robust against overfitting

---

## 📐 Evaluation Metrics

* **RMSE** — prediction error magnitude
* **R² Score** — model performance strength

---

## ▶️ How to Run

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Run the application

```bash
streamlit run app.py
```

---

## 📌 Example Usage

* Enter stock ticker (e.g., `NVDA`, `AAPL`, `TSLA`)
* View live price trends
* Analyze technical indicators
* Get next-day predicted closing price

---

## ⚠️ Disclaimer

This project is for educational purposes only.
Stock predictions are not financial advice.

---

## 🌟 Future Improvements

* Deep Learning (LSTM) models
* Portfolio tracking
* Real-time prediction updates
* Cloud deployment


## 📄 License

This project is licensed under the MIT License.
You are free to use, modify, and distribute it with attribution.



