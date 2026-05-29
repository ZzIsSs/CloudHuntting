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
    forecast_hours: int = Field(0, ge=0, le=72, description="Dự báo trước bao nhiêu giờ (0-72h)")

# ─── OUTPUT: Kết quả từng địa điểm ──────────────────────────────────────────

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

