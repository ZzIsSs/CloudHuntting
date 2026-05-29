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
            print(f"✅ Đã load mô hình AI thành công từ {MODEL_PATH}")
        except Exception as e:
            print(f"❌ Lỗi khi load mô hình AI: {e}")
            _model = None

def predict_cloud_probability(weather_data: Dict[str, Any]) -> Tuple[float, str]:
    """
    Module 3: Tính toán thông số săn mây.
    Dự đoán tỷ lệ săn mây thành công dựa trên dữ liệu thời tiết.
    """
    if _model is None:
        load_model()
        
    if _model is None:
        raise RuntimeError("Mô hình AI chưa sẵn sàng.")

    # Feature Engineering (giống trong data_pipeline.py)
    # Tính toán spread
    temp = weather_data.get("temperature_2m", 0)
    dew_point = weather_data.get("dew_point_2m", 0)
    spread = temp - dew_point

    # Xây dựng DataFrame 1 dòng (1 row) với đúng thứ tự features khi train
    features = [
        'temperature_2m',
        'relative_humidity_2m',
        'wind_speed_10m',
        'cloud_cover_low',
        'cloud_cover_high',
        'pressure_msl',
        'spread'
    ]
    
    input_data = {
        'temperature_2m': [temp],
        'relative_humidity_2m': [weather_data.get('relative_humidity_2m', 0)],
        'wind_speed_10m': [weather_data.get('wind_speed_10m', 0)],
        'cloud_cover_low': [weather_data.get('cloud_cover_low', 0)],
        'cloud_cover_high': [weather_data.get('cloud_cover_high', 0)],
        'pressure_msl': [weather_data.get('pressure_msl', 0)],
        'spread': [spread]
    }
    
    df_input = pd.DataFrame(input_data, columns=features)
    
    # Lấy xác suất của class '1' (có biển mây)
    # predict_proba trả về mảng [[prob_0, prob_1]]
    probabilities = _model.predict_proba(df_input)
    prob_cloud = probabilities[0][1] * 100 # Chuyển sang %
    
    # Sinh lời khuyên dựa trên xác suất
    if prob_cloud >= 80:
        suggestion = "Thời tiết cực kỳ lý tưởng! Khả năng cao sẽ có biển mây tuyệt đẹp. Hãy chuẩn bị máy ảnh và áo ấm ngay nhé."
    elif prob_cloud >= 50:
        suggestion = "Tỷ lệ có mây ở mức khá. Có thể mây sẽ không quá dày hoặc gió hơi mạnh, nhưng vẫn rất đáng để thử nghiệm."
    elif prob_cloud >= 20:
        suggestion = "Xác suất có mây thấp. Trời có thể quang đãng hoặc sương mù dày đặc (không ngưng tụ thành mây). Hãy cân nhắc kỹ."
    else:
        suggestion = "Không thuận lợi để săn mây hôm nay. Lớp nghịch nhiệt có thể đã bị phá vỡ hoặc trời mưa."

    return round(prob_cloud, 2), suggestion
