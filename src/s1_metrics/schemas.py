from pydantic import BaseModel, Field
from typing import Optional, List

# ─── INPUT: Yêu cầu dự báo săn mây ──────────────────────────────────────────

class CloudHuntingRequest(BaseModel):
    """
    Module 1: Tiếp nhận dữ liệu đầu vào.
    Người dùng chỉ cần nhập tên địa điểm và bán kính khảo sát.
    Hệ thống sẽ tự tìm tọa độ và quét các điểm săn mây lân cận.
    """
    # Tên địa điểm trung tâm (bắt buộc)
    location_name: str = Field(..., description="Tên địa điểm trung tâm khảo sát (VD: Hồ Xuân Hương, nhà nghỉ DaLat Sky)")
    
    # Bán kính quét (mặc định 15km, đủ bao phủ hầu hết Đà Lạt)
    radius_km: float = Field(15.0, ge=1.0, le=50.0, description="Bán kính khảo sát tính từ điểm trung tâm (km)")

    # Số giờ dự báo trong tương lai (0 = hiện tại, tối đa 72h)
    forecast_hours: int = Field(0, ge=0, le=384, description="Dự báo trước bao nhiêu giờ (0-384h, tức là 16 ngày)")

# ─── OUTPUT: Kết quả từng địa điểm ──────────────────────────────────────────

class ConfidenceInfo(BaseModel):
    """Thông tin mức độ tin cậy của dự báo."""
    level: str      # "high", "medium", "low", "very_low"
    percent: int    # 90, 70, 45, 25
    label: str      # "🟢 Rất tin cậy", "🟡 Tin cậy vừa", ...
    note: Optional[str] = None

class SpotResult(BaseModel):
    """
    Kết quả dự báo mây cho một địa điểm cụ thể trong danh sách Top 5.
    Bao gồm timeline chỉ số theo từng giờ để vẽ biểu đồ.
    """
    rank: int = Field(..., description="Xếp hạng (1 = xác suất cao nhất)")
    location_name: str = Field(..., description="Tên địa điểm săn mây")
    lat: float = Field(..., description="Vĩ độ")
    lon: float = Field(..., description="Kinh độ")
    distance_km: float = Field(..., description="Khoảng cách từ điểm trung tâm (km)")
    probability: float = Field(..., description="Xác suất xuất hiện mây cao nhất (%)")
    best_time: str = Field(..., description="Thời gian lý tưởng nhất đạt xác suất này")
    suggestion: str = Field(..., description="Lời khuyên cho địa điểm này")
    timeline: Optional[List[dict]] = Field(default=[], description="Chỉ số săn mây theo từng giờ [{time, probability}]")
    confidence: Optional[ConfidenceInfo] = Field(default=None, description="Độ tin cậy của dự báo")
    image_url: Optional[str] = Field(default=None, description="Đường dẫn ảnh địa điểm")

# ─── OUTPUT: Kết quả tổng hợp ────────────────────────────────────────────────

class CloudHuntingResponse(BaseModel):
    """
    Kết quả trả về: Top 5 địa điểm săn mây tốt nhất trong bán kính.
    Danh sách được sắp xếp từ xác suất mây cao nhất xuống thấp nhất.
    """
    center_location: str = Field(..., description="Địa điểm trung tâm khảo sát")
    center_lat: float = Field(..., description="Vĩ độ trung tâm (tự suy ra từ Geocoding)")
    center_lon: float = Field(..., description="Kinh độ trung tâm (tự suy ra từ Geocoding)")
    radius_km: float = Field(..., description="Bán kính khảo sát (km)")
    total_spots_found: int = Field(..., description="Tổng số địa điểm tìm được trong bán kính")
    top_spots: List[SpotResult] = Field(..., description="Top 5 địa điểm săn mây xếp hạng từ cao xuống thấp")
    
    # Các trường dành cho Smart Fallback (địa điểm lạ lấy data từ hotspot gần nhất)
    is_estimated: bool = Field(False, description="Dữ liệu có phải là ước tính từ trạm khác không?")
    estimated_from: Optional[str] = Field(None, description="Tên trạm quan sát gần nhất được dùng làm nguồn data")
    estimated_distance_km: Optional[float] = Field(None, description="Khoảng cách đến trạm đó")
    warning: Optional[str] = Field(None, description="Thông báo cảnh báo cho người dùng")

# ─── INPUT/OUTPUT cho endpoint đơn giản (Internal S6 → S1) ────────────────────

class SinglePredictRequest(BaseModel):
    """
    Yêu cầu dự báo cho MỘT tọa độ cụ thể.
    Dùng cho tích hợp nội bộ (S6 gọi S1 trực tiếp bằng tọa độ).
    """
    lat: float = Field(..., description="Vĩ độ GPS")
    lon: float = Field(..., description="Kinh độ GPS")
    location_name: str = Field("Unknown", description="Tên địa điểm (tùy chọn)")

class SinglePredictResponse(BaseModel):
    """
    Kết quả dự báo mây cho một tọa độ duy nhất.
    """
    location_name: str = Field(..., description="Tên địa điểm")
    lat: float = Field(..., description="Vĩ độ")
    lon: float = Field(..., description="Kinh độ")
    probability: float = Field(..., description="Xác suất xuất hiện mây (%)")
    best_time: str = Field(..., description="Thời gian lý tưởng nhất")
    suggestion: str = Field(..., description="Lời khuyên săn mây")

