from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import pandas as pd

from .database import CloudMetricsLog
from .schemas import LogRequest, StatisticItem, BatchLogItem, ForecastItem, ConfidenceInfo, ForecastResponse

def save_log(db: Session, request: LogRequest):
    """
    Lưu log từ Service 1 vào DB (giữ nguyên cho tương thích ngược).
    """
    # Nếu forecast_for không có, dùng thời điểm hiện tại
    forecast_time = datetime.fromisoformat(request.forecast_for) if request.forecast_for else datetime.utcnow()
    
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
        created_at=datetime.utcnow(),
        forecast_for=forecast_time,
        record_type=request.record_type
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def save_log_batch(db: Session, logs: list[BatchLogItem]):
    """
    UPSERT batch: Nhận từ Bot S1. 
    Nếu bản ghi (location_name + forecast_for) đã tồn tại thì cập nhật, ngược lại tạo mới.
    Thực hiện trong 1 transaction duy nhất để tối ưu SQLite.
    """
    now = datetime.utcnow()
    
    for log_data in logs:
        # Xử lý UTC từ ISO string (bỏ timezone Z nếu có)
        try:
            forecast_time = datetime.fromisoformat(log_data.forecast_for.replace('Z', ''))
        except ValueError:
            forecast_time = datetime.fromisoformat(log_data.forecast_for)
            
        # Tìm bản ghi hiện có
        existing = db.query(CloudMetricsLog).filter(
            CloudMetricsLog.location_name == log_data.location_name,
            CloudMetricsLog.forecast_for == forecast_time
        ).first()

        if existing:
            # Cập nhật (ghi đè dự báo cũ bằng dự báo mới nhất)
            existing.probability = log_data.probability
            existing.created_at = now
            existing.record_type = log_data.record_type
            existing.temperature_2m = log_data.weather_data.temperature_2m
            existing.relative_humidity_2m = log_data.weather_data.relative_humidity_2m
            existing.wind_speed_10m = log_data.weather_data.wind_speed_10m
            existing.pressure_msl = log_data.weather_data.pressure_msl
            existing.cloud_cover_low = log_data.weather_data.cloud_cover_low
            existing.cloud_cover_high = log_data.weather_data.cloud_cover_high
            existing.dew_point_2m = log_data.weather_data.dew_point_2m
        else:
            # Tạo mới
            db.add(CloudMetricsLog(
                location_name=log_data.location_name,
                lat=log_data.lat,
                lon=log_data.lon,
                probability=log_data.probability,
                temperature_2m=log_data.weather_data.temperature_2m,
                relative_humidity_2m=log_data.weather_data.relative_humidity_2m,
                wind_speed_10m=log_data.weather_data.wind_speed_10m,
                pressure_msl=log_data.weather_data.pressure_msl,
                cloud_cover_low=log_data.weather_data.cloud_cover_low,
                cloud_cover_high=log_data.weather_data.cloud_cover_high,
                dew_point_2m=log_data.weather_data.dew_point_2m,
                created_at=now,
                forecast_for=forecast_time,
                record_type=log_data.record_type
            ))

    # Commit 1 lần duy nhất cho toàn bộ batch
    db.commit()

