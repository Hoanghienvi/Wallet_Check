import pandas as pd
import numpy as np

class VolumeAnalyzer:
    def __init__(self):
        self.volume_signals = []
    
    def analyze_volume(self, df):
        """Phân tích khối lượng giao dịch"""
        volume_analysis = {
            'volume_profile': self.calculate_volume_profile(df),
            'obv': self.calculate_obv(df),
            'volume_sma': self.calculate_volume_sma(df),
            'volume_signals': self.identify_volume_signals(df)
        }
        
        return volume_analysis
    
    def calculate_volume_profile(self, df):
        """Tính toán Volume Profile"""
        # Chia giá thành các mức
        price_range = df['high'].max() - df['low'].min()
        price_levels = np.linspace(df['low'].min(), df['high'].max(), 20)
        
        # Tính toán khối lượng tại mỗi mức giá
        volume_profile = []
        for i in range(len(price_levels) - 1):
            lower = price_levels[i]
            upper = price_levels[i + 1]
            
            # Tổng khối lượng trong khoảng giá
            volume = df[(df['close'] >= lower) & (df['close'] < upper)]['volume'].sum()
            
            volume_profile.append({
                'price_range': f"{lower:.2f}-{upper:.2f}",
                'volume': volume,
                'high_volume': volume > df['volume'].mean() * 1.5
            })
        
        return volume_profile
    
    def calculate_obv(self, df):
        """Tính toán On-Balance Volume (OBV)"""
        obv = np.zeros(len(df))
        
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv[i] = obv[i-1] + df['volume'].iloc[i]
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv[i] = obv[i-1] - df['volume'].iloc[i]
            else:
                obv[i] = obv[i-1]
        
        return pd.Series(obv, index=df.index)
    
    def calculate_volume_sma(self, df):
        """Tính toán SMA của khối lượng"""
        volume_sma_20 = df['volume'].rolling(window=20).mean()
        volume_sma_50 = df['volume'].rolling(window=50).mean()
        
        return {
            'sma_20': volume_sma_20,
            'sma_50': volume_sma_50,
            'current_volume': df['volume'].iloc[-1],
            'current_sma_20': volume_sma_20.iloc[-1],
            'current_sma_50': volume_sma_50.iloc[-1]
        }
    
    def identify_volume_signals(self, df):
        """Nhận diện tín hiệu từ khối lượng"""
        signals = []
        
        # Tính toán OBV
        obv = self.calculate_obv(df)
        
        # So sánh giá và OBV
        price_trend = df['close'].iloc[-1] > df['close'].iloc[-2]
        obv_trend = obv.iloc[-1] > obv.iloc[-2]
        
        if price_trend and not obv_trend:
            signals.append({
                'type': 'Divergence',
                'message': 'Giá tăng nhưng OBV giảm - Divergence giảm giá',
                'strength': 0.8,
                'direction': 'bearish'
            })
        elif not price_trend and obv_trend:
            signals.append({
                'type': 'Divergence',
                'message': 'Giá giảm nhưng OBV tăng - Divergence tăng giá',
                'strength': 0.8,
                'direction': 'bullish'
            })
        
        # Kiểm tra volume breakout
        volume_sma_20 = df['volume'].rolling(window=20).mean()
        current_volume = df['volume'].iloc[-1]
        
        if current_volume > volume_sma_20.iloc[-1] * 2:
            signals.append({
                'type': 'Volume Breakout',
                'message': 'Khối lượng tăng đột biến',
                'strength': 0.7,
                'direction': 'bullish' if price_trend else 'bearish'
            })
        
        return signals