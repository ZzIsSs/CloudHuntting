from apscheduler.schedulers.background import BackgroundScheduler
from .nearby_service import HOTSPOTS
from .routes import send_log_to_service_5
from .weather_service import WeatherService
from .ai_service import predict_cloud_probability
from datetime import datetime

def auto_scan_hotspots():
    print(f"\n[BOT] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Đang tự động quét dự báo cho 10 HOTSPOTS...")
    for spot in HOTSPOTS:
        try:
            # Lấy thời tiết hiện tại (forecast_hours=0)
            weather_window = WeatherService.get_weather_window(spot["lat"], spot["lon"], 0)
            
            # Dự đoán
            probability, best_time, suggestion, _timeline = predict_cloud_probability(weather_window)
            
            w = weather_window[0] if weather_window else {}
            weather_payload = {
                "temperature_2m": w.get("temperature_2m", 0),
                "relative_humidity_2m": w.get("relative_humidity_2m", 0),
                "wind_speed_10m": w.get("wind_speed_10m", 0),
                "pressure_msl": w.get("pressure_msl", 0),
                "cloud_cover_low": w.get("cloud_cover_low", 0),
                "cloud_cover_high": w.get("cloud_cover_high", 0),
                "dew_point_2m": w.get("dew_point_2m", 0),
            }
            
            send_log_to_service_5({
                "location_name": spot["name"],
                "lat": spot["lat"],
                "lon": spot["lon"],
                "probability": probability,
                "weather_data": weather_payload
            })
        except Exception as e:
            print(f"[BOT] Lỗi khi xử lý {spot['name']}: {e}")
    print("[BOT] Hoàn thành quá trình quét.\n")

# Biến global lưu trữ scheduler
scheduler = BackgroundScheduler()

def start_bot():
    """Khởi động Bot lập lịch"""
    # Chạy lặp lại mỗi 3 giờ
    scheduler.add_job(auto_scan_hotspots, "interval", hours=3)
    scheduler.start()
    print("[INFO] Đã khởi động Bot tự động quét mỗi 3 giờ.")

    # Chạy ngay lần đầu tiên lúc khởi động
    scheduler.add_job(auto_scan_hotspots, "date")
