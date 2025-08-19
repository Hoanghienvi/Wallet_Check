import asyncio
import logging
from datetime import datetime
import os
import sys

# Thêm đường dẫn hiện tại vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import các module cần thiết từ dự án
from utils.config import Config
from telegram_handler import TelegramHandler
from indicators.ta_signals import TechnicalSignals
from indicators.chart_plotter import ChartPlotter
from macro_data.macro_checker import MacroChecker
from weekly_forecast import WeeklyForecast
from category_analyzer import CategoryAnalyzer
from advanced_indicators import AdvancedIndicators

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CryptoMacroAlertBot:
    def __init__(self):
        self.telegram = TelegramHandler()
        self.ta_signals = TechnicalSignals()
        self.chart_plotter = ChartPlotter()
        self.macro_checker = MacroChecker()
        self.weekly_forecast = WeeklyForecast()
        self.category_analyzer = CategoryAnalyzer()
        self.advanced_indicators = AdvancedIndicators()
        
        # Để theo dõi các cảnh báo crypto đã gửi, tránh gửi lặp lại
        self.last_crypto_alerts_sent = {} # { (symbol, timeframe): last_alert_message_hash }
        self.last_macro_alerts_sent = set() # { event_id }

    def analyze_advanced_patterns(self, df, symbol, timeframe):
        """Phân tích các mẫu hình nâng cao"""
        analysis = self.advanced_indicators.analyze_all(df, symbol, timeframe)
        
        # Tổng hợp các tín hiệu
        signals = []
        
        # Fibonacci signals
        if analysis['fibonacci']['near_levels']:
            for level, price in analysis['fibonacci']['near_levels']:
                signals.append({
                    'type': 'Fibonacci',
                    'message': f"Giá đang gần mức Fibonacci {level} ({price:.2f})",
                    'strength': 0.6
                })
        
        # Pattern signals
        for pattern_name, pattern in analysis['patterns'].items():
            if pattern['detected']:
                signals.append({
                    'type': pattern['name'],
                    'message': f"Phát hiện {pattern['name']} với độ tin cậy {pattern['strength']*100:.0f}%",
                    'strength': pattern['strength']
                })
        
        # Elliott Wave signals
        if analysis['elliott_wave']['pattern']:
            signals.append({
                'type': 'Elliott Wave',
                'message': f"Mẫu hình sóng Elliott: {analysis['elliott_wave']['pattern']}",
                'strength': analysis['elliott_wave']['confidence']
            })
        
        # FVG signals
        fvg_signals = self.advanced_indicators.fvg.identify_fvg_signals(df, analysis['fvg'])
        for signal in fvg_signals:
            signals.append({
                'type': 'FVG',
                'message': f"Fair Value Gap {signal['direction']}",
                'strength': signal['strength']
            })
        
        # Candlestick signals
        for pattern_type, patterns in analysis['candlestick'].items():
            for pattern in patterns:
                signals.append({
                    'type': 'Candlestick',
                    'message': f"Mẫu nến {pattern['type']}",
                    'strength': pattern['strength']
                })
        
        # Support/Resistance signals
        for level in analysis['support_resistance']['support']:
            if abs(df['close'].iloc[-1] - level['price']) / df['close'].iloc[-1] < 0.02:
                signals.append({
                    'type': 'Support',
                    'message': f"Giá đang gần mức hỗ trợ {level['price']:.2f}",
                    'strength': level['strength']
                })
        
        for level in analysis['support_resistance']['resistance']:
            if abs(df['close'].iloc[-1] - level['price']) / df['close'].iloc[-1] < 0.02:
                signals.append({
                    'type': 'Resistance',
                    'message': f"Giá đang gần mức kháng cự {level['price']:.2f}",
                    'strength': level['strength']
                })
        
        # Trendline signals
        for trendline in analysis['trendlines']['uptrend']:
            signals.append({
                'type': 'Uptrend',
                'message': f"Đường xu hướng tăng được xác nhận",
                'strength': trendline['strength']
            })
        
        for trendline in analysis['trendlines']['downtrend']:
            signals.append({
                'type': 'Downtrend',
                'message': f"Đường xu hướng giảm được xác nhận",
                'strength': trendline['strength']
            })
        
        # Momentum signals
        momentum_signals = []
        
        # RSI signals
        rsi = analysis['momentum']['rsi']
        if rsi['signal'] == 'overbought':
            momentum_signals.append({
                'type': 'RSI Overbought',
                'message': f"RSI ở vùng quá mua ({rsi['current']:.2f})",
                'strength': 0.7,
                'direction': 'bearish'
            })
        elif rsi['signal'] == 'oversold':
            momentum_signals.append({
                'type': 'RSI Oversold',
                'message': f"RSI ở vùng quá bán ({rsi['current']:.2f})",
                'strength': 0.7,
                'direction': 'bullish'
            })
        
        # MACD signals
        macd = analysis['momentum']['macd']
        if macd['signal'] == 'bullish':
            momentum_signals.append({
                'type': 'MACD Bullish',
                'message': "MACD có tín hiệu tăng",
                'strength': 0.6,
                'direction': 'bullish'
            })
        elif macd['signal'] == 'bearish':
            momentum_signals.append({
                'type': 'MACD Bearish',
                'message': "MACD có tín hiệu giảm",
                'strength': 0.6,
                'direction': 'bearish'
            })
        
        # Volume signals
        for volume_signal in analysis['volume']['volume_signals']:
            signals.append({
                'type': volume_signal['type'],
                'message': volume_signal['message'],
                'strength': volume_signal['strength']
            })
        
        return signals, momentum_signals
    
    async def run_check(self):
        logging.info("Bắt đầu chu kỳ kiểm tra cảnh báo...")

        # --- 1. Kiểm tra Macro Data ---
        macro_alerts = self.macro_checker.get_new_macro_alerts()
        for alert_message in macro_alerts:
            # So sánh với các cảnh báo đã gửi để tránh lặp
            # Để đơn giản, ta dựa vào việc event_id đã được thêm vào notified_macro_events trong MacroChecker
            await self.telegram.send_message(alert_message)

        # --- 2. Kiểm tra Crypto Data ---
        for symbol in Config.SYMBOLS:
            for timeframe in Config.TIMEFRAMES:
                logging.info(f"📊 Đang xử lý Crypto {symbol}-{timeframe}")

                df = self.ta_signals.get_klines(symbol, timeframe, limit=100) 
                
                if df.empty:
                    logging.warning(f"❌ Không lấy được dữ liệu cho {symbol}-{timeframe}")
                    continue
                
                # Kiểm tra dữ liệu có đủ nến không
                if len(df) < 100:
                    logging.warning(f"❌ Dữ liệu không đủ cho {symbol}-{timeframe} (cần ít nhất 100 nến)")
                    continue
                
                # Kiểm tra dữ liệu có giá trị NaN không
                if df.isnull().values.any():
                    logging.warning(f"⚠️ Dữ liệu có giá trị NaN cho {symbol}-{timeframe}")
                    df = df.fillna(method='ffill')  # Điền giá trị NaN bằng giá trị trước đó

                df_with_indicators = self.ta_signals.calculate_indicators(df, symbol, timeframe) 

                if df_with_indicators.empty or df_with_indicators.isnull().all().all():
                    logging.warning(f"⚠️ Không thể tính toán chỉ báo cho {symbol}-{timeframe} hoặc dữ liệu chỉ báo toàn NaN.")
                    continue

                alert_message = ""
                confirmation_count = 0
                alert_strength = "YẾU"
                
                # Lấy dữ liệu nến cuối cùng để kiểm tra tín hiệu
                latest_data = df_with_indicators.iloc[-1]
                prev_data = df_with_indicators.iloc[-2] if len(df_with_indicators) > 1 else None

                # Kiểm tra RSI
                if 'rsi' in latest_data:
                    latest_rsi = latest_data['rsi']
                    # Lấy cấu hình cho cặp tiền
                    symbol_config = Config.SYMBOL_CONFIGS.get(symbol, Config.SYMBOL_CONFIGS['DEFAULT'])
                    rsi_oversold = symbol_config.get('rsi_oversold', Config.RSI_OVERSOLD_THRESHOLD)
                    rsi_overbought = symbol_config.get('rsi_overbought', Config.RSI_OVERBOUGHT_THRESHOLD)
                    
                    # Cảnh báo RSI quá bán
                    if latest_rsi < rsi_oversold:
                        alert_message += f"- RSI ({latest_rsi:.2f}) quá bán ({rsi_oversold}).\n"
                        confirmation_count += 1
                        alert_strength = "TRUNG BÌNH"
                    
                    # Cảnh báo RSI quá mua
                    elif latest_rsi > rsi_overbought:
                        alert_message += f"- RSI ({latest_rsi:.2f}) quá mua ({rsi_overbought}).\n"
                        confirmation_count += 1
                        alert_strength = "TRUNG BÌNH"

                # ... (các phần kiểm tra khác không đổi)

                # 4. Gửi cảnh báo nếu có tín hiệu VÀ tín hiệu là MỚI
                if alert_message and confirmation_count >= 2:  # Yêu cầu ít nhất 2 chỉ báo xác nhận
                    current_message_hash = hash(alert_message) # Tạo hash từ nội dung tin nhắn
                    
                    # Chỉ gửi nếu tin nhắn cảnh báo khác với lần cuối cùng gửi cho cặp/khung thời gian này
                    if self.last_crypto_alerts_sent.get((symbol, timeframe)) != current_message_hash:
                        current_time_str = datetime.now().strftime("%Y%m%d%H%M%S")
                        chart_filename = f"{symbol}_{timeframe}_alert_{current_time_str}.png"
                        chart_path = self.chart_plotter.plot_chart(df_with_indicators, symbol, timeframe, chart_filename)

                        full_message = (
                            f"📈 *Cảnh báo Crypto: {symbol} - {timeframe}*\n"
                            f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                            f"⚡️ *Tín hiệu ({confirmation_count} chỉ báo xác nhận):*\n{alert_message}\n"
                            f"💪 *Độ mạnh:* {alert_strength}\n"
                            f"\\#CryptoAlert \\#{symbol} \\#{timeframe}"
                        )

                        if chart_path:
                            await self.telegram.send_photo(chart_path, caption=full_message)
                            # Xóa ảnh sau khi gửi để tránh đầy bộ nhớ
                            try:
                                os.remove(chart_path)
                                logging.info(f"Đã xóa file ảnh: {chart_path}")
                            except OSError as e:
                                logging.error(f"Lỗi khi xóa file ảnh {chart_path}: {e}")
                        else:
                            await self.telegram.send_message(full_message)
                        
                        # Cập nhật hash của tin nhắn đã gửi
                        self.last_crypto_alerts_sent[(symbol, timeframe)] = current_message_hash
                else:
                    logging.info(f"Không có tín hiệu cảnh báo mới cho {symbol}-{timeframe}.")
                    # Reset hash nếu không có cảnh báo nào, để lần sau nếu có cảnh báo lại sẽ gửi
                    self.last_crypto_alerts_sent[(symbol, timeframe)] = None
                
                # Phân tích các mẫu hình nâng cao
                advanced_signals, momentum_signals = self.analyze_advanced_patterns(df_with_indicators, symbol, timeframe)
                
                if advanced_signals or momentum_signals:
                    advanced_message = "🔍 *MẪU HÌNH NÂNG CAO*\n\n"
                    
                    # Thêm các tín hiệu nâng cao
                    for signal in advanced_signals:
                        strength_emoji = "🔴" if signal['strength'] > 0.7 else "🟡" if signal['strength'] > 0.5 else "🟢"
                        advanced_message += f"{strength_emoji} {signal['type']}: {signal['message']}\n"
                    
                    # Thêm các tín hiệu động lượng
                    if momentum_signals:
                        advanced_message += "\n📊 *CHỈ BÁO ĐỘNG LƯỢNG*\n\n"
                        for signal in momentum_signals:
                            direction_emoji = "📈" if signal['direction'] == 'bullish' else "📉"
                            advanced_message += f"{direction_emoji} {signal['type']}: {signal['message']}\n"
                    
                    # Gửi cảnh báo nâng cao
                    await self.telegram.send_message(advanced_message)

        # Gửi báo cáo category hàng ngày
        if Config.CATEGORY_REPORT_ENABLED:
            await self.category_analyzer.send_category_report()

        # Gửi dự báo tuần vào Chủ Nhật
        await self.weekly_forecast.send_weekly_forecast()

        logging.info("Kết thúc chu kỳ kiểm tra cảnh báo.")


async def main():
    bot = CryptoMacroAlertBot()
    
    # Chạy hệ thống phân tích category trong background
    if Config.CATEGORY_REPORT_ENABLED:
        asyncio.create_task(bot.category_analyzer.run_category_monitor())
    
    # Chạy dự báo tuần trong background
    asyncio.create_task(bot.weekly_forecast.run_weekly_monitor())
    
    # Chạy lần đầu ngay lập tức
    await bot.run_check()
    
    # Sau đó chạy lặp lại sau mỗi khoảng thời gian định cấu hình
    while True:
        logging.info(f"Đang chờ {Config.CHECK_INTERVAL_MINUTES} phút cho chu kỳ kiểm tra tiếp theo...")
        await asyncio.sleep(Config.CHECK_INTERVAL_MINUTES * 60) # Chuyển phút sang giây
        await bot.run_check()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot đã dừng bởi người dùng.")
    except Exception as e:
        logging.error(f"Lỗi nghiêm trọng xảy ra: {e}", exc_info=True)