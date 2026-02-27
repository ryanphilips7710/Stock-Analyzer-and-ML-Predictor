
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import app_v3_style


st.set_page_config(page_title="Stock ML Predictor Pro",layout="wide",initial_sidebar_state="expanded")
with st.sidebar:
    st.markdown('<div class="sidebar-section-title">Configuration</div>',unsafe_allow_html=True)
    ticker = st.text_input("Stock Ticker", "NVDA").upper().strip()
    years  = st.slider("Historical Data (Years)", 1, 5, 2)
    st.markdown("---")
    market_info_slot = st.empty()


st.markdown(app_v3_style.CSS, unsafe_allow_html=True)

MARKET_HOURS = {
    "NMS": ("09:30 AM", "04:00 PM"),
    "NYQ": ("09:30 AM", "04:00 PM"),
    "NSI": ("09:15 AM", "03:30 PM"),
    "BSE": ("09:15 AM", "03:30 PM"),
}
CURRENCY_SYMBOLS = {"USD": "$", "INR": "₹", "EUR": "€", "GBP": "£", "JPY": "¥"}
FEATURES = ["Lag1", "Lag2", "Lag3", "MA20", "MA50", "Open", "High", "Low", "Volume"]

_PLOT_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="#0a0e1a",
    plot_bgcolor="#0a0e1a",
    font=dict(family="Inter, sans-serif", color="#5a6a8a", size=10),
    margin=dict(l=8, r=8, t=36, b=8),
    legend=dict( bgcolor="rgba(15,22,41,0.9)", bordercolor="#1e2d50", borderwidth=1,
        font=dict(size=10), orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,),
    hoverlabel=dict(bgcolor="#0f1629", bordercolor="#1e2d50", font=dict(family="Inter", size=11)))

_AX  = dict(gridcolor="#111827", zeroline=False, linecolor="#1e2d50",
            tickcolor="#1e2d50", tickfont=dict(size=9))
_XAX = dict(**_AX, rangeslider=dict(visible=False))


def plot_layout(**kw): return {**_PLOT_BASE, **kw}
def ax(**kw): return {**_AX, **kw}
def xax(**kw): return {**_XAX, **kw}


# ──────────────────────────────────────────────────────────────
#CACHED DATA FETCHING
# ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_info(ticker: str) -> dict:
    info = yf.Ticker(ticker).info
    exchange = info.get("exchange", "N/A")
    open_t, close_t = MARKET_HOURS.get(exchange, ("N/A", "N/A"))
    return dict(exchange=exchange,
        timezone=info.get("exchangeTimezoneName", "N/A"),
        currency=info.get("currency", "USD"),
        name=info.get("longName", ticker),
        sector=info.get("sector", "—"),
        mktcap=info.get("marketCap"),
        pe=info.get("trailingPE"),
        open_t=open_t, close_t=close_t)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_prices(ticker: str, years: int) -> pd.DataFrame | None:
    df = yf.download(ticker, period=f"{years}y", interval="1d", auto_adjust=True, progress=False)
    if df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


# ──────────────────────────────────────────────────────────────
#  INDICATOR CALCULATIONS
# ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def build_features(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    s = df["Close"]

    df["Return"] = s.pct_change()
    df["MA20"] = s.rolling(20).mean()
    df["MA50"] = s.rolling(50).mean()

    high, low, prev_c = df["High"], df["Low"], df["Close"].shift(1)
    tr = pd.concat([high - low, (high - prev_c).abs(), (low - prev_c).abs()], axis=1).max(axis=1)
    df["ATR14"] = tr.rolling(14).mean()

    delta = s.diff()
    gain  = delta.clip(lower=0)
    loss  = (-delta).clip(lower=0)
    df["RSI"] = 100 - 100 / (
        1 + gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        /  loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean())

    ema12= s.ewm(span=12, adjust=False).mean()
    ema26= s.ewm(span=26, adjust=False).mean()
    df["MACD"]  = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["Histogram"] = df["MACD"] - df["Signal"]

    m, sig = df["MACD"], df["Signal"]
    df["Bullish"] = (m.shift(1) < sig.shift(1)) & (m > sig)
    df["Bearish"] = (m.shift(1) > sig.shift(1)) & (m < sig)

    for i in range(1, 4):
        df[f"Lag{i}"] = df["Return"].shift(i)

    df["Target"] = df["Return"].shift(-1)
    return df.dropna()


