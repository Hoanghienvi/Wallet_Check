import pandas as pd
import numpy as np

class GannAngleAnalyzer:
    def __init__(self):
        self.angles = []
    
    def calculate_gann_angles(self, df):
        """Tính toán các góc Gann"""
        angles = {
            '1x1': None,
            '1x2': None,
            '2x1': None,
            '4x1': None,
            '1x4': None
        }
        
        # Lấy dữ liệu
        high = df['high'].max()
        low = df['low'].min()
        close = df['close'].iloc[-1]
        
        # Tính toán phạm vi giá
        price_range = high - low
        
        # Tính toán các góc Gann
        # 1x1: 45 độ
        angles['1x1'] = {
            'angle': 45,
            'price_per_unit': 1,
            'time_per_unit': 1,
            'description': '1x1 angle - 45 degrees'
        }
        
        # 1x2: 63.43 độ
        angles['1x2'] = {
            'angle': 63.43,
            'price_per_unit': 2,
            'time_per_unit': 1,
            'description': '1x2 angle - 63.43 degrees'
        }
        
        # 2x1: 26.57 độ
        angles['2x1'] = {
            'angle': 26.57,
            'price_per_unit': 1,
            'time_per_unit': 2,
            'description': '2x1 angle - 26.57 degrees'
        }
        
        # 4x1: 75.96 độ
        angles['4x1'] = {
            'angle': 75.96,
            'price_per_unit': 4,
            'time_per_unit': 1,
            'description': '4x1 angle - 75.96 degrees'
        }
        
        # 1x4: 14.04 độ
        angles['1x4'] = {
            'angle': 14.04,
            'price_per_unit': 1,
            'time_per_unit': 4,
            'description': '1x4 angle - 14.04 degrees'
        }
        
        # Tính toán các mức giá dựa trên góc 1x1
        current_time = len(df)
        angles['1x1_levels'] = {
            'support': close - (current_time * price_range / len(df)),
            'resistance': close + (current_time * price_range / len(df))
        }
        
        return angles