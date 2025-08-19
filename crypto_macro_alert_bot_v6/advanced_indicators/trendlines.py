import pandas as pd
import numpy as np

class TrendlineAnalyzer:
    def __init__(self):
        self.trendlines = []
    
    def draw_trendlines(self, df):
        """Vẽ các đường xu hướng"""
        trendlines = {
            'uptrend': [],
            'downtrend': [],
            'horizontal': []
        }
        
        # Tìm các đỉnh và đáy
        highs = df['high'].rolling(window=5).max()
        lows = df['low'].rolling(window=5).min()
        peaks = highs[(highs.shift(1) < highs) & (highs.shift(-1) < highs)]
        valleys = lows[(lows.shift(1) > lows) & (lows.shift(-1) > lows)]
        
        # Vẽ đường xu hướng tăng
        if len(valleys) >= 2:
            # Lấy 2 đáy gần nhất để vẽ đường
            valley1 = valleys.iloc[-2]
            valley2 = valleys.iloc[-1]
            
            # Tính toán độ dốc
            slope = (valley2 - valley1) / 2
            
            # Vẽ đường xu hướng tăng
            trendlines['uptrend'].append({
                'start_price': valley1,
                'end_price': valley2,
                'slope': slope,
                'strength': 0.7
            })
        
        # Vẽ đường xu hướng giảm
        if len(peaks) >= 2:
            # Lấy 2 đỉnh gần nhất để vẽ đường
            peak1 = peaks.iloc[-2]
            peak2 = peaks.iloc[-1]
            
            # Tính toán độ dốc
            slope = (peak2 - peak1) / 2
            
            # Vẽ đường xu hướng giảm
            trendlines['downtrend'].append({
                'start_price': peak1,
                'end_price': peak2,
                'slope': slope,
                'strength': 0.7
            })
        
        # Vẽ đường ngang
        current_price = df['close'].iloc[-1]
        if len(trendlines['uptrend']) > 0:
            last_uptrend = trendlines['uptrend'][-1]
            if abs(current_price - last_uptrend['end_price']) / current_price < 0.02:
                trendlines['horizontal'].append({
                    'price': current_price,
                    'type': 'resistance',
                    'strength': 0.6
                })
        
        if len(trendlines['downtrend']) > 0:
            last_downtrend = trendlines['downtrend'][-1]
            if abs(current_price - last_downtrend['end_price']) / current_price < 0.02:
                trendlines['horizontal'].append({
                    'price': current_price,
                    'type': 'support',
                    'strength': 0.6
                })
        
        return trendlines