# ──────────────────────────────────────────────────────────────
#  MODEL
# ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def train_rf(train_hash: int, X: np.ndarray, y: np.ndarray) -> RandomForestRegressor:
    rf = RandomForestRegressor(n_estimators=400, max_depth=10, min_samples_leaf=10,
        random_state=42, n_jobs=-1)
    rf.fit(X, y)
    return rf

#==========Load and process
with st.spinner(""):
    raw = fetch_prices(ticker, years)
    info = fetch_info(ticker)

if raw is None or raw.empty:
    st.error(f"No price data found for **{ticker}**.")
    st.stop()

stock = build_features(raw)
currency = info["currency"]
cur_sym = CURRENCY_SYMBOLS.get(currency, currency)
mktcap = info["mktcap"]
cap_str = (f"{cur_sym}{mktcap/1e12:.2f}T" if mktcap and mktcap > 1e12
            else f"{cur_sym}{mktcap/1e9:.1f}B" if mktcap else "—")

# Fill sidebar market info
with market_info_slot.container():
    pe_str = f"{info['pe']:.1f}" if info['pe'] else "—"
    st.markdown(f"""
<div class="sidebar-section-title" style="margin-top:8px;">Market Info</div>
<div class="market-info-card">
  <div class="ticker-name-block">
    <strong>{ticker}</strong> <span>— {info['name']}</span>
  </div>
  <div class="market-info-row"><span class="label">Exchange:</span><span class="value">{info['exchange']}</span></div>
  <div class="market-info-row"><span class="label">Currency:</span><span class="value">{currency}</span></div>
  <div class="market-info-row"><span class="label">Sector:</span><span class="value">{info['sector']}</span></div>
  <div class="market-info-row"><span class="label">Timezone:</span><span class="value">{info['timezone']}</span></div>
  <div class="market-info-row"><span class="label">Hours:</span><span class="value">{info['open_t']} – {info['close_t']}</span></div>
  <div class="market-cap-block">
    <div class="market-cap-label">Market Cap</div>
    <div class="market-cap-value">{cap_str}</div>
  </div>
  <div class="pe-block">
    <div class="market-cap-label">P/E Ratio</div>
    <div class="market-cap-value">{pe_str}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── ML ────────────────────────────────────────────────────────
X = stock[FEATURES].values
y = stock["Target"].values
split = int(len(X) * 0.8)
X_tr, X_te = X[:split], X[split:]
y_tr, y_te = y[:split], y[split:]

model = train_rf(hash((ticker, years, X_tr.shape[0])), X_tr, y_tr)
pred_returns = model.predict(X_te)
rmse = np.sqrt(mean_squared_error(y_te, pred_returns))
r2 = r2_score(y_te, pred_returns)

last_close = float(stock["Close"].iloc[-1])
prev_close = float(stock["Close"].iloc[-2])
day_chg_pct= (last_close - prev_close) / prev_close * 100
latest_pred_ret = float(model.predict(X[[-1]])[0])
next_price = last_close * (1 + latest_pred_ret)
pred_pct = latest_pred_ret * 100
prev_ret_pct = float(stock["Return"].iloc[-1]) * 100

rsi_now = float(stock["RSI"].iloc[-1])
atr_now = float(stock["ATR14"].iloc[-1])


#Header
chg_color  = "#00d4aa" if day_chg_pct >= 0 else "#ff4d6d"
chg_arrow  = "▲" if day_chg_pct >= 0 else "▼"
pred_color = "#00d4aa" if pred_pct >= 0 else "#ff4d6d"
pred_arrow = "▲" if pred_pct >= 0 else "▼"

st.markdown(f"""
<div class="main-header">
  <div>
    <span class="company-name">{info['name']}</span>
    <span class="ticker-badge">{ticker}</span>
  </div>
  <div class="price-row">
    <span class="current-price">{cur_sym}{last_close:,.2f}</span>
    <span class="price-change" style="color:{chg_color};">{chg_arrow} {abs(day_chg_pct):.2f}%</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI strip ─────────────────────────────────────────────────
rsi_badge_cls = "overbought" if rsi_now > 70 else ("oversold" if rsi_now < 30 else "neutral")
rsi_badge_txt = "Overbought" if rsi_now > 70 else ("Oversold" if rsi_now < 30 else "Neutral")
pred_badge_cls = "forecast-up" if pred_pct > 0.15 else ("forecast-down" if pred_pct < -0.15 else "forecast-neut")

st.markdown(f"""
<div class="kpi-bar">
  <div class="kpi-item">
    <div class="kpi-label">Last Close</div>
    <div class="kpi-value">{cur_sym}{last_close:,.2f}</div>
  </div>
  <div class="kpi-item">
    <div class="kpi-label">RSI</div>
    <div class="kpi-value">{rsi_now:.1f}</div>
    <div><span class="kpi-badge {rsi_badge_cls}">↑ {rsi_badge_txt}</span></div>
  </div>
  <div class="kpi-item">
    <div class="kpi-label">ATR (14)</div>
    <div class="kpi-value">{cur_sym}{atr_now:.2f}</div>
  </div>
  <div class="kpi-item">
    <div class="kpi-label">Model R²</div>
    <div class="kpi-value">{r2:.3f}</div>
    <div><span class="kpi-badge rmse">↑ RMSE {rmse*100:.2f}%</span></div>
  </div>
  <div class="kpi-item">
    <div class="kpi-label">Tomorrow Forecast</div>
    <div class="kpi-value">{cur_sym}{next_price:,.2f}</div>
    <div><span class="kpi-badge {pred_badge_cls}">{pred_arrow} {pred_pct:+.2f}%</span></div>
  </div>
</div>
""", unsafe_allow_html=True)


t1, t2, t3, t4 = st.tabs(["📈 Price & Volume", "📊 Indicators", "🤖 ML Forecast", "📋 Data"])
# ─── TAB 1 · PRICE ───────────────────────────────────────────
with t1:
    toggle_col, _ = st.columns([2, 6])
    with toggle_col:
        chart_type = st.radio("", ["Line + MAs", "Candlestick"], horizontal=True)

    vol_colors = [ "#00d4aa" if c >= o else "#ff4d6d"
        for c, o in zip(stock["Close"], stock["Open"])]

    fig_p = make_subplots(rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.75, 0.25], vertical_spacing=0.025)

    def add_trace_p(trace):
        fig_p.add_trace(trace, row=1, col=1)

    if chart_type == "Candlestick":
        add_trace_p(go.Candlestick(
            x=stock.index,
            open=stock["Open"], high=stock["High"],
            low=stock["Low"],   close=stock["Close"],
            increasing=dict(line=dict(color="#00d4aa", width=1), fillcolor="#00d4aa"),
            decreasing=dict(line=dict(color="#ff4d6d", width=1), fillcolor="#ff4d6d"),
            name="OHLC"))
    else:
        add_trace_p(go.Scatter(
            x=stock.index, y=stock["Close"],
            name="Close", line=dict(color="#4a9eff", width=1.8),
            fill="tozeroy", fillcolor="rgba(74,158,255,0.05)"))

    add_trace_p(go.Scatter(x=stock.index, y=stock["MA20"], name="MA 20",
        line=dict(color="#00d4aa", width=1, dash="dot")))
    add_trace_p(go.Scatter(x=stock.index, y=stock["MA50"], name="MA 50",
        line=dict(color="#f5a623", width=1, dash="dash")))

    fig_p.add_trace(go.Bar(x=stock.index, y=stock["Volume"], name="Volume", marker_color=vol_colors,
        marker_line_width=0, opacity=0.65,), row=2, col=1)
    
    fig_p.update_layout(**plot_layout(height=560, title=None),
        xaxis=dict(**xax()), xaxis2=dict(**xax()),
        yaxis=dict(**ax(), title=f"Price ({currency})"),
        yaxis2=dict(**ax(), title="Volume"))

    st.plotly_chart(fig_p, use_container_width=True)

