from .fibonacci import FibonacciAnalyzer
from .patterns import PatternRecognizer
from .elliot_wave import ElliotWaveAnalyzer
from .fair_value_gap import FairValueGapAnalyzer
from .candlestick_patterns import CandlestickPatternRecognizer
from .support_resistance import SupportResistanceAnalyzer
from .trendlines import TrendlineAnalyzer
from .gann_angles import GannAngleAnalyzer
from .momentum_oscillators import MomentumOscillatorAnalyzer
from .volume_analysis import VolumeAnalyzer

class AdvancedIndicators:
    def __init__(self):
        self.fibonacci = FibonacciAnalyzer()
        self.patterns = PatternRecognizer()
        self.elliott_wave = ElliotWaveAnalyzer()
        self.fvg = FairValueGapAnalyzer()
        self.candlestick = CandlestickPatternRecognizer()
        self.support_resistance = SupportResistanceAnalyzer()
        self.trendlines = TrendlineAnalyzer()
        self.gann = GannAngleAnalyzer()
        self.momentum = MomentumOscillatorAnalyzer()
        self.volume = VolumeAnalyzer()
    
    def analyze_all(self, df, symbol, timeframe):
        """Phân tích tất cả các chỉ báo nâng cao"""
        analysis = {
            'fibonacci': self.fibonacci.identify_fibonacci_retracement(df, symbol, timeframe),
            'patterns': {
                'head_and_shoulders': self.patterns.identify_head_and_shoulders(df),
                'double_top': self.patterns.identify_double_top(df),
                'double_bottom': self.patterns.identify_double_bottom(df),
                'triangle': self.patterns.identify_triangle(df),
                'wedge': self.patterns.identify_wedge(df)
            },
            'elliott_wave': self.elliott_wave.identify_elliott_waves(df),
            'fvg': self.fvg.calculate_fvg(df),
            'candlestick': {
                'doji': self.candlestick.identify_doji(df),
                'hammer': self.candlestick.identify_hammer(df),
                'shooting_star': self.candlestick.identify_shooting_star(df),
                'engulfing': self.candlestick.identify_engulfing(df),
                'harami': self.candlestick.identify_harami(df)
            },
            'support_resistance': self.support_resistance.find_levels(df),
            'trendlines': self.trendlines.draw_trendlines(df),
            'gann': self.gann.calculate_gann_angles(df),
            'momentum': self.momentum.calculate_indicators(df),
            'volume': self.volume.analyze_volume(df)
        }
        
        return analysis