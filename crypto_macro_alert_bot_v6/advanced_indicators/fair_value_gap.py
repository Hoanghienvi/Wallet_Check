import pandas as pd
import numpy as np

class FairValueGapAnalyzer:
    def __init__(self):
        self.fvg_list = []
    
    def calculate_fvg(self, df):
        """Tính toán Fair Value Gap"""
        fvg_list = []
        
        # Lấy dữ liệu nến
        for i in range(1, len(df) - 2):
            current_candle = df.iloc[i]
            next_candle = df.iloc[i + 1]
            third_candle = df.iloc[i + 2]
            
            # Kiểm tra FVG: nến hiện tại có bóng nến thứ 3 đi qua nến hiện tại
            if (current_candle['high'] < third_candle['low'] and 
                next_candle['high'] > current_candle['high']):
                
                fvg = {
                    'index': i,
                    'start_price': current_candle['high'],
                    'end_price': third_candle['low'],
                    'start_time': current_candle.name,
                    'end_time': third_candle.name,
                    'status': 'unfilled'
                }
                fvg_list.append(fvg)
        
        return fvg_list
    
    def identify_fvg_signals(self, df, fvg_list):
        """Nhận diện tín hiệu từ FVG"""
        signals = []
        
        for fvg in fvg_list:
            # Kiểm tra FVG đã được lấp đầy chưa
            current_price = df.iloc[-1]['close']
            
            if current_price > fvg['start_price']:
                fvg['status'] = 'filled_bullish'
                signals.append({
                    'type': 'FVG Fill',
                    'direction': 'bullish',
                    'price': fvg['start_price'],
                    'strength': 0.7
                })
            elif current_price < fvg['end_price']:
                fvg['status'] = 'filled_bearish'
                signals.append({
                    'type': 'FVG Fill',
                    'direction': 'bearish',
                    'price': fvg['end_price'],
                    'strength': 0.7
                })
        
        return signals