# ─── TAB 2 · INDICATORS ──────────────────────────────────────
with t2:
    hist_colors = ["#00d4aa" if h >= 0 else "#ff4d6d" for h in stock["Histogram"]]

    left, right = st.columns(2)
    with left:
        st.markdown('<div class="section-label">RSI · 14-period</div>', unsafe_allow_html=True)
        fig_rsi = go.Figure()
        fig_rsi.add_hrect(y0=70, y1=100, fillcolor="rgba(255,77,109,.05)",  line_width=0)
        fig_rsi.add_hrect(y0=0,  y1=30,  fillcolor="rgba(0,212,170,.05)", line_width=0)
        fig_rsi.add_trace(go.Scatter(x=stock.index, y=stock["RSI"],
            line=dict(color="#4a9eff", width=1.6), name="RSI"))
        fig_rsi.add_hline(y=70, line_dash="dot", line_color="#ff4d6d", opacity=.5,
                          annotation_text="70", annotation_font_size=9)
        fig_rsi.add_hline(y=30, line_dash="dot", line_color="#00d4aa", opacity=.5,
                          annotation_text="30", annotation_font_size=9)
        fig_rsi.add_hline(y=50, line_dash="dot", line_color="#1e2d50", opacity=.8)
        fig_rsi.update_layout(**plot_layout(height=240, showlegend=False),
                               xaxis=dict(**xax()), yaxis=dict(**ax(), range=[0, 100]))
        st.plotly_chart(fig_rsi, use_container_width=True)

    with right:
        st.markdown('<div class="section-label">MACD Histogram</div>', unsafe_allow_html=True)
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Bar(x=stock.index, y=stock["Histogram"],
            marker_color=hist_colors, marker_line_width=0, opacity=.85))
        fig_hist.update_layout(**plot_layout(height=240, showlegend=False),
                                xaxis=dict(**xax()), yaxis=dict(**ax()))
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown('<div class="section-label">MACD · Signal · Crossovers</div>', unsafe_allow_html=True)
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Bar(x=stock.index, y=stock["Histogram"],
        marker_color=hist_colors, marker_line_width=0, opacity=.4, name="Histogram"))
    fig_macd.add_trace(go.Scatter(x=stock.index, y=stock["MACD"],
        line=dict(color="#4a9eff", width=1.4), name="MACD"))
    fig_macd.add_trace(go.Scatter(x=stock.index, y=stock["Signal"],
        line=dict(color="#f5a623", width=1.2, dash="dash"), name="Signal"))
    fig_macd.add_trace(go.Scatter(
        x=stock.index[stock["Bullish"]], y=stock.loc[stock["Bullish"], "MACD"],
        mode="markers", name="Bullish",
        marker=dict(symbol="triangle-up", size=9, color="#00d4aa", line=dict(width=0))))
    fig_macd.add_trace(go.Scatter(
        x=stock.index[stock["Bearish"]], y=stock.loc[stock["Bearish"], "MACD"],
        mode="markers", name="Bearish",
        marker=dict(symbol="triangle-down", size=9, color="#ff4d6d", line=dict(width=0))))
    fig_macd.update_layout(**plot_layout(height=320), xaxis=dict(**xax()), yaxis=dict(**ax()))
    st.plotly_chart(fig_macd, use_container_width=True)

