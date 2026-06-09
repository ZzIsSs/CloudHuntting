from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import pandas as pd

from .database import CloudMetricsLog
from .schemas import LogRequest, StatisticItem

def save_log(db: Session, request: LogRequest):
    """
    Lưu log từ Service 1 vào DB.
    """
    db_log = CloudMetricsLog(
        location_name=request.location_name,
        lat=request.lat,
        lon=request.lon,
        probability=request.probability,
        temperature_2m=request.weather_data.temperature_2m,
        relative_humidity_2m=request.weather_data.relative_humidity_2m,
        wind_speed_10m=request.weather_data.wind_speed_10m,
        pressure_msl=request.weather_data.pressure_msl,
        cloud_cover_low=request.weather_data.cloud_cover_low,
        cloud_cover_high=request.weather_data.cloud_cover_high,
        dew_point_2m=request.weather_data.dew_point_2m,
        timestamp=datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_statistics(db: Session, location_name: str, days: int) -> list[StatisticItem]:
    """
    Module 2 & 3: Lấy dữ liệu từ DB, tính trung bình theo ngày và định dạng trả về cho UI.
    """
    # Lấy thời điểm cắt (ví dụ: 30 ngày trước)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Lấy dữ liệu từ DB
    records = db.query(CloudMetricsLog).filter(
        CloudMetricsLog.location_name == location_name,
        CloudMetricsLog.timestamp >= cutoff_date
    ).all()
    
    if not records:
        return []
        
    # Chuyển thành Pandas DataFrame để dễ tính trung bình theo ngày
    df = pd.DataFrame([{
        'date': r.timestamp.date(),
        'probability': r.probability
    } for r in records])
    
    # Tính trung bình theo từng ngày
    daily_avg = df.groupby('date')['probability'].mean().reset_index()
    daily_avg = daily_avg.sort_values(by='date')
    
    # Tính toán Trend (xu hướng)
    results = []
    prev_prob = None
    for _, row in daily_avg.iterrows():
        prob = row['probability']
        trend = "Đi ngang"
        if prev_prob is not None:
            if prob > prev_prob + 5: # Chênh lệch > 5% coi như tăng
                trend = "Tăng"
            elif prob < prev_prob - 5:
                trend = "Giảm"
                
        results.append(StatisticItem(
            date=row['date'].strftime("%Y-%m-%d"),
            avg_probability=round(prob, 2),
            trend=trend
        ))
        prev_prob = prob
        
    return results

def cleanup_old_records(db: Session):
    """
    Module 4: Dọn dẹp dữ liệu cũ hơn 30 ngày.
    Hàm này sẽ được gọi tự động bởi APScheduler.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    deleted_count = db.query(CloudMetricsLog).filter(CloudMetricsLog.timestamp < cutoff_date).delete()
    db.commit()
    print(f"🧹 [Cleanup] Đã xóa {deleted_count} bản ghi cũ hơn 30 ngày.")
