# CloudHuntting
☁️ Cloud Hunting System (Hệ thống Săn Mây)Hệ thống tự động thu thập dữ liệu thời tiết, phân tích chỉ số và tích hợp AI để gợi ý địa điểm, thời gian săn mây lý tưởng. Dự án được chia thành kiến trúc Microservices để đảm bảo tính mở rộng và hiệu suất.🏗️ Kiến trúc Hệ thống (6 Services)Dự án được cấu trúc thành 6 service cốt lõi:S1 (Chỉ số): Thu thập dữ liệu API thời tiết (OpenWeatherMap/Tomorrow.io) theo tọa độ.S2 (Đặt chỗ): Tích hợp bản đồ, logic chọn slot và đặt chỗ tại các địa điểm săn mây.S3 (Auth): Xác thực người dùng (JWT, OAuth), phân quyền (User/Admin/Moderator).S4 (Nội dung): Quản lý bài viết, tin tức săn mây và hệ thống ticket CSKH.S5 (Thống kê): Phân tích xu hướng, tính toán các chỉ số trung bình/cao/thấp.S6 (Gợi ý): Thuật toán AI cá nhân hóa, gợi ý địa điểm dựa trên dữ liệu S1 & S5.📂 Cấu trúc Thư mụccloud-hunting-system/
├── data/                  # [KHÔNG PUSH] Dữ liệu thời tiết thô & đã xử lý
├── notebooks/             # File Jupyter Notebook (test thuật toán AI, EDA)
├── src/                   # Source code chính của dự án
│   ├── crawler/           # Script tự động cào dữ liệu (S1)
│   ├── models/            # Mã nguồn huấn luyện AI (S5, S6)
│   ├── app/               # API / Web server chính
│   └── utils/             # Các hàm bổ trợ dùng chung
├── .github/               # Template quy chuẩn Pull Request
├── .gitignore             # File cấu hình chặn push file rác/mật khẩu
└── requirements.txt       # Danh sách thư viện Python
⚙️ Yêu cầu Hệ thống (Prerequisites)Python 3.10 trở lênGitTài khoản GitHub đã được phân quyền vào repository🚀 Hướng dẫn Cài đặt & Khởi chạyBước 1: Clone kho mã nguồn về máygit clone [https://github.com/ZzIsSs/CloudHuntting.git](https://github.com/ZzIsSs/CloudHuntting.git)
cd CloudHuntting
Bước 2: Cài đặt Môi trường Ảo (Virtual Environment)# Tạo môi trường ảo có tên là venv
python -m venv venv

# Kích hoạt môi trường (Dành cho Windows)
venv\Scripts\activate
# Kích hoạt môi trường (Dành cho macOS/Linux)
source venv/bin/activate
Bước 3: Cài đặt thư việnpip install -r requirements.txt
Bước 4: Cấu hình biến môi trườngTạo một file tên là .env ở thư mục gốc (Ngang hàng với README).Tuyệt đối KHÔNG push file .env lên GitHub.Thêm các API Key cần thiết vào file (Ví dụ):WEATHER_API_KEY=your_api_key_here
JWT_SECRET=your_secret_key_here
📜 Nội quy Code & Làm việc Nhóm (Dành cho Team)Để hệ thống hoạt động trơn tru và không bị xung đột code, toàn bộ thành viên bắt buộc phải tuân thủ luồng Git Workflow sau:1. Luật Nhánh (Branching)main: Nhánh chứa code hoàn chỉnh, ổn định nhất. (Khóa bảo vệ, không được push trực tiếp).develop: Nhánh làm việc chung của cả team. (Khóa bảo vệ, không được push trực tiếp).feature/...: Nhánh để làm tính năng mới. Mọi người phải rẽ nhánh từ develop.Ví dụ: git checkout -b feature/s1-weather-api develop2. Luật Gộp Code (Pull Request)Code xong trên nhánh feature/... phải đẩy lên GitHub và tạo Pull Request (PR) xin gộp vào develop.Bắt buộc: Điền đầy đủ thông tin vào PR Template có sẵn.Cần ít nhất 1 người (Tech Lead) Approve thì mới được Merge.3. Luật Báo cáo Tiến độ (Issue Tracking)Quản lý task hoàn toàn trên GitHub Projects và GitHub Issues.Khi tạo PR, bắt buộc phải gõ vào phần mô tả PR cú pháp: Closes #ID (Ví dụ: Closes #5) để hệ thống tự động đánh dấu hoàn thành task trên bảng tiến độ.
