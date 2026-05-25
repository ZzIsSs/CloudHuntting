# Service 6 (S6) - Recommendation & Itinerary Planning (Gợi ý & Lên Lịch Trình Săn Mây)

Service 6 (S6) là một microservice cốt lõi trong hệ thống Cloud Hunting, chịu trách nhiệm cá nhân hóa trải nghiệm người dùng, đề xuất các địa điểm săn mây tốt nhất dựa trên thời tiết (dữ liệu từ S1, S5) và tự động lên lịch trình di chuyển chi tiết, bao gồm cả kịch bản dự phòng "Plan B" khi thời tiết xấu đi đột ngột.

## 🎯 Chức năng chính
- **Cá nhân hóa lộ trình**: Nhận thông tin sở thích người dùng (phương tiện, phong cách, vị trí xuất phát, khoảng cách tối đa).
- **Đánh giá & Chấm điểm (Scoring)**: Lấy dữ liệu xác suất mây từ S1 và xu hướng từ S5 để chấm điểm các địa điểm săn mây.
- **Tự động lên lịch trình (Itinerary Generation)**: Sinh ra lộ trình chi tiết (thời gian khởi hành, thời gian tới nơi, các hoạt động).
- **Cứu nét (Plan B)**: Tự động đổi lộ trình sang điểm khác tốt hơn hoặc đề xuất điểm dừng chân (quán cafe) khi thời tiết tại điểm đến dự kiến thay đổi xấu.
- **Thông báo & Cảnh báo (Background Job)**: Quét tự động định kỳ (1 phút/lần) để phát hiện cơ hội săn mây và lưu cảnh báo.

## 📂 Cấu trúc thư mục
- `main.py`: Điểm vào (Entry point) của FastAPI, cấu hình CORS, khởi tạo DB và Background Scheduler.
- `routes.py`: Định nghĩa các API endpoints (`/recommend`, `/plan-b`, `/notifications`).
- `services.py`: Chứa logic nghiệp vụ lõi (lưu sở thích, chấm điểm địa điểm, sinh lịch trình, Plan B, quét cơ hội săn mây).
- `schemas.py`: Định nghĩa các Pydantic models (Request/Response) để validate dữ liệu đầu vào.
- `database.py`: Cấu hình kết nối SQLite, định nghĩa các SQLAlchemy models.
- `integrations.py`: Chứa các hàm mock (giả lập) để gọi sang S1 và S5.
- `test_simulation.py`: Script giả lập kịch bản test không cần gọi API.

## 🚀 Các API Endpoints
Service 6 chạy tại `http://127.0.0.1:8006`.
- `POST /api/s6/recommend`: Gửi thông tin cá nhân và nhận về lịch trình săn mây.
- `POST /api/s6/plan-b`: Gửi yêu cầu chuyển hướng khi thời tiết thay đổi và nhận về lịch trình khẩn cấp.
- `GET /api/s6/notifications`: Lấy danh sách các cảnh báo, cơ hội săn mây mới nhất (News feed).

---

## 🧪 Hướng dẫn chạy và test Service 6

### 1. Cài đặt thư viện
Đảm bảo bạn đã cài đặt các thư viện cần thiết:
```bash
pip install fastapi uvicorn sqlalchemy apscheduler pydantic
```

### 2. Chạy Service
Bạn có thể khởi động Server bằng lệnh:
```bash
python src/s6_recommend/main.py
```
*(Server sẽ chạy tại `http://127.0.0.1:8006`)*

### 3. Test API thông qua Swagger UI
Sau khi chạy Server, truy cập vào giao diện Swagger UI tại:
👉 `http://127.0.0.1:8006/docs`

Bạn có thể test trực tiếp các endpoints `/recommend`, `/plan-b`, `/notifications` ngay trên giao diện này bằng cách nhập JSON request.

### 4. Chạy kịch bản giả lập (Test Simulation)
Để kiểm tra logic cốt lõi (thuật toán chấm điểm, sinh lịch trình) mà không cần gọi API hay gửi HTTP request phức tạp, bạn có thể chạy file test giả lập:
```bash
python src/s6_recommend/test_simulation.py
```
**File giả lập bao gồm 2 kịch bản chính:**
- **Kịch bản 1 (Thời tiết tốt)**: Hệ thống nhận được báo cáo thời tiết 85% mây. Hệ thống sẽ tự động tìm điểm đến tốt nhất và trả về một lịch trình lý tưởng.
- **Kịch bản 2 (Thời tiết xấu - Plan B)**: Giả lập thời tiết rất xấu (20% mây). Người dùng đang đi thì gặp sự cố. Hệ thống sẽ không tìm thấy điểm săn mây thay thế và sẽ kích hoạt lịch trình "dừng chân khẩn cấp" tại một quán cafe an toàn.
