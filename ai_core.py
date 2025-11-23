import google.generativeai as genai
import json
import config
import strategies_db

genai.configure(api_key=config.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash', generation_config=config.AI_CONFIG)

def execute_iron_dome_protocol(image, symbol, tf, market_data, macro_data, sentiment, depth, user_strats):
    """
    HAAUB DEMİR KUBBE PROTOKOLÜ
    ---------------------------
    Bu fonksiyon 'Council of Experts' (Uzmanlar Konseyi) simülasyonu yapar.
    Tek bir karar yerine, zıt görüşlerin çatışmasından doğan sentezi üretir.
    """
    
    # 1. Veri Paketlemesi (AI'a Okunabilir Rapor Sunma)
    data_report = f"""
    --- MARKET SNAPSHOT ---
    ASSET: {symbol} ({tf})
    PRICE: {market_data.get('price', 'N/A')}
    
    [TECHNICALS]
    RSI: {market_data.get('rsi', 'N/A')}
    ATR (Volatility): {market_data.get('atr', 'N/A')}
    Trend: {market_data.get('trend_ema', 'N/A')}
    
    [MACRO CONTEXT]
    DXY (Dollar Index): {macro_data.get('DXY', {}).get('change', 0)}% (Negative correlation to Crypto)
    US10Y (Yields): {macro_data.get('US10Y', {}).get('change', 0)}%
    VIX (Fear): {macro_data.get('VIX', {}).get('price', 0)}
    
    [SENTIMENT & DEPTH]
    Fear & Greed: {sentiment.get('value')} ({sentiment.get('status')})
    Funding Rate: {depth.get('funding', 0)}%
    Orderbook Bias: {depth.get('pressure', 'Neutral')}
    """
    
    # 2. Kullanıcı Stratejileri
    strat_instruction = "AUTO-DETECT BEST STRATEGY"
    if user_strats:
        strat_instruction = f"VALIDATE SPECIFICALLY AGAINST: {', '.join(user_strats)}"

    # 3. THE COUNCIL PROMPT (Devasa Prompt)
    prompt = f"""
    **SYSTEM:** YOU ARE THE 'HAAUB IRON DOME' TRADING COUNCIL.
    **OBJECTIVE:** PROTECT CAPITAL FIRST, THEN SEEK PROFIT.
    
    You are composed of 3 internal agents. You must simulate their debate:
    
    **AGENT 1: THE TECHNICIAN (Bullish/Opportunity Seeker)**
    - Scan the chart image for patterns, entries, and selected strategies ({strat_instruction}).
    - Ignore macro FUD, focus purely on Price Action.
    - Output: "Here is the opportunity..."
    
    **AGENT 2: THE SKEPTIC (Bearish/Risk Manager)**
    - Look at the DATA REPORT below the chart.
    - Find reasons to REJECT the trade (e.g., DXY is pumping, Funding is too high, RSI is overbought).
    - Check for divergences or traps.
    - Output: "Here are the risks..."
    
    **AGENT 3: THE JUDGE (Final Decision)**
    - Weigh Agent 1 vs Agent 2.
    - IF risks > opportunities OR Macro contradicts Technicals -> VETO (WAIT).
    - IF Technicals aligned AND Macro neutral/supportive -> APPROVE.
    - Assign a confidence score (0-100).
    - Calculate Entry, Stop Loss (Using ATR from data), and TP.
    
    ---
    **DATA REPORT:**
    {data_report}
    ---
    
    **OUTPUT FORMAT (JSON ONLY):**
    {{
        "council_debate": {{
            "bull_agent": "Summary of technical reasons to enter...",
            "bear_agent": "Summary of risks (Macro/Data) to avoid...",
            "judge_verdict": "Final synthesis reasoning..."
        }},
        "action": "LONG / SHORT / WAIT",
        "score": 85,
        "strategy": "Name of the winning strategy",
        "setup": {{
            "entry": 0.0,
            "sl": 0.0,
            "tp1": 0.0,
            "tp2": 0.0
        }}
    }}
    """
    
    try:
        inputs = [prompt, image] if image else [prompt]
        res = model.generate_content(inputs)
        return json.loads(res.text.replace("```json", "").replace("```", "").strip())
    except Exception as e:
        return {
            "action": "ERROR", 
            "score": 0, 
            "council_debate": {"judge_verdict": f"System Error: {str(e)}"}
        }