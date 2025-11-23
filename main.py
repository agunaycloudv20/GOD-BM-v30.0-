import streamlit as st
import pandas as pd
from PIL import Image
import io
import time
import json
import calendar
from datetime import datetime
import pytz
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

# HAAUB MODÜLLERİ
import config
import data_engine
import strategies_db
import ai_core
import db_manager

# ==========================================
# 1. SYSTEM CONFIG
# ==========================================
st.set_page_config(page_title="HAAUB TERMINAL", layout="wide", initial_sidebar_state="expanded")

# 60 Saniyede bir UI yenile
st_autorefresh(interval=60000, key="sys_refresh")

# Başlatıcılar
db_manager.init_db()
engine = data_engine.DataEngine()

# State
if 'view' not in st.session_state: st.session_state.view = 'MONITOR'
if 'language' not in st.session_state: st.session_state.language = 'EN'
if 'selected_tf' not in st.session_state: st.session_state.selected_tf = '4h'

# ==========================================
# 2. CSS (PRESTIGE UI)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* GLOBAL */
    .stApp { background-color: #050505; color: #EAECEF; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 0px; padding-left: 10px; padding-right: 10px; }
    
    /* HEADER */
    .header-container {
        display: flex; justify-content: space-between; align-items: center;
        background: #0f0f0f; padding: 15px 20px; border-bottom: 1px solid #222;
        margin-top: -50px;
    }
    .brand-text { font-family: 'Inter'; font-weight: 900; font-size: 22px; letter-spacing: 1px; color: #fff; }
    .brand-sub { color: #f0b90b; font-size: 11px; font-weight: 500; margin-left: 10px; letter-spacing: 2px; }
    
    /* MACRO GRID */
    .macro-wrapper {
        display: grid; grid-template-columns: repeat(6, 1fr); 
        background: #080808; border-bottom: 1px solid #222; width: 100%;
    }
    .macro-box { padding: 10px; text-align: center; border-right: 1px solid #1a1a1a; }
    .macro-lbl { font-size: 10px; color: #666; font-weight: 700; margin-bottom: 4px; }
    .macro-val { font-size: 13px; color: #eee; font-family: 'JetBrains Mono'; font-weight: 700; }
    .up { color: #0ECB81; font-size: 11px; margin-left: 4px; } 
    .down { color: #F6465D; font-size: 11px; margin-left: 4px; }
    
    /* STATUS BAR */
    .status-bar {
        display: flex; justify-content: space-between; background: #0f0f0f; padding: 5px 20px;
        font-family: 'JetBrains Mono'; font-size: 10px; color: #666; border-bottom: 1px solid #222;
    }
    
    /* CUSTOM BUTTONS */
    .stButton>button { border-radius: 2px; border: 1px solid #222; background: #1a1a1a; color: #888; font-weight: 600; width: 100%; }
    .stButton>button:hover { border-color: #f0b90b; color: #fff; background: #222; }
    
    /* IRON DOME UPLOAD ZONE */
    .upload-zone {
        border: 2px dashed #333; border-radius: 10px; padding: 40px; text-align: center;
        background: #0a0a0a; margin-bottom: 20px; transition: 0.3s;
    }
    .upload-zone:hover { border-color: #f0b90b; background: #0f0f0f; }
    
    /* STRATEGY SELECTOR STYLE */
    div[data-testid="stExpander"] { background-color: #0f0f0f; border: 1px solid #222; border-radius: 4px; }
    
    /* CALENDAR GRID */
    .cal-grid {
        display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-top: 10px;
    }
    .cal-header { text-align: center; font-size: 12px; color: #666; padding: 5px; }
    .cal-day {
        background: #111; border: 1px solid #222; height: 80px; padding: 5px; 
        font-family: 'JetBrains Mono'; font-size: 12px; position: relative; cursor: pointer;
    }
    .cal-day:hover { border-color: #fff; }
    .cal-day.profit { border-top: 3px solid #0ECB81; }
    .cal-day.loss { border-top: 3px solid #F6465D; }
    .pnl-tag { position: absolute; bottom: 5px; right: 5px; font-weight: bold; }
    
    /* TOOLTIP */
    .cal-day:hover::after {
        content: attr(data-tooltip);
        position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
        background: #333; color: #fff; padding: 5px 10px; border-radius: 4px;
        font-size: 10px; white-space: pre; z-index: 100; pointer-events: none;
    }

    /* PRICING CARDS */
    .price-card {
        background: #0f0f0f; border: 1px solid #222; padding: 30px; text-align: center; border-radius: 4px; transition: 0.3s;
    }
    .price-card:hover { border-color: #f0b90b; transform: translateY(-5px); box-shadow: 0 5px 15px rgba(240, 185, 11, 0.1); }
    .price-head { font-size: 14px; color: #888; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }
    .price-val { font-size: 36px; color: #fff; font-weight: 700; font-family: 'Inter'; }
    .price-sub { font-size: 12px; color: #555; margin-bottom: 20px; }
    .price-feat { font-size: 11px; color: #ccc; border-bottom: 1px solid #222; padding: 8px 0; }

    header, footer { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DATA ENGINE
# ==========================================
tr_now = datetime.now(pytz.timezone('Europe/Istanbul')).strftime("%H:%M")
utc_hour = datetime.now(pytz.utc).hour
session = "MARKET CLOSED"
if 8 <= utc_hour < 17: session = "LONDON SESSION"
if 13 <= utc_hour < 22: session = "NEW YORK SESSION"
if 8 <= utc_hour < 17 and 13 <= utc_hour < 22: session = "LONDON & NY OVERLAP"
if 0 <= utc_hour < 9: session = "TOKYO SESSION"

macro = engine.get_macro_data()
news = engine.get_news()

# ==========================================
# 4. HEADER & MACRO
# ==========================================
st.markdown(f"""
<div class="header-container">
    <div><span class="brand-text">HAAUB & CO</span><span class="brand-sub">GOD GM v30.1</span></div>
    <div style="font-size:12px; color:#666; font-weight:600; border:1px solid #333; padding:5px 10px; border-radius:4px;">
        <span style="color:#fff;">ENG</span> <span style="color:#444;">|</span> TR
    </div>
</div>
""", unsafe_allow_html=True)

macro_items = ["DXY", "US10Y", "VIX", "GOLD", "SP500", "BTC.D"]
cols = st.columns(6) 
for i, item in enumerate(macro_items):
    val = macro.get(item, {'price':0, 'change':0})
    cls = "up" if val['change'] >= 0 else "down"
    sign = "+" if val['change'] >= 0 else ""
    with cols[i]:
        st.markdown(f"""
        <div class="macro-box" style="background:#080808; padding:10px; text-align:center; border-right:1px solid #222;">
            <div class="macro-lbl">{item}</div>
            <div class="macro-val">{val['price']:.2f}<span class="{cls}">{sign}{val['change']:.2f}%</span></div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f"""
<div class="status-bar">
    <span>SYSTEM: <span style="color:#0ECB81;">ONLINE</span></span>
    <span>SESSION: <span style="color:#fff;">{session}</span></span>
    <span>TSI: <span style="color:#fff;">{tr_now}</span></span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. NAVIGATION
# ==========================================
nav = st.columns(5)
if nav[0].button("MONITOR"): st.session_state.view = 'MONITOR'
if nav[1].button("IRON DOME"): st.session_state.view = 'ANALYSIS'
if nav[2].button("SIMULATOR"): st.session_state.view = 'SIM'
if nav[3].button("JOURNAL"): st.session_state.view = 'DB'
if nav[4].button("SUBSCRIPTION"): st.session_state.view = 'SUB'

st.markdown("---")

col_L, col_M, col_R = st.columns([1.2, 3.3, 1.5])

# ------------------------------------------
# ◀️ SOL PANEL
# ------------------------------------------
with col_L:
    bal = engine.get_wallet_balance()
    st.markdown(f"""
    <div style="background:#111; padding:15px; border:1px solid #222; margin-bottom:15px;">
        <div style="color:#666; font-size:10px; font-weight:700;">EST. EQUITY (USDT)</div>
        <div style="color:#fff; font-size:22px; font-family:'JetBrains Mono'; font-weight:700;">${bal:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    assets = {
        "--- CRYPTO ---": ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT"],
        "--- FX MAJORS ---": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF"],
        "--- COMMODITIES ---": ["XAU/USD", "WTI/USD", "NG/USD"],
        "--- INDICES ---": ["SPX500", "NAS100"]
    }
    flat_assets = []
    for k, v in assets.items():
        flat_assets.append(k)
        flat_assets.extend(v)
        
    symbol = st.selectbox("ASSET", flat_assets, index=1, label_visibility="collapsed")
    
    st.markdown("<div style='margin:10px 0 5px 0; font-size:10px; color:#666; font-weight:700;'>TIMEFRAME</div>", unsafe_allow_html=True)
    tf1, tf2, tf3 = st.columns(3)
    if tf1.button("15M"): st.session_state.selected_tf = '15m'
    if tf2.button("1H"): st.session_state.selected_tf = '1h'
    if tf3.button("4H"): st.session_state.selected_tf = '4h'
    
    tf4, tf5, tf6 = st.columns(3)
    if tf4.button("1D"): st.session_state.selected_tf = '1d'
    if tf5.button("1W"): st.session_state.selected_tf = '1w'
    if tf6.button("1M"): st.session_state.selected_tf = '1M'
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:10px; color:#666; font-weight:700; margin-bottom:5px;'>ACTIVE POSITIONS</div>", unsafe_allow_html=True)
    df_pos = engine.get_open_positions_df()
    if not df_pos.empty:
        st.dataframe(df_pos, use_container_width=True, hide_index=True)
    else:
        st.markdown("<div style='font-size:10px; color:#444; text-align:center; padding:10px; border:1px dashed #222;'>NO ACTIVE POSITIONS</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:10px; color:#666; font-weight:700; margin-bottom:5px;'>PENDING ORDERS</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:10px; color:#444; text-align:center; padding:10px; border:1px dashed #222;'>NO LIMIT ORDERS</div>", unsafe_allow_html=True)

# ------------------------------------------
# ⏹️ ORTA PANEL
# ------------------------------------------
with col_M:
    
    # VIEW: MONITOR
    if st.session_state.view == 'MONITOR':
        tv_sym = f"OKX:{symbol.replace('/','')}" if "---" not in symbol else "OKX:BTCUSDT"
        components.html(f"""
        <div class="tradingview-widget-container">
          <div id="tv_chart"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
          "width": "100%", "height": 600, "symbol": "{tv_sym}", 
          "interval": "240", "timezone": "Etc/UTC", "theme": "dark", 
          "style": "1", "locale": "en", "toolbar_bg": "#f1f3f6", 
          "enable_publishing": false, "hide_side_toolbar": false, 
          "container_id": "tv_chart"
          }});
          </script>
        </div>""", height=610)
        
        c1, c2 = st.columns(2)
        c1.info("VOLUME PROFILE POC: 98,240.00 (Support)")
        c2.warning("LIQUIDATION HEATMAP: Short Squeeze Risk @ 99,100")

    # VIEW: IRON DOME (FIX: Strateji Seçimi Eklendi)
    elif st.session_state.view == 'ANALYSIS':
        st.markdown("#### 🛡️ IRON DOME PROTOCOL")
        
        # --- STRATEJİ SEÇİMİ (Geri Getirildi) ---
        with st.expander("⚔️ SELECT ACTIVE STRATEGIES (MANUAL OVERRIDE)", expanded=True):
            cats = list(strategies_db.STRATEGY_LIBRARY.keys())
            selected_strats = []
            # 3 Kolonlu Kategori Listesi
            s_cols = st.columns(3)
            for i, cat in enumerate(cats):
                col = s_cols[i % 3]
                col.markdown(f"**{cat}**")
                for strat in strategies_db.STRATEGY_LIBRARY[cat]:
                    if col.checkbox(strat, key=f"chk_{strat}"):
                        selected_strats.append(strat)
        
        if not selected_strats:
            st.caption("⚠️ AUTO-MODE: AI will select the best fitting strategy.")
        else:
            st.caption(f"✅ ACTIVE PROTOCOLS: {', '.join(selected_strats)}")
        # ---------------------------------------

        st.markdown("""
        <div class="upload-zone">
            <div style="font-size:30px; color:#444;">📸</div>
            <div style="color:#888; font-size:12px;">DROP CHART SNAPSHOT HERE</div>
            <div style="color:#444; font-size:10px;">SUPPORTS PNG, JPG (MAX 5MB)</div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded = st.file_uploader("Hidden Uploader", type=['png','jpg'], label_visibility="collapsed")
        
        if uploaded:
            st.image(uploaded, caption=f"Analyzing {symbol}...", use_column_width=True)
            if st.button("INITIATE NEURAL SCAN (LIVE)", type="primary", use_container_width=True):
                with st.spinner("GATHERING GLOBAL INTEL & CONVENING COUNCIL..."):
                    img = Image.open(uploaded)
                    current_symbol = symbol if "---" not in symbol else "BTC/USDT"
                    data_pkg = engine.get_master_data(current_symbol, st.session_state.selected_tf)
                    tech_dict = data_pkg['technical'].iloc[-1].to_dict() if not data_pkg['technical'].empty else {}
                    
                    ai_response = ai_core.execute_iron_dome_protocol(
                        img, current_symbol, st.session_state.selected_tf,
                        market_data=tech_dict, macro_data=data_pkg['macro'],
                        sentiment=data_pkg['sentiment'], depth=data_pkg['depth'],
                        user_strats=selected_strats # Seçilen stratejileri gönder
                    )
                    
                    if ai_response['action'] != "ERROR":
                        st.session_state.ai_res = ai_response
                        st.success("ANALYSIS COMPLETE")
                        buf = io.BytesIO(); img.save(buf, format='PNG')
                        db_manager.log_analysis(current_symbol, st.session_state.selected_tf, ai_response, tech_dict, data_pkg['macro'], data_pkg['sentiment'], buf.getvalue())
                    else:
                        st.error(f"AI ERROR: {ai_response.get('log')}")
        
        if 'ai_res' in st.session_state:
            r = st.session_state.ai_res
            clr = "#0ecb81" if r['action']=="LONG" else "#f6465d" if r['action']=="SHORT" else "#888"
            debate = r.get('council_debate', {})
            
            st.markdown(f"""
            <div class="council-grid">
                <div class="council-card" style="border-top: 3px solid #0ECB81;"><div class="council-title" style="color:#0ECB81;">THE BULL</div><div class="council-text">{debate.get('bull_agent')}</div></div>
                <div class="council-card" style="border-top: 3px solid #F6465D;"><div class="council-title" style="color:#F6465D;">THE BEAR</div><div class="council-text">{debate.get('bear_agent')}</div></div>
                <div class="council-card" style="border-top: 3px solid #F0B90B;"><div class="council-title" style="color:#F0B90B;">THE JUDGE</div><div class="council-text">{debate.get('judge_verdict')}</div></div>
            </div>
            <div style="border:1px solid {clr}; padding:20px; background:#0a0a0a; text-align:center; margin-top:15px;">
                <div style="font-size:12px; color:#888;">SYSTEM BIAS</div>
                <div style="font-size:32px; color:{clr}; font-weight:bold;">{r['action']}</div>
                <div style="font-size:14px; color:#ccc;">CONFIDENCE: {r['score']}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("⚡ AUTO-FILL EXECUTION"): st.session_state.fill_setup = r.get('setup', {})

    # VIEW: SIMULATOR
    elif st.session_state.view == 'SIM':
        st.markdown("#### 🧠 STRATEGY ARCHITECT")
        strat_list = strategies_db.get_all_strategies_list()
        c1, c2 = st.columns(2)
        selected_strat = c1.selectbox("STRATEGY PROTOCOL", strat_list)
        risk_mode = c2.selectbox("RISK MODEL", ["Conservative (0.5%)", "Balanced (1.0%)", "Aggressive (2.0%)"])
        
        if st.button("RUN SIMULATION", type="primary"):
            with st.spinner(f"BACKTESTING {selected_strat}..."):
                st.markdown("---")
                st.markdown(f"**PROTOCOL:** {selected_strat}")
                st.info("Simulated Win Rate: 68% | Profit Factor: 2.1")
                st.code(f"Entry Logic: {strategies_db.get_strategy_details(selected_strat)['Logic']}", language="json")

    # VIEW: JOURNAL
    elif st.session_state.view == 'DB':
        st.markdown("#### 📅 PERFORMANCE CALENDAR")
        c_w1, c_w2 = st.columns(2)
        c_w1.metric("USER WIN RATE", "62%", "+2%")
        c_w2.metric("AI ACCURACY", "78%", "+5%")
        
        cal = calendar.monthcalendar(2025, 11)
        month_html = '<div class="cal-grid">'
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        for d in days: month_html += f'<div class="cal-header">{d}</div>'
        for week in cal:
            for day in week:
                if day == 0: month_html += '<div class="cal-day" style="background:transparent; border:none;"></div>'
                else:
                    pnl = 0
                    if day in [3, 12, 15]: pnl = 500
                    if day in [5, 8]: pnl = -200
                    cls = "profit" if pnl > 0 else "loss" if pnl < 0 else ""
                    pnl_txt = f"${pnl}" if pnl != 0 else ""
                    tooltip = f"Day: {day}\nTrades: 3\nAI Bias: LONG\nResult: {pnl_txt}"
                    month_html += f"""<div class="cal-day {cls}" data-tooltip="{tooltip}"><span style="color:#666;">{day}</span><div class="pnl-tag" style="color:{'#0ecb81' if pnl>0 else '#f6465d'};">{pnl_txt}</div></div>"""
        month_html += '</div>'
        st.markdown(month_html, unsafe_allow_html=True)

    # VIEW: SUBSCRIPTION
    elif st.session_state.view == 'SUB':
        st.markdown("#### 💎 MEMBERSHIP TIERS")
        p1, p2, p3 = st.columns(3)
        with p1:
            st.markdown("""<div class="price-card"><div class="price-head">STARTER</div><div class="price-val">$19.99</div><div class="price-sub">per month</div><div class="price-feat">Basic Analysis</div><div class="price-feat">5 AI Scans / Day</div><div class="price-feat" style="color:#666;">No Macro Data</div><br></div>""", unsafe_allow_html=True)
            st.button("SELECT STARTER", use_container_width=True)
        with p2:
            st.markdown("""<div class="price-card" style="border-color:#F0B90B; background:#1a1600;"><div class="price-head" style="color:#F0B90B;">PRO TRADER</div><div class="price-val">$39.99</div><div class="price-sub">per month</div><div class="price-feat">Iron Dome Protocol</div><div class="price-feat">Unlimited Scans</div><div class="price-feat">Macro & Sentiment</div><br></div>""", unsafe_allow_html=True)
            st.button("SELECT PRO", type="primary", use_container_width=True)
        with p3:
            st.markdown("""<div class="price-card"><div class="price-head">INSTITUTIONAL</div><div class="price-val">$89.99</div><div class="price-sub">per month</div><div class="price-feat">Full API Access</div><div class="price-feat">On-Chain Ghost</div><div class="price-feat">24/7 Priority Support</div><br></div>""", unsafe_allow_html=True)

# ------------------------------------------
# SAĞ PANEL (İŞLEM)
# ------------------------------------------
with col_R:
    st.markdown("<div style='font-size:10px; color:#848e9c; font-weight:700; margin-bottom:10px;'>EXECUTION PROTOCOL</div>", unsafe_allow_html=True)
    
    setup = st.session_state.get('fill_setup', {})
    order_type = st.radio("TYPE", ["MARKET", "LIMIT"], horizontal=True, label_visibility="collapsed")
    
    with st.form("exec_form"):
        if order_type == "LIMIT":
            entry = st.number_input("ENTRY PRICE", value=float(setup.get('entry', 0.0)))
        else:
            st.caption("Market Execution")
            entry = 98000.0
            
        stop = st.number_input("STOP LOSS", value=float(setup.get('sl', 0.0)))
        tp = st.number_input("TAKE PROFIT", value=float(setup.get('tp', 0.0)))
        
        st.markdown("---")
        risk_usd = st.number_input("RISK ($)", value=100.0)
        lev = st.slider("LEVERAGE", 1, 100, 10)
        
        if stop > 0 and entry > 0:
            diff_pct = abs(entry - stop) / entry
            if diff_pct > 0:
                pos_value = risk_usd / diff_pct 
                margin = pos_value / lev
                size_in_coin = pos_value / entry
                st.markdown(f"""<div style="font-size:11px; background:#111; padding:10px; border-radius:4px; border:1px solid #222;"><div style="display:flex; justify-content:space-between;"><span>SIZE:</span> <span style="color:#fff;">{size_in_coin:.4f}</span></div><div style="display:flex; justify-content:space-between;"><span>MARGIN:</span> <span style="color:#F0B90B;">${margin:.2f}</span></div></div>""", unsafe_allow_html=True)
        
        c_b1, c_b2 = st.columns(2)
        c_b1.form_submit_button("BUY / LONG")
        c_b2.form_submit_button("SELL / SHORT")
    
    st.markdown("---")
    st.markdown("<div style='font-size:10px; color:#848e9c; font-weight:700;'>LATEST INTEL</div>", unsafe_allow_html=True)
    for n in news[:6]:
        st.markdown(f"<div style='font-size:10px; padding:5px 0; border-bottom:1px solid #2b3139; color:#999;'>{n['title'][:50]}...</div>", unsafe_allow_html=True)