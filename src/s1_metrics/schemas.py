from pydantic import BaseModel, Field

class CloudHuntingRequest(BaseModel):
    """
    Module 1: Tiếp nhận và kiểm tra dữ liệu đầu vào.
    Model này dùng để validate tọa độ và các thông số phụ do người dùng cung cấp.
    """
    # Tên địa điểm người dùng chọn (Dùng để gửi sang S5 thống kê)
    location_name: str = Field(..., description="Tên địa điểm săn mây (VD: Đồi chè Cầu Đất)")
    
    # Vĩ độ (Latitude) giới hạn trong khu vực Đà Lạt (khoảng 11.7 đến 12.1)
    lat: float = Field(..., ge=11.7, le=12.1, description="Vĩ độ của điểm cần săn mây (chỉ hỗ trợ Đà Lạt)")
    
    # Kinh độ (Longitude) giới hạn trong khu vực Đà Lạt (khoảng 108.3 đến 108.7)
    lon: float = Field(..., ge=108.3, le=108.7, description="Kinh độ của điểm cần săn mây (chỉ hỗ trợ Đà Lạt)")
    
    # Bán kính quét (tùy chọn, mặc định 2km)
    radius_km: float = Field(2.0, ge=1.0, le=50.0, description="Bán kính quét (km)")

class CloudHuntingResponse(BaseModel):
    """
    Model để định dạng dữ liệu trả về cho người dùng
    """
    probability: float = Field(..., description="Tỷ lệ % xuất hiện biển mây")
    suggestion: str = Field(..., description="Lời khuyên tương ứng với tỷ lệ")
    weather_data: dict = Field(..., description="Thông tin thời tiết hiện tại")
    data_source: str = Field(..., description="Nguồn dữ liệu (Cache, Mới, Fallback)")
