from apscheduler.schedulers.background import BackgroundScheduler
from .nearby_service import HOTSPOTS
from .weather_service import WeatherService
from .ai_service import predict_cloud_probability
from datetime import datetime, timedelta, timezone

VN_TZ = timezone(timedelta(hours=7))
import requests
import os

def send_forecast_to_service_5(spot: dict, weather_window: list):
    """
    Gửi toàn bộ chuỗi dự báo (batch) về S5.
    Mỗi giờ trong weather_window trở thành 1 bản ghi riêng trong DB.
    """
    now_vn = datetime.now(VN_TZ)
    payload_list = []
    
    for w in weather_window:
        try:
            forecast_for = datetime.strptime(w["time"], "%Y-%m-%dT%H:%M")
        except ValueError:
            # Fallback if time format is unexpected
            forecast_for = now_vn
            
        # Xác định record_type dựa trên khoảng cách so với hiện tại
        delta_hours = (forecast_for - now_vn).total_seconds() / 3600
        if delta_hours < -1:
            record_type = "historical"
        elif delta_hours <= 1:
            record_type = "current"
        elif delta_hours <= 24:
            record_type = "forecast_d1"
        elif delta_hours <= 48:
            record_type = "forecast_d2"
        elif delta_hours <= 72:
            record_type = "forecast_d3"
        else:
            record_type = "forecast_d4"

        # Chạy AI predict cho từng giờ
        prob, _, _, _ = predict_cloud_probability([w])

        payload_list.append({
            "location_name": spot["name"],
            "lat": spot["lat"],
            "lon": spot["lon"],
            "probability": prob,
            "forecast_for": forecast_for.isoformat(),
            "record_type": record_type,
            "weather_data": {
                "temperature_2m": w.get("temperature_2m", 0),
                "relative_humidity_2m": w.get("relative_humidity_2m", 0),
                "wind_speed_10m": w.get("wind_speed_10m", 0),
                "pressure_msl": w.get("pressure_msl", 0),
                "cloud_cover_low": w.get("cloud_cover_low", 0),
                "cloud_cover_high": w.get("cloud_cover_high", 0),
                "dew_point_2m": w.get("dew_point_2m", 0),
            }
        })

    # Gửi batch lên S5
    try:
        s5_url = os.getenv('S5_URL', 'http://127.0.0.1:8005')
        requests.post(
            f"{s5_url}/api/s5/log-batch",
            json={"logs": payload_list},
            timeout=10
        )
    except Exception as e:
        print(f"[BOT] Error sending batch to S5: {e}")

def auto_scan_hotspots():
    print(f"\n[BOT] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Scanning 4-day forecast for {len(HOTSPOTS)} hotspots...")
    for spot in HOTSPOTS:
        try:
            # Lấy toàn bộ 4 ngày dự báo (96 datapoints/hotspot)
            weather_window = WeatherService.get_weather_window(spot["lat"], spot["lon"], 96)
            
            # Gửi TOÀN BỘ 96 giờ về S5 theo dạng batch
            if weather_window:
                send_forecast_to_service_5(spot, weather_window)
        except Exception as e:
            print(f"[BOT] Error processing {spot['name']}: {e}")
    print("[BOT] Scan completed.\n")

# Biến global lưu trữ scheduler
scheduler = BackgroundScheduler()

def start_bot():
    """Khởi động Bot lập lịch"""
    # Chạy lặp lại mỗi 1 giờ để dữ liệu luôn tươi mới
    scheduler.add_job(auto_scan_hotspots, "interval", hours=1)
    scheduler.start()
    print("[INFO] Started auto-scan bot every 1 hour.")

    # Chạy ngay lần đầu tiên lúc khởi động
    scheduler.add_job(auto_scan_hotspots, "date")
