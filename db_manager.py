import sqlite3
import json
from datetime import datetime
import pandas as pd
import io

DB_NAME = 'god_gm_final.db'

def init_db():
    """Veritabanı ve Tabloları Oluşturur"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Analiz Geçmişi
    c.execute('''CREATE TABLE IF NOT EXISTS analysis_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        symbol TEXT,
        timeframe TEXT,
        final_action TEXT,
        confidence_score INTEGER,
        winning_strategy TEXT,
        log TEXT,
        chart_image BLOB
    )''')

    # 2. İşlem Geçmişi (Trades)
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        symbol TEXT,
        side TEXT,
        pnl REAL,
        status TEXT
    )''')
    
    conn.commit()
    conn.close()

def log_analysis(symbol, tf, ai_result, market_data, macro_data, crypto_data, img_bytes):
    """Analiz Sonucunu Kaydeder"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # AI Sonucundan verileri çek
        action = ai_result.get('action', 'WAIT')
        score = ai_result.get('confidence_score', 0) if 'confidence_score' in ai_result else ai_result.get('score', 0)
        strat = ai_result.get('best_strategy_match', 'AUTO') if 'best_strategy_match' in ai_result else ai_result.get('winning_strategy', 'AUTO')
        log_txt = str(ai_result.get('log', ''))

        # Konsey verisi varsa onu da loga ekle
        if 'council_debate' in ai_result:
            debate = ai_result['council_debate']
            log_txt += f"\n\n[BULL]: {debate.get('bull_agent')}\n[BEAR]: {debate.get('bear_agent')}\n[JUDGE]: {debate.get('judge_verdict')}"

        c.execute("""INSERT INTO analysis_log 
                  (timestamp, symbol, timeframe, final_action, confidence_score, winning_strategy, log, chart_image) 
                  VALUES (?,?,?,?,?,?,?,?)""",
                  (dt, symbol, tf, action, score, strat, log_txt, img_bytes))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"DB Error: {e}")
        return False

def get_history_df():
    """Geçmiş Analizleri Tablo Olarak Döner"""
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT id, timestamp, symbol, timeframe, final_action, confidence_score, winning_strategy FROM analysis_log ORDER BY id DESC LIMIT 50", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def get_image_by_id(analysis_id):
    """ID'ye göre resmi getirir"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT chart_image FROM analysis_log WHERE id=?", (analysis_id,))
        data = c.fetchone()
        conn.close()
        if data and data[0]:
            return data[0]
        return None
    except: return None