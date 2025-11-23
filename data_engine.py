import ccxt
import yfinance as yf
import feedparser
import pandas as pd
import numpy as np
import requests
import time
import concurrent.futures
from datetime import datetime
import config

class DataEngine:
    def __init__(self):
        self.okx = self._init_exchange()
        self.cache = {}

    def _init_exchange(self):
        try:
            return ccxt.okx({
                'apiKey': config.OKX_API_KEY,
                'secret': config.OKX_SECRET,
                'password': config.OKX_PASSWORD,
                'enableRateLimit': True,
                'options': {'defaultType': 'swap'}
            })
        except Exception as e:
            print(f"Exchange Init Error: {e}")
            return ccxt.okx()

    def _retry_fetch(self, func, *args, retries=3):
        for i in range(retries):
            try:
                return func(*args)
            except: time.sleep(0.5)
        return None

    # ============================================================
    # 🚀 MASTER COLLECTOR
    # ============================================================
    def get_master_data(self, symbol, timeframe):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            f_candles = executor.submit(self.get_technical_data, symbol, timeframe)
            f_mtf = executor.submit(self.get_multi_timeframe_trend, symbol, timeframe)
            f_macro = executor.submit(self.get_macro_data)
            f_depth = executor.submit(self.get_depth_data, symbol)
            f_sentiment = executor.submit(self.get_sentiment_data)

            tech_data = f_candles.result()
            
            return {
                "technical": tech_data,
                "mtf_trend": f_mtf.result(),
                "macro": f_macro.result(),
                "depth": f_depth.result(),
                "sentiment": f_sentiment.result(),
                "analysis_extras": {
                    "liquidation_zones": self.calculate_liquidation_zones(tech_data),
                    "whale_alert": self.detect_whale_activity(tech_data),
                    "volume_profile_poc": self.calculate_volume_profile(tech_data)
                }
            }

    def get_news(self):
        """
        Haberleri Canlı Çeker (Cache süresini Main.py yönetir)
        CoinTelegraph + CryptoPanic (Yedekli)
        """
        news_list = []
        try:
            # Kaynak 1: CoinTelegraph
            d = feedparser.parse('https://cointelegraph.com/rss')
            for e in d.entries[:5]:
                news_list.append({"title": e.title, "link": e.link})
        except: pass
        
        return news_list

    # ============================================================
    # 🛠️ ALT MODÜLLER
    # ============================================================

    def get_technical_data(self, symbol, timeframe):
        try:
            bars = self._retry_fetch(self.okx.fetch_ohlcv, symbol, timeframe, None, 200)
            if not bars: return pd.DataFrame()
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # EMA
            df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
            df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()
            
            # Bollinger
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['STD20'] = df['close'].rolling(window=20).std()
            df['BBU_20_2.0'] = df['MA20'] + (df['STD20'] * 2)
            df['BBL_20_2.0'] = df['MA20'] - (df['STD20'] * 2)
            
            # ATR
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            df['ATR'] = true_range.rolling(14).mean()

            return df
        except: return pd.DataFrame()

    def get_multi_timeframe_trend(self, symbol, current_tf):
        try:
            higher_tf = "1d" if current_tf in ["4h", "12h"] else "4h" if current_tf == "1h" else "1h"
            bars = self.okx.fetch_ohlcv(symbol, higher_tf, limit=50)
            df = pd.DataFrame(bars, columns=['t','o','h','l','c','v'])
            sma50 = df['c'].rolling(window=50).mean().iloc[-1]
            curr = df['c'].iloc[-1]
            return f"{higher_tf.upper()} Trend: {'BULLISH' if curr > sma50 else 'BEARISH'}"
        except: return "MTF: N/A"

    def get_macro_data(self):
        """
        DXY, US10Y, VIX, GOLD, SP500 + BTC.D (CoinGecko Entegreli)
        """
        result = {}
        
        # 1. Yahoo Finance Verileri
        try:
            tickers = {"DXY": "DX-Y.NYB", "US10Y": "^TNX", "VIX": "^VIX", "GOLD": "GC=F", "SP500": "^GSPC"}
            data = yf.download(list(tickers.values()), period="2d", progress=False)['Close']
            
            for k, v in tickers.items():
                try:
                    curr = data[v].iloc[-1]
                    prev = data[v].iloc[-2]
                    chg = ((curr - prev) / prev) * 100
                    result[k] = {"price": curr, "change": chg}
                except: result[k] = {"price": 0, "change": 0}
        except: pass

        # 2. BTC.D (CoinGecko FIX) - 0.00 Sorununu Çözer
        try:
            # Global Market verisini çek
            r = requests.get("https://api.coingecko.com/api/v3/global", timeout=2).json()
            btc_d = r['data']['market_cap_percentage']['btc']
            # Değişim verisi global endpointte anlık gelmez, bu yüzden değişimi 0 kabul edip sadece mevcut oranı gösteriyoruz
            # Veya bir önceki cache'den fark alınabilir ama şimdilik real-time değer yeterli.
            result["BTC.D"] = {"price": btc_d, "change": 0.0} 
        except:
            # Eğer API hata verirse manuel hesaplama denemesi veya N/A
            result["BTC.D"] = {"price": 0.0, "change": 0.0}

        return result

    def calculate_liquidation_zones(self, df):
        if df.empty: return {}
        curr = df['close'].iloc[-1]
        return {"Short_Liq": curr * 1.01, "Long_Liq": curr * 0.99}

    def detect_whale_activity(self, df):
        if df.empty: return False
        last_vol = df['volume'].iloc[-1]
        avg_vol = df['volume'].tail(20).mean()
        return "🚨 WHALE ALERT!" if last_vol > avg_vol * 3 else "Normal Volume"

    def calculate_volume_profile(self, df):
        if df.empty: return 0
        try:
            price_bins = pd.cut(df['close'], bins=10)
            vol_grp = df.groupby(price_bins, observed=False)['volume'].sum()
            poc_idx = vol_grp.idxmax()
            return (poc_idx.left + poc_idx.right) / 2
        except: return 0

    def get_depth_data(self, symbol):
        try:
            fund = self._retry_fetch(self.okx.fetch_funding_rate, symbol)
            fr = fund['fundingRate'] * 100 if fund else 0
            
            ob = self._retry_fetch(self.okx.fetch_order_book, symbol, 20)
            pressure = "NEUTRAL"
            if ob:
                bids = sum([x[1] for x in ob['bids']])
                asks = sum([x[1] for x in ob['asks']])
                ratio = bids / asks if asks > 0 else 1
                pressure = "BUYERS" if ratio > 1.1 else "SELLERS" if ratio < 0.9 else "NEUTRAL"
            return {"funding": fr, "pressure": pressure}
        except: return {}

    def get_sentiment_data(self):
        try:
            r = requests.get("https://api.alternative.me/fng/", timeout=3).json()
            return {"value": int(r['data'][0]['value']), "status": r['data'][0]['value_classification']}
        except: return {"value": 50, "status": "Neutral"}

    def get_wallet_balance(self):
        try:
            bal = self._retry_fetch(self.okx.fetch_balance)
            return bal['USDT']['free'] if bal else 0.0
        except: return 0.00

    def get_open_positions_df(self):
        try:
            pos = self.okx.fetch_positions()
            if pos:
                d = [[p['symbol'], p['side'].upper(), p['contracts'], p['entryPrice'], p['unrealizedPnl']] for p in pos]
                return pd.DataFrame(d, columns=['SYMBOL', 'SIDE', 'SIZE', 'ENTRY', 'PNL'])
        except: pass
        return pd.DataFrame(columns=['SYMBOL', 'SIDE', 'SIZE', 'ENTRY', 'PNL'])