# ─── TAB 3 · ML FORECAST ─────────────────────────────────────
with t3:
    bull = pred_pct > 0.15
    bear = pred_pct < -0.15
    card_cls  = "bull" if bull else ("bear" if bear else "")
    badge_cls = "bull" if bull else ("bear" if bear else "neut")
    badge_txt = "BULLISH" if bull else ("BEARISH" if bear else "NEUTRAL")
    ret_color  = "#00d4aa" if pred_pct >= 0 else "#ff4d6d"
    prev_color = "#00d4aa" if prev_ret_pct >= 0 else "#ff4d6d"

    vol_20 = float(stock["Return"].tail(20).std()) * last_close
    ci_low  = next_price - 1.645 * vol_20
    ci_high = next_price + 1.645 * vol_20

    st.markdown(f"""
<div class="pred-grid">
  <div class="pred-card">
    <div class="pred-card-label">Last Close</div>
    <div class="pred-card-value">{cur_sym}{last_close:,.2f}</div>
    <div class="pred-card-sub" style="color:{prev_color};">Yesterday &nbsp;{prev_ret_pct:+.2f}%</div>
  </div>
  <div class="pred-card {card_cls}">
    <div class="pred-card-label">Tomorrow Forecast</div>
    <div class="pred-card-value" style="color:{ret_color};">{cur_sym}{next_price:,.2f}</div>
    <div class="pred-card-sub" style="color:{ret_color};">{pred_pct:+.2f}%</div>
    <div>
      <span class="signal-badge {badge_cls}">
        <span class="signal-dot {badge_cls}"></span>
        {badge_txt}
      </span>
    </div>
  </div>
  <div class="pred-card">
    <div class="pred-card-label">90% CI Range</div>
    <div class="ci-range">{cur_sym}{ci_low:,.2f} – {cur_sym}{ci_high:,.2f}</div>
    <div class="ci-sub">Based on 20-day volatility</div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Actual vs Predicted returns · Test set</div>', unsafe_allow_html=True)

    test_idx = stock.index[-len(y_te):]
    fig_pred = go.Figure()
    fig_pred.add_trace(go.Scatter(x=test_idx, y=y_te * 100,
        name="Actual", line=dict(color="#5a6a8a", width=1.2)))
    fig_pred.add_trace(go.Scatter(x=test_idx, y=pred_returns * 100,
        name="Predicted", line=dict(color="#4a9eff", width=1.6),
        fill="tonexty", fillcolor="rgba(74,158,255,0.04)"))
    fig_pred.add_annotation(
        xref="paper", yref="paper", x=0.99, y=0.96, showarrow=False,
        text=f"{'▲' if pred_pct>=0 else '▼'} {pred_pct:+.2f}% tomorrow",
        font=dict(color=ret_color, size=12, family="Space Grotesk"), align="right")
    fig_pred.update_layout(**plot_layout(height=380),
        xaxis=dict(**xax()), yaxis=dict(**ax(), title="Return (%)"))
    st.plotly_chart(fig_pred, use_container_width=True)

    col_a, col_b = st.columns(2)
    prev_arr = "▲" if prev_ret_pct >= 0 else "▼"
    pred_arr = "▲" if pred_pct >= 0 else "▼"
    col_a.markdown(
        f'<div><span style="font-size:10px;letter-spacing:.1em;color:#5a6a8a;text-transform:uppercase;">Yesterday Return</span><br>'
        f'<span style="color:{prev_color};font-size:28px;font-weight:700;font-family:Space Grotesk,sans-serif;">{prev_arr} {abs(prev_ret_pct):.2f}%</span></div>',
        unsafe_allow_html=True)
    col_b.markdown(
        f'<div><span style="font-size:10px;letter-spacing:.1em;color:#5a6a8a;text-transform:uppercase;">Predicted Return</span><br>'
        f'<span style="color:{ret_color};font-size:28px;font-weight:700;font-family:Space Grotesk,sans-serif;">{pred_arr} {abs(pred_pct):.2f}%</span></div>',
        unsafe_allow_html=True)


# ─── TAB 4 · DATA ────────────────────────────────────────────
with t4:
    st.markdown('<div class="section-label">Recent price data · last 60 sessions</div>', unsafe_allow_html=True)
    cols_show = ["Open", "High", "Low", "Close", "Volume", "Return", "RSI"]

    display = (stock[cols_show].tail(60).iloc[::-1].style
        .format({
            "Open": f"{cur_sym}{{:.2f}}", "High": f"{cur_sym}{{:.2f}}",
            "Low":  f"{cur_sym}{{:.2f}}", "Close": f"{cur_sym}{{:.2f}}",
            "Volume": "{:,.0f}", "Return": "{:+.3%}",
            "RSI": "{:.1f}", "MACD": "{:.4f}", "Signal": "{:.4f}"})
        .background_gradient(subset=["Return"], cmap="RdYlGn", vmin=-.03, vmax=.03))
    
    st.dataframe(display, use_container_width=True, height=480)
    st.download_button( label="↓ Download CSV",
        data=stock[cols_show].to_csv().encode(),
        file_name=f"{ticker}_data.csv", mime="text/csv")