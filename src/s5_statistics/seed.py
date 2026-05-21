import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import os

from .database import SessionLocal, CloudMetricsLog, init_db

# Đường dẫn file CSV ở thư mục ngoài
CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "AI_CHI_ĐàLạt", "AI", "historical_weather.csv"))

def seed_data():
    print("🌱 Bắt đầu nạp dữ liệu mồi (Seeding Data)...")
    init_db()
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ Không tìm thấy file {CSV_PATH}. Vui lòng kiểm tra lại.")
        return

    df = pd.read_csv(CSV_PATH)
    df['time'] = pd.to_datetime(df['time'])
    
    # Tìm ngày mới nhất trong file
    max_date = df['time'].max()
    print(f"📅 Ngày mới nhất trong file CSV: {max_date}")
    
    # Lấy mốc 30 ngày lùi lại
    cutoff_date = max_date - timedelta(days=30)
    print(f"📅 Lọc dữ liệu từ ngày: {cutoff_date} đến {max_date}")
    
    # Lọc dữ liệu 30 ngày gần nhất
    df_30d = df[df['time'] >= cutoff_date]
    
    # Giả lập tỷ lệ % (vì file csv chỉ có nhãn 0/1, ta sẽ nhân nhãn với 80-95% nếu =1, hoặc 10-30% nếu =0 cho chân thực)
    import numpy as np
    np.random.seed(42)
    df_30d = df_30d.copy()
    
    def fake_prob(val):
        if val == 1:
            return float(np.random.randint(80, 98))
        else:
            return float(np.random.randint(5, 40))
            
    df_30d['probability'] = df_30d['is_cloud_hunting_good'].apply(fake_prob)

    db: Session = SessionLocal()
    
    # Kiểm tra xem đã có dữ liệu chưa
    existing_count = db.query(CloudMetricsLog).count()
    if existing_count > 0:
        print("⚠️ Database đã có dữ liệu, sẽ xóa toàn bộ để làm mới...")
        db.query(CloudMetricsLog).delete()
        db.commit()

    logs = []
    # Lưu ý: Cột location trong CSV chứa tên địa điểm, ta map nó vào location_name
    # Các giá trị lat, lon không có trong csv nhưng không sao, S5 không vẽ bản đồ
    for _, row in df_30d.iterrows():
        # Điều chỉnh timestamp lùi về đúng thời điểm hiện tại của máy để dễ test
        # Tính delta: max_date -> datetime.utcnow()
        delta = datetime.utcnow() - max_date
        adjusted_time = row['time'] + delta
        
        log = CloudMetricsLog(
            location_name=row['location'],
            lat=0.0,
            lon=0.0,
            probability=row['probability'],
            temperature_2m=row['temperature_2m'],
            relative_humidity_2m=row['relative_humidity_2m'],
            wind_speed_10m=row['wind_speed_10m'],
            pressure_msl=row['pressure_msl'],
            cloud_cover_low=row['cloud_cover_low'],
            cloud_cover_high=row['cloud_cover_high'],
            dew_point_2m=row['dew_point_2m'],
            timestamp=adjusted_time
        )
        logs.append(log)
        
    db.add_all(logs)
    db.commit()
    db.close()
    
    print(f"✅ Đã nạp thành công {len(logs)} bản ghi vào Database (đã điều chỉnh timestamp theo thời gian thực)!")

if __name__ == "__main__":
    seed_data()
