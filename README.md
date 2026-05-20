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
git clone https://github.com/ZzIsSs/CloudHuntting.git
cd CloudHuntting
```

## Bước 2: Cài đặt Môi trường Ảo (Virtual Environment)

```bash
# Tạo môi trường ảo có tên là venv
python -m venv venv
```

### Kích hoạt môi trường

**Windows**

```bash
venv\Scripts\activate
```

**macOS/Linux**

```bash
source venv/bin/activate
```

## Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

## Bước 4: Cấu hình biến môi trường

Tạo một file tên là `.env` ở thư mục gốc (**ngang hàng với README**).

**Tuyệt đối KHÔNG push file `.env` lên GitHub.**

Thêm các API Key cần thiết vào file:

```env
WEATHER_API_KEY=your_api_key_here
JWT_SECRET=your_secret_key_here
```

---

# 📜 Nội quy Code & Làm việc Nhóm (Dành cho Team)

Để hệ thống hoạt động trơn tru và không bị xung đột code, toàn bộ thành viên bắt buộc phải tuân thủ luồng **Git Workflow** sau:

## 1. Luật Nhánh (Branching)

### `main`
Nhánh chứa code hoàn chỉnh, ổn định nhất.  
(**Khóa bảo vệ, không được push trực tiếp**)

### `develop`
Nhánh làm việc chung của cả team.  
(**Khóa bảo vệ, không được push trực tiếp**)

### `feature/...`
Nhánh để làm tính năng mới.

Mọi người phải rẽ nhánh từ `develop`.

Ví dụ:

```bash
git checkout -b feature/s1-weather-api develop
```

## 2. Luật Gộp Code (Pull Request)

- Code xong trên nhánh `feature/...` phải đẩy lên GitHub và tạo **Pull Request (PR)** xin gộp vào `develop`.
- **Bắt buộc:** Điền đầy đủ thông tin vào **PR Template** có sẵn.
- Cần ít nhất **1 người (Tech Lead)** approve thì mới được merge.

## 3. Luật Báo cáo Tiến độ (Issue Tracking)

Quản lý task hoàn toàn trên GitHub Projects và GitHub Issues.

Khi tạo PR, bắt buộc phải gõ vào phần mô tả PR cú pháp:

```txt
Closes #ID
```

Ví dụ:

```txt
Closes #5
```

để hệ thống tự động đánh dấu hoàn thành task trên bảng tiến độ.