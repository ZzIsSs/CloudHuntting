# ☁️ Cloud Hunting System (Hệ thống Săn Mây)

Hệ thống tự động thu thập dữ liệu thời tiết, phân tích chỉ số và tích hợp AI để gợi ý địa điểm, thời gian săn mây lý tưởng.

Dự án được xây dựng theo kiến trúc **Monorepo (Modular Monolith)**, gom toàn bộ các thành phần vào một kho lưu trữ thống nhất để dễ dàng phát triển và triển khai.

---

# 🏗️ Kiến trúc Hệ thống (6 Modules)

Dự án được chia thành **6 phân hệ (module)** cốt lõi cùng chạy trên một hệ thống:

### S1 (Chỉ số)
Module thu thập dữ liệu API thời tiết (OpenWeatherMap/Tomorrow.io) theo tọa độ.

### S2 (Đặt chỗ)
Module tích hợp bản đồ, logic chọn slot và đặt chỗ tại các địa điểm săn mây.

### S3 (Auth)
Module xác thực người dùng (JWT, OAuth), phân quyền (User/Admin/Moderator).

### S4 (Nội dung)
Module quản lý bài viết, tin tức săn mây và hệ thống ticket CSKH.

### S5 (Thống kê)
Module phân tích xu hướng, tính toán các chỉ số trung bình/cao/thấp.

### S6 (Gợi ý)
Module chứa thuật toán AI cá nhân hóa, gợi ý địa điểm dựa trên dữ liệu S1 & S5.

---

# 📂 Cấu trúc Thư mục

Mặc dù là mô hình Mono, mã nguồn trong `src/` vẫn được chia phân khu rành mạch theo từng Module để tránh xung đột code khi làm việc nhóm:

```txt
cloud-hunting-system/
├── data/                  # [KHÔNG PUSH] Dữ liệu thời tiết thô & đã xử lý
├── notebooks/             # File Jupyter Notebook (test thuật toán AI, EDA)
├── src/                   # Source code chính của dự án
│   ├── s1_metrics/        # [S1] Code gọi API thời tiết, cào dữ liệu
│   ├── s2_booking/        # [S2] Code xử lý đặt chỗ, tích hợp bản đồ
│   ├── s3_auth/           # [S3] Code cấp token JWT, phân quyền, middleware
│   ├── s4_content/        # [S4] Code quản lý bài viết, ticket hỗ trợ
│   ├── s5_statistics/     # [S5] Code tính toán chỉ số, lưu lịch sử
│   ├── s6_recommend/      # [S6] Thuật toán AI gợi ý cá nhân hóa
│   └── shared/            # Code dùng chung cho cả 6 module (utils, config DB...)
├── .github/               # Template quy chuẩn Pull Request
├── .gitignore             # File cấu hình chặn push file rác/mật khẩu
└── requirements.txt       # Danh sách thư viện Python
```

---

# ⚙️ Yêu cầu Hệ thống (Prerequisites)

- Python 3.10 trở lên  
- Git  
- Tài khoản GitHub đã được phân quyền vào repository

---

# 🚀 Hướng dẫn Cài đặt & Khởi chạy

## Bước 1: Clone kho mã nguồn về máy

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


