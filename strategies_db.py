# strategies_db.py

"""
HAAUB & CO - STRATEGY LIBRARY DATABASE
31 Professional Trading Strategies with Strict Confirmation Rules.
"""

STRATEGY_LIBRARY = {
    # ---------------------------------------------------------
    # I. TREND TAKİP STRATEJİLERİ (TREND FOLLOWING)
    # ---------------------------------------------------------
    "TREND_FOLLOWING": {
        "MA Crossover": {
            "Logic": "Golden/Death Cross (50 EMA crosses 200 EMA).",
            "Confirmation": "Price must close above (Buy) or below (Sell) the short-term MA after cross."
        },
        "Breakout": {
            "Logic": "High volume break of established Support/Resistance.",
            "Confirmation": "Clear candle close beyond the level + Retest of the broken level."
        },
        "Bollinger Squeeze": {
            "Logic": "Low volatility contraction followed by expansion.",
            "Confirmation": "Price pierces Upper Band (Buy) or Lower Band (Sell) with Volume spike."
        },
        "Trendline Bounce": {
            "Logic": "3rd or 4th touch of a validated trendline.",
            "Confirmation": "Reversal candle formation (Pin Bar, Engulfing) at the touch point."
        },
        "Ichimoku Breakout": {
            "Logic": "Price breaks out of the Kumo Cloud.",
            "Confirmation": "Chikou Span (Lagging line) must also be above/below the price and cloud."
        }
    },

    # ---------------------------------------------------------
    # II. FİYAT HAREKETİ (PRICE ACTION)
    # ---------------------------------------------------------
    "PRICE_ACTION": {
        "Pin Bar": {
            "Logic": "Long wick rejection at key Support/Resistance.",
            "Confirmation": "Next candle must close in the opposite direction or break the Pin Bar high/low."
        },
        "Engulfing": {
            "Logic": "Reversal body fully covers the previous candle body.",
            "Confirmation": "Must occur at a Key Level (S/R)."
        },
        "Inside Bar": {
            "Logic": "Consolidation candle fully contained within the previous mother candle.",
            "Confirmation": "Breakout of the mother candle's High or Low."
        },
        "Head & Shoulders": {
            "Logic": "Reversal pattern (Left Shoulder, Head, Right Shoulder).",
            "Confirmation": "Break and close below/above the Neckline."
        },
        "Double Top/Bottom": {
            "Logic": "Price fails to break a level twice (M or W shape).",
            "Confirmation": "Break of the Neckline between the two peaks/troughs."
        }
    },

    # ---------------------------------------------------------
    # III. SMART MONEY CONCEPTS (SMC - TEMEL)
    # ---------------------------------------------------------
    "SMC_BASIC": {
        "Supply & Demand": {
            "Logic": "Return to aggressive buying (Demand) or selling (Supply) origin zones.",
            "Confirmation": "LTF (Lower Timeframe) CHoCH (Change of Character) upon entry."
        },
        "Fibonacci Retracement": {
            "Logic": "Correction to Golden Pocket (0.618 - 0.5).",
            "Confirmation": "Reversal candle formation at the Fibonacci level."
        },
        "Wyckoff Method": {
            "Logic": "Accumulation (Spring) or Distribution (UTAD) schematic.",
            "Confirmation": "Strong impulse back into range after the Spring/UTAD."
        },
        "Order Block": {
            "Logic": "Last opposing candle before a strong impulsive move.",
            "Confirmation": "High volume reaction upon mitigation (return to block)."
        },
        "Liquidity Hunt": {
            "Logic": "Fakeout/Stop Hunt below Support or above Resistance.",
            "Confirmation": "Fast reversal and close back inside the range after taking stops."
        }
    },

    # ---------------------------------------------------------
    # IV. MOMENTUM & OSCILLATORS
    # ---------------------------------------------------------
    "MOMENTUM": {
        "RSI Divergence": {
            "Logic": "Price makes Higher High, RSI makes Lower High (Bearish) or vice versa.",
            "Confirmation": "Trendline break or Reversal Candle after divergence."
        },
        "MACD Cross": {
            "Logic": "MACD line crosses Signal line.",
            "Confirmation": "Crossover happens above/below Zero Line for trend confirmation."
        },
        "Stochastic Scalp": {
            "Logic": "Ranging market: Oversold (<20) Buy, Overbought (>80) Sell.",
            "Confirmation": "K line crosses D line."
        }
    },

    # ---------------------------------------------------------
    # V. FUNDAMENTAL & MACRO
    # ---------------------------------------------------------
    "FUNDAMENTAL": {
        "News Straddle": {
            "Logic": "High volatility expectation before NFP/FOMC.",
            "Confirmation": "Entry triggered by momentum burst in one direction post-news."
        },
        "Carry Trade": {
            "Logic": "Long High Yield Currency / Short Low Yield Currency.",
            "Confirmation": "Central Bank interest rate divergence widening + Trend alignment."
        }
    },

    # ---------------------------------------------------------
    # VI. HARMONIC PATTERNS (GEOMETRİ)
    # ---------------------------------------------------------
    "HARMONICS": {
        "Gartley & Bat": {
            "Logic": "Retracement pattern completing at 0.618 or 0.786 Fib.",
            "Confirmation": "RSI Divergence or Pinbar within the PRZ (Potential Reversal Zone)."
        },
        "Butterfly & Crab": {
            "Logic": "Extension pattern completing at 1.272 or 1.618 Fib.",
            "Confirmation": "Hard rejection (Wick) from the extension level."
        }
    },

    # ---------------------------------------------------------
    # VII. ZAMAN VE OTURUM (TIME-BASED)
    # ---------------------------------------------------------
    "TIME_BASED": {
        "London Breakout": {
            "Logic": "Break of the Asian Range High/Low.",
            "Confirmation": "15m Candle close outside Asian Box + Retest."
        },
        "ICT Kill Zones": {
            "Logic": "High volatility window (NY/London Open).",
            "Confirmation": "Liquidity Sweep or Market Structure Break (MSB) during these specific hours."
        },
        "Fade Asian Range": {
            "Logic": "Range-bound market: Sell Asian High, Buy Asian Low.",
            "Confirmation": "Momentum loss at range boundaries + Oscillator extreme."
        }
    },

    # ---------------------------------------------------------
    # VIII. HACİM VE PROFİL (VOLUME)
    # ---------------------------------------------------------
    "VOLUME": {
        "Volume Profile (POC)": {
            "Logic": "Revisit to the Point of Control (Highest Volume Level).",
            "Confirmation": "Delta divergence or rejection reaction at POC."
        },
        "VWAP Reversion": {
            "Logic": "Price extended far from VWAP returns to mean.",
            "Confirmation": "Price touches VWAP and reacts."
        }
    },

    # ---------------------------------------------------------
    # IX. KURUMSAL YAPI (ADVANCED SMC)
    # ---------------------------------------------------------
    "ADVANCED_SMC": {
        "Fair Value Gap (FVG)": {
            "Logic": "Imbalance area left by impulsive move.",
            "Confirmation": "Price fills the gap and breaks structure (CHoCH) on LTF."
        },
        "SMT Divergence": {
            "Logic": "Correlation crack (e.g., BTC makes HH, ETH makes LH).",
            "Confirmation": "Divergence occurs at a Key HTF Level."
        }
    },

    # ---------------------------------------------------------
    # X. MEKANİK VE İSTATİSTİKSEL
    # ---------------------------------------------------------
    "MECHANICAL": {
        "Grid Trading": {
            "Logic": "Ranging market automated buy/sell levels.",
            "Confirmation": "No confirmation needed; relies on math/risk management in sideways market."
        },
        "3-Tap Setup": {
            "Logic": "3rd touch of a Wedge or Channel boundary.",
            "Confirmation": "Engulfing candle formed on the 3rd touch."
        }
    }
}

def get_all_strategies_list():
    """Tüm strateji isimlerini tek bir liste olarak döner (Arayüz için)"""
    all_strats = []
    for cat in STRATEGY_LIBRARY.values():
        all_strats.extend(list(cat.keys()))
    return sorted(all_strats)

def get_strategy_details(strategy_name):
    """Seçilen stratejinin mantık ve onay kurallarını döner (AI için)"""
    for cat in STRATEGY_LIBRARY.values():
        if strategy_name in cat:
            return cat[strategy_name]
    return {"Logic": "General Analysis", "Confirmation": "Price Action"}