from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WeatherDataSchema(BaseModel):
    temperature_2m: float
    relative_humidity_2m: float
    wind_speed_10m: float
    pressure_msl: float
    cloud_cover_low: float
    cloud_cover_high: float
    dew_point_2m: float

class LogRequest(BaseModel):
    """
    Model để nhận dữ liệu từ Service 1 bắn qua.
    """
    location_name: str = Field(..., description="Tên địa điểm")
    lat: float
    lon: float
    probability: float
    weather_data: WeatherDataSchema

class StatisticItem(BaseModel):
    """
    Model kết quả thống kê của 1 ngày.
    """
    date: str
    avg_probability: float
    trend: str # "Tăng", "Giảm", "Đi ngang"

class StatisticsResponse(BaseModel):
    """
    Model trả về cho UI.
    """
    location_name: str
    days_analyzed: int
    data: list[StatisticItem]
    message: Optional[str] = None
