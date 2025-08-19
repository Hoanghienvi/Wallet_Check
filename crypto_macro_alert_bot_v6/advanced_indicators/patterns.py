import pandas as pd
import numpy as np

class PatternRecognizer:
    def __init__(self):
        self.patterns = []
    
    def identify_head_and_shoulders(self, df):
        """Nhận diện mẫu hình Head and Shoulders"""
        pattern = {
            'name': 'Head and Shoulders',
            'type': 'reversal',
            'strength': 0,
            'detected': False,
            'details': {}
        }
        
        # Tìm 3 đỉnh
        highs = df['high'].rolling(window=5).max()
        peaks = highs[(highs.shift(1) < highs) & (highs.shift(-1) < highs)]
        
        if len(peaks) >= 3:
            # Lấy 3 đỉnh gần nhất
            last_3_peaks = peaks.tail(3)
            
            # Kiểm tra xem có phải là Head and Shoulders không
            if (last_3_peaks.iloc[0] < last_3_peaks.iloc[1] > last_3_peaks.iloc[2] and
                abs(last_3_peaks.iloc[0] - last_3_peaks.iloc[2]) < 0.1 * last_3_peaks.iloc[1]):
                
                pattern['detected'] = True
                pattern['strength'] = 0.8
                pattern['details'] = {
                    'left_shoulder': last_3_peaks.iloc[0],
                    'head': last_3_peaks.iloc[1],
                    'right_shoulder': last_3_peaks.iloc[2],
                    'neckline': df['low'].rolling(window=5).min().mean()
                }
        
        return pattern
    
    def identify_double_top(self, df):
        """Nhận diện mẫu hình Double Top"""
        pattern = {
            'name': 'Double Top',
            'type': 'reversal',
            'strength': 0,
            'detected': False,
            'details': {}
        }
        
        # Tìm 2 đỉnh gần nhau
        highs = df['high'].rolling(window=5).max()
        peaks = highs[(highs.shift(1) < highs) & (highs.shift(-1) < highs)]
        
        if len(peaks) >= 2:
            last_2_peaks = peaks.tail(2)
            
            # Kiểm tra xem có phải là Double Top không
            if abs(last_2_peaks.iloc[0] - last_2_peaks.iloc[1]) < 0.05 * last_2_peaks.iloc[0]:
                pattern['detected'] = True
                pattern['strength'] = 0.7
                pattern['details'] = {
                    'first_top': last_2_peaks.iloc[0],
                    'second_top': last_2_peaks.iloc[1],
                    'neckline': df['low'].rolling(window=5).min().mean()
                }
        
        return pattern
    
    def identify_double_bottom(self, df):
        """Nhận diện mẫu hình Double Bottom"""
        pattern = {
            'name': 'Double Bottom',
            'type': 'reversal',
            'strength': 0,
            'detected': False,
            'details': {}
        }
        
        # Tìm 2 đáy gần nhau
        lows = df['low'].rolling(window=5).min()
        valleys = lows[(lows.shift(1) > lows) & (lows.shift(-1) > lows)]
        
        if len(valleys) >= 2:
            last_2_valleys = valleys.tail(2)
            
            # Kiểm tra xem có phải là Double Bottom không
            if abs(last_2_valleys.iloc[0] - last_2_valleys.iloc[1]) < 0.05 * last_2_valleys.iloc[0]:
                pattern['detected'] = True
                pattern['strength'] = 0.7
                pattern['details'] = {
                    'first_bottom': last_2_valleys.iloc[0],
                    'second_bottom': last_2_valleys.iloc[1],
                    'resistance': df['high'].rolling(window=5).max().mean()
                }
        
        return pattern
    
    def identify_triangle(self, df):
        """Nhận diện mẫu hình Triangle"""
        pattern = {
            'name': 'Triangle',
            'type': 'continuation',
            'strength': 0,
            'detected': False,
            'details': {}
        }
        
        # Tính toán các đường trend
        highs = df['high'].rolling(window=3).mean()
        lows = df['low'].rolling(window=3).mean()
        
        # Kiểm tra xu hướng thu hẹp
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
        
        if abs(high_slope) < 0.1 and abs(low_slope) < 0.1 and high_slope * low_slope > 0:
            pattern['detected'] = True
            pattern['strength'] = 0.6
            pattern['details'] = {
                'high_slope': high_slope,
                'low_slope': low_slope,
                'type': 'Ascending' if high_slope > 0 else 'Descending'
            }
        
        return pattern
    
    def identify_wedge(self, df):
        """Nhận diện mẫu hình Wedge"""
        pattern = {
            'name': 'Wedge',
            'type': 'reversal',
            'strength': 0,
            'detected': False,
            'details': {}
        }
        
        # Tính toán các đường trend
        highs = df['high'].rolling(window=3).mean()
        lows = df['low'].rolling(window=3).mean()
        
        # Kiểm tra xu hướng hội tụ
        high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
        low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
        
        if abs(high_slope) > 0.05 and abs(low_slope) > 0.05 and high_slope * low_slope < 0:
            pattern['detected'] = True
            pattern['strength'] = 0.6
            pattern['details'] = {
                'high_slope': high_slope,
                'low_slope': low_slope,
                'type': 'Rising' if high_slope > 0 else 'Falling'
            }
        
        return pattern