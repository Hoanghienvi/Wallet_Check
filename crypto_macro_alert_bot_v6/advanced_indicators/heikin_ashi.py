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

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CryptoMacroAlertBot:
    def __init__(self):
        self.telegram = TelegramHandler()
        self.ta_signals = TechnicalSignals()
        self.chart_plotter = ChartPlotter()
        self.macro_checker = MacroChecker()
        self.weekly_forecast = WeeklyForecast()
        
        # Để theo dõi các cảnh báo crypto đã gửi, tránh gửi lặp lại
        self.last_crypto_alerts_sent = {} # { (symbol, timeframe): last_alert_message_hash }
        self.last_macro_alerts_sent = set() # { event_id }

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

                # Kiểm tra MACD
                if 'macd_diff' in latest_data and prev_data is not None:
                    latest_macd_diff = latest_data['macd_diff']
                    prev_macd_diff = prev_data['macd_diff']
                    
                    # Lấy cấu hình cho cặp tiền
                    symbol_config = Config.SYMBOL_CONFIGS.get(symbol, Config.SYMBOL_CONFIGS['DEFAULT'])
                    
                    # Cảnh báo MACD giao cắt lên (tín hiệu mua tiềm năng)
                    if prev_macd_diff < 0 and latest_macd_diff > 0:
                        alert_message += "- MACD giao cắt lên (tín hiệu mua tiềm năng).\n"
                        confirmation_count += 1
                        alert_strength = "MẠNH"
                    
                    # Cảnh báo MACD giao cắt xuống (tín hiệu bán tiềm năng)
                    if prev_macd_diff > 0 and latest_macd_diff < 0:
                        alert_message += "- MACD giao cắt xuống (tín hiệu bán tiềm năng).\n"
                        confirmation_count += 1
                        alert_strength = "MẠNH"
                    
                    # Kiểm tra phân kỳ MACD
                    # Phân kỳ tăng (bullish divergence)
                    if (latest_data['low'] < prev_data['low'] and 
                        latest_macd_diff > prev_macd_diff):
                        alert_message += "- MACD phân kỳ tăng (tiềm năng tăng giá).\n"
                        confirmation_count += 1
                        alert_strength = "MẠNH"
                    
                    # Phân kỳ giảm (bearish divergence)
                    elif (latest_data['high'] > prev_data['high'] and 
                          latest_macd_diff < prev_macd_diff):
                        alert_message += "- MACD phân kỳ giảm (tiềm năng giảm giá).\n"
                        confirmation_count += 1
                        alert_strength = "MẠNH"

                # Kiểm tra EMA crossover
                if 'ema_cross_signal' in latest_data and latest_data['ema_cross_signal'] != 0:
                    alert_message += "- EMA giao cắt.\n"
                    confirmation_count += 1
                    alert_strength = "MẠNH"
                
                # Kiểm tra Bollinger Bands
                if 'bb_percent' in latest_data:
                    latest_bb_percent = latest_data['bb_percent']
                    if latest_bb_percent <= 0:
                        alert_message += "- Giá chạm Bollinger Bands dưới.\n"
                        confirmation_count += 1
                        alert_strength = "TRUNG BÌNH"
                    elif latest_bb_percent >= 1:
                        alert_message += "- Giá chạm Bollinger Bands trên.\n"
                        confirmation_count += 1
                        alert_strength = "TRUNG BÌNH"
                
                # Kiểm tra Stochastic
                if 'stoch_k' in latest_data and 'stoch_d' in latest_data:
                    latest_stoch_k = latest_data['stoch_k']
                    latest_stoch_d = latest_data['stoch_d']
                    
                    # Cảnh báo Stochastic quá bán
                    if latest_stoch_k < 20 and latest_stoch_d < 20:
                        alert_message += "- Stochastic quá bán.\n"
                        confirmation_count += 1
                        alert_strength = "TRUNG BÌNH"
                    
                    # Cảnh báo Stochastic quá mua
                    elif latest_stoch_k > 80 and latest_stoch_d > 80:
                        alert_message += "- Stochastic quá mua.\n"
                        confirmation_count += 1
                        alert_strength = "TRUNG BÌNH"
                    
                    # Cảnh báo Stochastic crossover
                    if prev_data is not None:
                        prev_stoch_k = prev_data['stoch_k']
                        prev_stoch_d = prev_data['stoch_d']
                        
                        # Stochastic crossover lên
                        if prev_stoch_k < prev_stoch_d and latest_stoch_k > latest_stoch_d:
                            alert_message += "- Stochastic crossover lên.\n"
                            confirmation_count += 1
                            alert_strength = "MẠNH"
                        
                        # Stochastic crossover xuống
                        elif prev_stoch_k > prev_stoch_d and latest_stoch_k < latest_stoch_d:
                            alert_message += "- Stochastic crossover xuống.\n"
                            confirmation_count += 1
                            alert_strength = "MẠNH"

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

        # Gửi dự báo tuần vào Chủ Nhật
        await self.weekly_forecast.send_weekly_forecast()

        logging.info("Kết thúc chu kỳ kiểm tra cảnh báo.")


async def main():
    bot = CryptoMacroAlertBot()
    
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