def get_statistics(db: Session, location_name: str, days: int) -> list[StatisticItem]:
    """
    Lấy dữ liệu thống kê quá khứ.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Chỉ lấy các bản ghi historical hoặc current để thống kê
    records = db.query(CloudMetricsLog).filter(
        CloudMetricsLog.location_name == location_name,
        CloudMetricsLog.forecast_for >= cutoff_date,
        CloudMetricsLog.forecast_for <= datetime.utcnow(),
        CloudMetricsLog.record_type.in_(["historical", "current"])
    ).all()
    
    if not records:
        return []
        
    df = pd.DataFrame([{
        'date': r.forecast_for.date(),
        'probability': r.probability
    } for r in records])
    
    daily_avg = df.groupby('date')['probability'].mean().reset_index()
    daily_avg = daily_avg.sort_values(by='date')
    
    results = []
    prev_prob = None
    for _, row in daily_avg.iterrows():
        prob = row['probability']
        trend = "Đi ngang"
        if prev_prob is not None:
            if prob > prev_prob + 5:
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

def get_confidence_info(record_type: str) -> ConfidenceInfo:
    """Trả về thông tin tin cậy dựa trên loại bản ghi."""
    if record_type in ["historical", "current"]:
        return ConfidenceInfo(level="high", percent=90, label="🟢 Rất tin cậy")
    elif record_type == "forecast_d1":
        return ConfidenceInfo(level="high", percent=85, label="🟢 Tin cậy cao")
    elif record_type == "forecast_d2":
        return ConfidenceInfo(level="medium", percent=70, label="🟡 Tin cậy vừa")
    elif record_type == "forecast_d3":
        return ConfidenceInfo(level="low", percent=55, label="🟠 Tham khảo")
    else: # forecast_d4
        return ConfidenceInfo(level="very_low", percent=40, label="🔴 Cần cập nhật thêm")

def get_location_forecast(db: Session, location_name: str) -> ForecastResponse:
    """
    Lấy dữ liệu dự báo đã tính sẵn (pre-computed) cho một địa điểm.
    """
    # Lấy dự báo tương lai và hiện tại (trong khoảng -1h đến tương lai)
    cutoff = datetime.utcnow() - timedelta(hours=1)
    
    records = db.query(CloudMetricsLog).filter(
        CloudMetricsLog.location_name == location_name,
        CloudMetricsLog.forecast_for >= cutoff
    ).order_by(CloudMetricsLog.forecast_for.asc()).all()
    
    if not records:
        return None
        
    # Lấy thông tin tọa độ từ bản ghi đầu tiên
    first_record = records[0]
    
    forecast_items = []
    current_item = None
    
    now = datetime.utcnow()
    
    for r in records:
        item = ForecastItem(
            forecast_for=r.forecast_for.isoformat(),
            probability=round(r.probability, 2),
            record_type=r.record_type,
            temperature_2m=r.temperature_2m,
            relative_humidity_2m=r.relative_humidity_2m,
            wind_speed_10m=r.wind_speed_10m,
            pressure_msl=r.pressure_msl,
            cloud_cover_low=r.cloud_cover_low,
            cloud_cover_high=r.cloud_cover_high,
            dew_point_2m=r.dew_point_2m,
            confidence=get_confidence_info(r.record_type)
        )
        
        # Xác định current item (gần thời điểm hiện tại nhất)
        if current_item is None and r.forecast_for >= now - timedelta(hours=1):
            current_item = item
            
        forecast_items.append(item)
        
    if current_item is None and forecast_items:
        current_item = forecast_items[0]
        
    # Thêm lịch sử 30 ngày (tùy chọn)
    history = get_statistics(db, location_name, 30)
        
    return ForecastResponse(
        location_name=location_name,
        lat=first_record.lat,
        lon=first_record.lon,
        total_points=len(forecast_items),
        current=current_item,
        forecast=forecast_items,
        history=history,
        last_updated=first_record.created_at.isoformat()
    )

def cleanup_old_records(db: Session):
    """
    Dọn dẹp dữ liệu cũ.
    """
    # 1. Xóa dữ liệu lịch sử cũ hơn 30 ngày
    cutoff_history = datetime.utcnow() - timedelta(days=30)
    del_hist = db.query(CloudMetricsLog).filter(
        CloudMetricsLog.record_type == "historical",
        CloudMetricsLog.forecast_for < cutoff_history
    ).delete()
    
    # 2. Xóa dự báo tương lai đã "trở thành quá khứ" hơn 12 giờ
    # (Tránh trường hợp Bot chết, dự báo cũ vẫn tồn tại và bị nhầm là hiện tại)
    cutoff_forecast = datetime.utcnow() - timedelta(hours=12)
    del_fc = db.query(CloudMetricsLog).filter(
        CloudMetricsLog.record_type.like("forecast%"),
        CloudMetricsLog.forecast_for < cutoff_forecast
    ).delete()
    
    db.commit()
    print(f"🧹 [Cleanup] Đã xóa {del_hist} historical cũ và {del_fc} forecast lỗi thời.")
