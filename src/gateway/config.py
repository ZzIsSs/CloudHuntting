"""
Service Registry: Bảng đăng ký tất cả microservices trong hệ thống CloudHunting.
Gateway sẽ đọc file này để biết cần điều hướng request đến đâu.
"""
import os

SERVICES = {
    "s1_metrics": {
        "name": "S1 - Dự báo Săn Mây (AI Metrics)",
        "url": os.getenv("S1_URL", "http://127.0.0.1:8001"),
        "prefix": "/api/s1",
        "description": "Nhập địa điểm → Trả về Top 5 điểm săn mây tốt nhất"
    },
    "s2_booking": {
        "name": "S2 - Đặt chỗ (Booking)",
        "url": os.getenv("S2_URL", "http://127.0.0.1:8002"),
        "prefix": "/api/v1",
        "description": "Tìm & đặt chỗ cafe, homestay, camping gần điểm săn mây"
    },
    "s3_auth": {
        "name": "S3 - Xác thực (Auth)",
        "url": os.getenv("S3_URL", "http://127.0.0.1:8003"),
        "prefix": "/auth",
        "description": "Đăng ký, đăng nhập, quản lý JWT token"
    },
    "s4_content": {
        "name": "S4 - Nội dung & CSKH (Content)",
        "url": os.getenv("S4_URL", "http://127.0.0.1:8004"),
        "prefix": "/api/v1/content",
        "description": "Quản lý bài viết, đánh giá, hỗ trợ khách hàng"
    },
    "s5_statistics": {
        "name": "S5 - Thống kê (Statistics)",
        "url": os.getenv("S5_URL", "http://127.0.0.1:8005"),
        "prefix": "/api/s5",
        "description": "Lưu log dự báo, phân tích xu hướng mây theo ngày"
    },
    "s6_recommend": {
        "name": "S6 - Gợi ý Lộ trình (Recommend)",
        "url": os.getenv("S6_URL", "http://127.0.0.1:8006"),
        "prefix": "/api/s6",
        "description": "Lập lịch trình cá nhân hóa, Plan B, cảnh báo tự động"
    },
}

# Port của Gateway
GATEWAY_HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "8000"))
