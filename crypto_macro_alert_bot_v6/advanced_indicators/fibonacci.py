import numpy as np
import pandas as pd

class FibonacciAnalyzer:
    def __init__(self):
        self.fib_levels = {
            '0.0': 0,
            '23.6': 0.236,
            '38.2': 0.382,
            '50.0': 0.5,
            '61.8': 0.618,
            '78.6': 0.786,
            '100.0': 1
        }
    
    def calculate_fibonacci(self, df, high_col='high', low_col='low'):
        """Tính toán các mức Fibonacci"""
        # Lấy đỉnh và đáy trong khoảng thời gian
        high = df[high_col].max()
        low = df[low_col].min()
        
        # Tính toán các mức Fibonacci
        fib_levels = {}
        for level, ratio in self.fib_levels.items():
            fib_levels[level] = high - (high - low) * ratio
        
        return fib_levels
    
    def identify_fibonacci_retracement(self, df, symbol, timeframe):
        """Nhận diện mức Fibonacci retracement"""
        # Tìm đỉnh và đáy gần nhất
        recent_high = df['high'].iloc[-20:].max()
        recent_low = df['low'].iloc[-20:].min()
        
        # Tính toán các mức retracement
        fib_levels = {}
        for level, ratio in self.fib_levels.items():
            fib_levels[level] = recent_high - (recent_high - recent_low) * ratio
        
        # Kiểm tra giá có đang ở gần mức Fibonacci nào không
        current_price = df['close'].iloc[-1]
        near_levels = []
        
        for level, price in fib_levels.items():
            if abs(current_price - price) / current_price < 0.02:  # 2% tolerance
                near_levels.append((level, price))
        
        return {
            'fib_levels': fib_levels,
            'near_levels': near_levels,
            'recent_high': recent_high,
            'recent_low': recent_low
        }
    
    def identify_fibonacci_extension(self, df):
        """Nhận diện mức Fibonacci extension"""
        # Tìm đỉnh và đáy gần nhất
        recent_high = df['high'].iloc[-20:].max()
        recent_low = df['low'].iloc[-20:].min()
        
        # Tính toán các mức extension
        ext_levels = {
            '127.2': recent_low + (recent_high - recent_low) * 1.272,
            '161.8': recent_low + (recent_high - recent_low) * 1.618,
            '261.8': recent_low + (recent_high - recent_low) * 2.618
        }
        
        return ext_levels