import pandas as pd
import numpy as np

class SupportResistanceAnalyzer:
    def __init__(self):
        self.levels = []
    
    def find_levels(self, df, window=20):
        """Tìm các mức hỗ trợ và kháng cự"""
        levels = {
            'support': [],
            'resistance': [],
            'dynamic': {
                'support': [],
                'resistance': []
            }
        }
        
        # Tìm các mức cứng (Static Support/Resistance)
        highs = df['high'].rolling(window=window).max()
        lows = df['low'].rolling(window=window).min()
        
        # Lấy các đỉnh và đáy
        peaks = highs[(highs.shift(1) < highs) & (highs.shift(-1) < highs)]
        valleys = lows[(lows.shift(1) > lows) & (lows.shift(-1) > lows)]
        
        # Thêm vào danh sách
        for peak in peaks:
            levels['resistance'].append({
                'price': peak,
                'type': 'resistance',
                'strength': 0.7
            })
        
        for valley in valleys:
            levels['support'].append({
                'price': valley,
                'type': 'support',
                'strength': 0.7
            })
        
        # Tìm các mức động (Dynamic Support/Resistance)
        sma_20 = df['close'].rolling(window=20).mean()
        sma_50 = df['close'].rolling(window=50).mean()
        
        # Mức động là các SMA
        levels['dynamic']['support'].append({
            'price': sma_20.iloc[-1],
            'type': 'sma_20',
            'strength': 0.5
        })
        
        levels['dynamic']['support'].append({
            'price': sma_50.iloc[-1],
            'type': 'sma_50',
            'strength': 0.6
        })
        
        # Tìm các mức pivot
        pivot_highs = self.find_pivot_highs(df)
        pivot_lows = self.find_pivot_lows(df)
        
        for pivot in pivot_highs:
            levels['resistance'].append({
                'price': pivot,
                'type': 'pivot_high',
                'strength': 0.8
            })
        
        for pivot in pivot_lows:
            levels['support'].append({
                'price': pivot,
                'type': 'pivot_low',
                'strength': 0.8
            })
        
        return levels
    
    def find_pivot_highs(self, df, window=5):
        """Tìm các đỉnh pivot"""
        pivot_highs = []
        
        for i in range(window, len(df) - window):
            if (df.iloc[i]['high'] > df.iloc[i-window:i]['high'].max() and
                df.iloc[i]['high'] > df.iloc[i+1:i+window+1]['high'].max()):
                pivot_highs.append(df.iloc[i]['high'])
        
        return pivot_highs
    
    def find_pivot_lows(self, df, window=5):
        """Tìm các đáy pivot"""
        pivot_lows = []
        
        for i in range(window, len(df) - window):
            if (df.iloc[i]['low'] < df.iloc[i-window:i]['low'].min() and
                df.iloc[i]['low'] < df.iloc[i+1:i+window+1]['low'].min()):
                pivot_lows.append(df.iloc[i]['low'])
        
        return pivot_lows