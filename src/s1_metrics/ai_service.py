import joblib
import pandas as pd
import os
from typing import Dict, Any, Tuple

# Đường dẫn tương đối tới file model (chạy từ thư mục gốc dự án)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "cloud_model.pkl")

# Biến global lưu model để load 1 lần duy nhất khi khởi động
_model = None

def load_model():
    """
    Load mô hình RandomForestClassifier vào RAM.
    """
    global _model
    if _model is None:
        try:
            _model = joblib.load(MODEL_PATH)
            print(f"[SUCCESS] Đã load mô hình AI thành công từ {MODEL_PATH}")
        except Exception as e:
            print(f"[ERROR] Lỗi khi load mô hình AI: {e}")
            _model = None

from typing import List

def predict_cloud_probability(weather_window: List[Dict[str, Any]]) -> Tuple[float, str, str, list]:
    """
    Nhận vào mảng dữ liệu thời tiết (từng giờ).
    Dự đoán xác suất cho tất cả các giờ, tìm giờ có xác suất cao nhất.
    Trả về (max_prob, best_time, suggestion, timeline)
    timeline = [{time, probability}, ...] cho toàn bộ các giờ
    """
    if _model is None:
        load_model()
        
    if _model is None:
        raise RuntimeError("Mô hình AI chưa sẵn sàng.")

    # Chuẩn bị dữ liệu cho tất cả các giờ
    temps = []
    humidities = []
    winds = []
    low_clouds = []
    high_clouds = []
    pressures = []
    spreads = []
    times = []

    for w in weather_window:
        temp = w.get("temperature_2m", 0)
        dew = w.get("dew_point_2m", 0)
        spread = temp - dew
        
        temps.append(temp)
        humidities.append(w.get("relative_humidity_2m", 0))
        winds.append(w.get("wind_speed_10m", 0))
        low_clouds.append(w.get("cloud_cover_low", 0))
        high_clouds.append(w.get("cloud_cover_high", 0))
        pressures.append(w.get("pressure_msl", 0))
        spreads.append(spread)
        
        # Format lại giờ cho dễ nhìn (VD: "2023-10-01T06:00" -> "06:00 01/10")
        try:
            dt = pd.to_datetime(w.get("time", ""))
            times.append(dt.strftime("%H:%M %d/%m"))
        except:
            times.append(w.get("time", "Unknown"))

    features = [
        'temperature_2m', 'relative_humidity_2m', 'wind_speed_10m',
        'cloud_cover_low', 'cloud_cover_high', 'pressure_msl', 'spread'
    ]
    
    input_data = {
        'temperature_2m': temps,
        'relative_humidity_2m': humidities,
        'wind_speed_10m': winds,
        'cloud_cover_low': low_clouds,
        'cloud_cover_high': high_clouds,
        'pressure_msl': pressures,
        'spread': spreads
    }
    
    df_input = pd.DataFrame(input_data, columns=features)
    
    # Dự đoán cho toàn bộ DataFrame (tất cả các giờ) cùng lúc
    probabilities = _model.predict_proba(df_input)
    
    # Lấy xác suất lớp 1 (có mây)
    prob_class_1 = probabilities[:, 1] * 100
    
    # Xây dựng timeline: mảng [{time, probability}] cho toàn bộ các giờ
    timeline = []
    for i in range(len(prob_class_1)):
        timeline.append({
            "time": times[i],
            "probability": round(float(prob_class_1[i]), 2)
        })
    
    # Tìm max
    max_idx = prob_class_1.argmax()
    max_prob = prob_class_1[max_idx]
    best_time = times[max_idx]
    
    # Sinh lời khuyên dựa trên xác suất cao nhất
    if max_prob >= 80:
        suggestion = "Thời tiết cực kỳ lý tưởng! Khả năng cao sẽ có biển mây tuyệt đẹp."
    elif max_prob >= 50:
        suggestion = "Tỷ lệ có mây ở mức khá. Rất đáng để thử nghiệm."
    elif max_prob >= 20:
        suggestion = "Xác suất có mây thấp. Hãy cân nhắc kỹ."
    else:
        suggestion = "Không thuận lợi để săn mây. Lớp nghịch nhiệt có thể đã bị phá vỡ."

    return round(max_prob, 2), best_time, suggestion, timeline

