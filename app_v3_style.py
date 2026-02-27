CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
  --bg:        #0a0e1a;
  --surface:   #0f1629;
  --surface2:  #141c33;
  --border:    #1e2d50;
  --blue:      #4a9eff;
  --blue-dim:  #1a3a6e;
  --green:     #00d4aa;
  --red:       #ff4d6d;
  --text:      #e2e8f8;
  --muted:     #5a6a8a;
  --font:      'Inter', sans-serif;
  --font-head: 'Space Grotesk', sans-serif;
}

html, body, [class*="css"] { font-family: var(--font); }
.stApp { background: var(--bg); color: var(--text); }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1500px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--surface);
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }

.sidebar-section-title {
  font-family: var(--font-head);
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.sidebar-section-title::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 18px;
  background: var(--blue);
  border-radius: 2px;
}

.market-info-card {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  margin-top: 8px;
}
.ticker-name-block {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}
.ticker-name-block span { color: var(--muted); font-weight: 400; }
.market-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 7px;
  font-size: 12px;
}
.market-info-row .label { color: var(--muted); font-weight: 500; }
.market-info-row .value { color: var(--text); font-weight: 600; }
.market-cap-block {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.market-cap-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--muted);
  margin-bottom: 4px;
}
.market-cap-value {
  font-family: var(--font-head);
  font-size: 26px;
  font-weight: 700;
  color: var(--text);
}
.pe-block {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

/* ── Inputs ── */
.stTextInput label {
  font-size: 12px !important;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--muted) !important;
  font-weight: 500;
}
input[type="text"], .stTextInput input {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--blue) !important;
  font-family: var(--font-head) !important;
  font-size: 16px !important;
  font-weight: 600;
  letter-spacing: .06em;
}
input[type="text"]:focus { border-color: var(--blue) !important; box-shadow: 0 0 0 2px rgba(74,158,255,.2) !important; }

.stSlider label {
  font-size: 12px !important;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--muted) !important;
}

/* ── Tabs ── */
[data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border);
  gap: 0;
}
button[data-baseweb="tab"] {
  font-family: var(--font) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  color: var(--muted) !important;
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  padding: 12px 24px !important;
  transition: all .15s !important;
}
button[data-baseweb="tab"]:hover { color: var(--text) !important; }
button[data-baseweb="tab"][aria-selected="true"] {
  color: var(--blue) !important;
  border-bottom-color: var(--blue) !important;
}
[data-baseweb="tab-highlight"] { display: none !important; }
[data-baseweb="tab-border"]    { display: none !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { font-size: 12px !important; border-radius: 10px; overflow: hidden; }

.stSuccess { background: #071a14 !important; border-left-color: var(--green) !important; border-radius: 8px !important; }
.stError   { background: #1a0710 !important; border-left-color: var(--red)   !important; border-radius: 8px !important; }

hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

.section-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .12em;
  color: var(--muted);
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

/* ── Main header ── */
.main-header { padding: 16px 0 8px; margin-bottom: 4px; }
.company-name {
  font-family: var(--font-head);
  font-size: 36px;
  font-weight: 700;
  color: var(--text);
  display: inline;
}
.ticker-badge {
  font-family: var(--font-head);
  font-size: 22px;
  font-weight: 600;
  color: var(--blue);
  margin-left: 12px;
}
.price-row { display: flex; align-items: center; gap: 16px; margin-top: 10px; margin-bottom: 6px; }
.current-price { font-family: var(--font-head); font-size: 34px; font-weight: 700; color: var(--text); }
.price-change { font-size: 17px; font-weight: 500; display: flex; align-items: center; gap: 4px; }

/* ── KPI bar ── */
.kpi-bar {
  display: flex;
  gap: 24px;
  padding: 16px 0;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  margin: 12px 0 20px;
  flex-wrap: wrap;
}
.kpi-item { flex: 1; min-width: 120px; }
.kpi-label { font-size: 11px; text-transform: uppercase; letter-spacing: .1em; color: var(--muted); margin-bottom: 4px; }
.kpi-value { font-family: var(--font-head); font-size: 22px; font-weight: 700; color: var(--text); }
.kpi-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .06em;
  padding: 3px 10px;
  border-radius: 20px;
  margin-top: 4px;
}
.kpi-badge.neutral  { background: rgba(0,212,170,.12); color: var(--green); }
.kpi-badge.overbought { background: rgba(255,77,109,.12); color: var(--red); }
.kpi-badge.oversold { background: rgba(74,158,255,.12); color: var(--blue); }
.kpi-badge.rmse { background: rgba(0,212,170,.12); color: var(--green); }
.kpi-badge.forecast-up   { background: rgba(0,212,170,.12); color: var(--green); }
.kpi-badge.forecast-down { background: rgba(255,77,109,.12); color: var(--red); }
.kpi-badge.forecast-neut { background: rgba(245,166,35,.12); color: #f5a623; }

/* ── Prediction cards ── */
.pred-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.pred-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px 24px;
}
.pred-card.bull { border-color: rgba(0,212,170,.3); }
.pred-card.bear { border-color: rgba(255,77,109,.3); }
.pred-card-label { font-size: 10px; text-transform: uppercase; letter-spacing: .12em; color: var(--muted); margin-bottom: 10px; }
.pred-card-value { font-family: var(--font-head); font-size: 32px; font-weight: 700; color: var(--text); }
.pred-card-sub { font-size: 13px; margin-top: 6px; }
.signal-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .1em;
  padding: 5px 14px;
  border-radius: 20px;
  margin-top: 10px;
}
.signal-badge.bull { background: rgba(0,212,170,.1); color: var(--green); border: 1px solid rgba(0,212,170,.3); }
.signal-badge.bear { background: rgba(255,77,109,.1); color: var(--red);   border: 1px solid rgba(255,77,109,.3); }
.signal-badge.neut { background: rgba(245,166,35,.1); color: #f5a623;      border: 1px solid rgba(245,166,35,.3); }
.signal-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.signal-dot.bull { background: var(--green); }
.signal-dot.bear { background: var(--red); }
.signal-dot.neut { background: #f5a623; }
.ci-range { font-family: var(--font-head); font-size: 20px; font-weight: 600; color: var(--text); margin-top: 4px; }
.ci-sub { font-size: 11px; color: var(--muted); margin-top: 6px; }

/* Model info card */
.model-info-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px 24px;
}
.model-info-title {
  font-family: var(--font-head);
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}
.model-info-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px; }
.model-info-row .ml { color: var(--muted); }
.model-info-row .mv { color: var(--text); font-weight: 500; }

.stCheckbox label { font-size: 13px !important; color: var(--text) !important; }
</style>
"""
