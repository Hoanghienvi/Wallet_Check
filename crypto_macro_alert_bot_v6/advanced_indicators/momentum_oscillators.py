import pandas as pd
import numpy as np
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands

class MomentumOscillatorAnalyzer:
    def __init__(self):
        self.indicators = {}
    
    def calculate_indicators(self, df):
        """Tính toán các chỉ báo động lượng và dao động"""
        indicators = {}
        
        # RSI
        rsi_indicator = RSIIndicator(close=df['close'], window=14)
        indicators['rsi'] = {
            'values': rsi_indicator.rsi(),
            'current': rsi_indicator.rsi().iloc[-1],
            'signal': self.get_rsi_signal(rsi_indicator.rsi().iloc[-1])
        }
        
        # MACD
        macd_indicator = MACD(
            close=df['close'],
            window_fast=12,
            window_slow=26,
            window_sign=9
        )
        indicators['macd'] = {
            'macd': macd_indicator.macd(),
            'signal': macd_indicator.macd_signal(),
            'histogram': macd_indicator.macd_diff(),
            'signal': self.get_macd_signal(macd_indicator.macd_diff().iloc[-1])
        }
        
        # Stochastic
        stoch_indicator = StochasticOscillator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14,
            smooth_window=3
        )
        indicators['stochastic'] = {
            'k': stoch_indicator.stoch(),
            'd': stoch_indicator.stoch_signal(),
            'signal': self.get_stochastic_signal(
                stoch_indicator.stoch().iloc[-1],
                stoch_indicator.stoch_signal().iloc[-1]
            )
        }
        
        # CCI (Commodity Channel Index)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma_tp = typical_price.rolling(window=20).mean()
        mad = typical_price.rolling(window=20).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
        cci = (typical_price - sma_tp) / (0.015 * mad)
        
        indicators['cci'] = {
            'values': cci,
            'current': cci.iloc[-1],
            'signal': self.get_cci_signal(cci.iloc[-1])
        }
        
        # Williams %R
        williams_r = -100 * (df['high'].rolling(window=14).max() - df['close']) / (df['high'].rolling(window=14).max() - df['low'].rolling(window=14).min())
        
        indicators['williams_r'] = {
            'values': williams_r,
            'current': williams_r.iloc[-1],
            'signal': self.get_williams_r_signal(williams_r.iloc[-1])
        }
        
        return indicators
    
    def get_rsi_signal(self, rsi_value):
        """Lấy tín hiệu từ RSI"""
        if rsi_value > 70:
            return 'overbought'
        elif rsi_value < 30:
            return 'oversold'
        else:
            return 'neutral'
    
    def get_macd_signal(self, histogram_value):
        """Lấy tín hiệu từ MACD"""
        if histogram_value > 0:
            return 'bullish'
        elif histogram_value < 0:
            return 'bearish'
        else:
            return 'neutral'
    
    def get_stochastic_signal(self, k_value, d_value):
        """Lấy tín hiệu từ Stochastic"""
        if k_value > 80 and d_value > 80:
            return 'overbought'
        elif k_value < 20 and d_value < 20:
            return 'oversold'
        elif k_value > d_value:
            return 'bullish'
        elif k_value < d_value:
            return 'bearish'
        else:
            return 'neutral'
    
    def get_cci_signal(self, cci_value):
        """Lấy tín hiệu từ CCI"""
        if cci_value > 100:
            return 'overbought'
        elif cci_value < -100:
            return 'oversold'
        else:
            return 'neutral'
    
    def get_williams_r_signal(self, williams_r_value):
        """Lấy tín hiệu từ Williams %R"""
        if williams_r_value > -20:
            return 'overbought'
        elif williams_r_value < -80:
            return 'oversold'
        else:
            return 'neutral'