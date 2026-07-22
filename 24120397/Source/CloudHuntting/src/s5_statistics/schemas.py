from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class WeatherDataSchema(BaseModel):
    temperature_2m: float
    relative_humidity_2m: float
    wind_speed_10m: float
    pressure_msl: float
    cloud_cover_low: float
    cloud_cover_high: float
    dew_point_2m: float

# ─── INPUT: Log đơn lẻ từ S1 (giữ tương thích ngược) ────────────────────────

class LogRequest(BaseModel):
    """
    Model để nhận dữ liệu từ Service 1 bắn qua (endpoint cũ /log).
    """
    location_name: str = Field(..., description="Tên địa điểm")
    lat: float
    lon: float
    probability: float
    weather_data: WeatherDataSchema
    forecast_for: Optional[str] = None      # ISO datetime string, nếu None → dùng created_at
    record_type: Optional[str] = "current"  # historical/current/forecast_d1-d4

# ─── INPUT: Batch log từ Bot S1 (endpoint mới /log-batch) ────────────────────

class BatchLogItem(BaseModel):
    """Một bản ghi trong batch."""
    location_name: str
    lat: float
    lon: float
    probability: float
    forecast_for: str   # ISO datetime string (bắt buộc)
    record_type: str    # historical/current/forecast_d1-d4
    weather_data: WeatherDataSchema

class BatchLogRequest(BaseModel):
    """Batch chứa nhiều bản ghi, gửi 1 lần từ Bot S1."""
    logs: List[BatchLogItem]

# ─── OUTPUT: Thống kê theo ngày (giữ nguyên cho tương thích) ─────────────────

class StatisticItem(BaseModel):
    """Model kết quả thống kê của 1 ngày."""
    date: str
    avg_probability: float
    trend: str  # "Tăng", "Giảm", "Đi ngang"

class StatisticsResponse(BaseModel):
    """Model trả về cho UI (endpoint cũ /statistics)."""
    location_name: str
    days_analyzed: int
    data: list[StatisticItem]
    message: Optional[str] = None

# ─── OUTPUT: Dự báo pre-computed cho 1 địa điểm (endpoint mới /forecast) ─────

class ConfidenceInfo(BaseModel):
    """Thông tin mức độ tin cậy của dự báo."""
    level: str      # "high", "medium", "low", "very_low"
    percent: int    # 90, 70, 45, 25
    label: str      # "🟢 Rất tin cậy", "🟡 Tin cậy vừa", ...

class ForecastItem(BaseModel):
    """Một điểm dữ liệu dự báo (1 giờ cụ thể)."""
    forecast_for: str           # ISO datetime
    probability: float
    record_type: str            # current/forecast_d1/d2/d3/d4
    temperature_2m: float
    relative_humidity_2m: float
    wind_speed_10m: float
    pressure_msl: float
    cloud_cover_low: float
    cloud_cover_high: float
    dew_point_2m: float
    confidence: ConfidenceInfo

class ForecastResponse(BaseModel):
    """Response cho endpoint /forecast/{location_name}."""
    location_name: str
    lat: float
    lon: float
    total_points: int
    current: Optional[ForecastItem] = None
    forecast: List[ForecastItem] = []
    history: List[StatisticItem] = []       # Tóm tắt 30 ngày quá khứ
    last_updated: Optional[str] = None      # Lần cuối Bot cập nhật
    message: Optional[str] = None
