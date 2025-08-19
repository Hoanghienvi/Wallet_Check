import pandas as pd
import numpy as np

class CandlestickPatternRecognizer:
    def __init__(self):
        self.patterns = []
    
    def identify_doji(self, df):
        """Nhận diện mẫu hình Doji"""
        patterns = []
        
        for i in range(1, len(df)):
            candle = df.iloc[i]
            body = abs(candle['close'] - candle['open'])
            total_range = candle['high'] - candle['low']
            
            # Doji: thân nến rất nhỏ so với tổng phạm vi
            if body < 0.1 * total_range:
                patterns.append({
                    'index': i,
                    'type': 'Doji',
                    'strength': 0.5,
                    'pattern': 'neutral'
                })
        
        return patterns
    
    def identify_hammer(self, df):
        """Nhận diện mẫu hình Hammer"""
        patterns = []
        
        for i in range(1, len(df)):
            candle = df.iloc[i]
            body = abs(candle['close'] - candle['open'])
            lower_shadow = candle['open'] - min(candle['open'], candle['close'])
            upper_shadow = max(candle['open'], candle['close']) - candle['high']
            total_range = candle['high'] - candle['low']
            
            # Hammer: bóng dài dưới, thân ngắn, bóng trên rất ngắn
            if (lower_shadow > 2 * body and 
                upper_shadow < 0.1 * total_range and
                candle['low'] < df.iloc[i-1]['low']):
                
                patterns.append({
                    'index': i,
                    'type': 'Hammer',
                    'strength': 0.7,
                    'pattern': 'bullish'
                })
        
        return patterns
    
    def identify_shooting_star(self, df):
        """Nhận diện mẫu hình Shooting Star"""
        patterns = []
        
        for i in range(1, len(df)):
            candle = df.iloc[i]
            body = abs(candle['close'] - candle['open'])
            lower_shadow = candle['open'] - min(candle['open'], candle['close'])
            upper_shadow = max(candle['open'], candle['close']) - candle['high']
            total_range = candle['high'] - candle['low']
            
            # Shooting Star: bóng dài trên, thân ngắn, bóng dưới rất ngắn
            if (upper_shadow > 2 * body and 
                lower_shadow < 0.1 * total_range and
                candle['high'] > df.iloc[i-1]['high']):
                
                patterns.append({
                    'index': i,
                    'type': 'Shooting Star',
                    'strength': 0.7,
                    'pattern': 'bearish'
                })
        
        return patterns
    
    def identify_engulfing(self, df):
        """Nhận diện mẫu hình Engulfing"""
        patterns = []
        
        for i in range(1, len(df)):
            current = df.iloc[i]
            previous = df.iloc[i-1]
            
            # Bullish Engulfing: nến xanh bao nến đỏ trước đó
            if (current['close'] > current['open'] and 
                previous['close'] < previous['open'] and
                current['open'] < previous['close'] and
                current['close'] > previous['open']):
                
                patterns.append({
                    'index': i,
                    'type': 'Bullish Engulfing',
                    'strength': 0.8,
                    'pattern': 'bullish'
                })
            
            # Bearish Engulfing: nến đỏ bao nến xanh trước đó
            elif (current['close'] < current['open'] and 
                  previous['close'] > previous['open'] and
                  current['open'] > previous['close'] and
                  current['close'] < previous['open']):
                
                patterns.append({
                    'index': i,
                    'type': 'Bearish Engulfing',
                    'strength': 0.8,
                    'pattern': 'bearish'
                })
        
        return patterns
    
    def identify_harami(self, df):
        """Nhận diện mẫu hình Harami"""
        patterns = []
        
        for i in range(1, len(df)):
            current = df.iloc[i]
            previous = df.iloc[i-1]
            
            # Harami: nến hiện tại nằm trong thân nến trước đó
            if (current['high'] < previous['high'] and 
                current['low'] > previous['low'] and
                abs(current['close'] - current['open']) < 0.5 * abs(previous['close'] - previous['open'])):
                
                # Xác định Harami tăng hay giảm
                if current['close'] > current['open'] and previous['close'] < previous['open']:
                    pattern_type = 'Bullish Harami'
                    pattern_signal = 'bullish'
                elif current['close'] < current['open'] and previous['close'] > previous['open']:
                    pattern_type = 'Bearish Harami'
                    pattern_signal = 'bearish'
                else:
                    continue
                
                patterns.append({
                    'index': i,
                    'type': pattern_type,
                    'strength': 0.6,
                    'pattern': pattern_signal
                })
        
        return patterns