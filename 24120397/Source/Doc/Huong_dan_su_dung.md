# HƯỚNG DẪN CÀI ĐẶT VÀ SỬ DỤNG
**Hệ thống Hỗ trợ Săn mây Đà Lạt (CloudHunting)**

---

## I. YÊU CẦU HỆ THỐNG

Để triển khai và vận hành hệ thống CloudHunting, thiết bị cần đáp ứng các yêu cầu tối thiểu sau:
- **Hệ điều hành:** Windows 10/11, macOS hoặc Linux.
- **Backend Environment:** Python 3.9 trở lên.
- **Frontend Environment:** Node.js 18.x trở lên và npm.
- **Trình duyệt web:** Khuyến nghị Google Chrome, Microsoft Edge hoặc Safari phiên bản mới nhất.

---

## II. HƯỚNG DẪN CÀI ĐẶT VÀ KHỞI CHẠY

Hệ thống được chia thành hai phần độc lập: Backend (kiến trúc Microservices) và Frontend (ReactJS). Cần khởi chạy Backend trước khi chạy Frontend.

### 1. Khởi chạy Backend (Microservices & API Gateway)
1. Mở Terminal (Command Prompt / PowerShell).
2. Di chuyển vào thư mục chứa mã nguồn hệ thống.
3. Cài đặt các thư viện phụ thuộc bằng lệnh:
   ```bash
   pip install -r requirements.txt
   ```
4. Kích hoạt toàn bộ các dịch vụ (Gateway và các Service từ S1 đến S6) bằng tệp lệnh khởi động:
   ```bash
   python start_all.py
   ```
   *(Hệ thống Backend sẽ chạy tại địa chỉ: `http://localhost:8000`)*

### 2. Khởi chạy Frontend (Giao diện người dùng)
Hệ thống Gateway đã được lập trình để tự động phân phối (serve) giao diện Frontend tại cổng `8000`. Tuy nhiên, cần đảm bảo mã nguồn React đã được biên dịch thành bản Release.

1. Mở một cửa sổ Terminal mới.
2. Di chuyển vào thư mục Frontend:
   ```bash
   cd frontend/cloud-hunting-app
   ```
3. Cài đặt các gói thư viện Node.js (chỉ làm lần đầu):
   ```bash
   npm install
   ```
4. Biên dịch mã nguồn Frontend (Build Release):
   ```bash
   npm run build
   ```
5. Sau khi quá trình build hoàn tất (tạo ra thư mục `dist`), trình duyệt đã có thể truy cập toàn bộ giao diện và backend chung tại đường dẫn: `http://localhost:8000`.

*(Lưu ý: Nếu đang trong quá trình phát triển và cần sửa code, có thể dùng lệnh `npm run dev` để chạy Server phát triển độc lập tại `http://localhost:5173`)*.

---

## III. HƯỚNG DẪN TÍNH NĂNG DÀNH CHO NGƯỜI DÙNG CƠ BẢN (USER)

### 1. Đăng ký và Đăng nhập
- Tại trang chủ, chọn tab **Đăng ký** để tạo tài khoản mới bằng cách nhập Email, Tên hiển thị, Tên đăng nhập và Mật khẩu.
- Chuyển sang tab **Đăng nhập**, nhập Tên đăng nhập và Mật khẩu để vào hệ thống.
- *(Lưu ý: Mật khẩu được mã hóa an toàn trong cơ sở dữ liệu).*

### 2. Dò tìm điểm săn mây (Predict Cloud)
- Sau khi đăng nhập, màn hình sẽ hiển thị bảng cấu hình thông số dò mây.
- Nhập tên khu vực trung tâm (Mặc định: Đà Lạt).
- Điều chỉnh **Bán kính (Radius)** (từ 1km đến 50km) để mở rộng vùng quét.
- Điều chỉnh **Độ trễ thời gian (Time offset)** để dự báo cho ngày mai hoặc ngày mốt (tối đa 72 giờ).
- Nhấn nút **DÒ**. Hệ thống sẽ tính toán và hiển thị danh sách các địa điểm có tỷ lệ xuất hiện mây cao nhất.

### 3. Xem chi tiết và Xếp hạng địa điểm
- Tại trang Kết quả (dạng băng chuyền/carousel), nhấp vào một thẻ địa điểm bất kỳ để vào trang **Chi tiết & Đánh giá**.
- Tại đây, người dùng có thể:
  - Xem hình ảnh và thông tin vị trí.
  - Viết đánh giá, chấm điểm (số sao) cho địa điểm.
  - Bấm "Hữu ích" (Like) cho các đánh giá của người khác.

### 4. Tạo lịch trình AI tự động
- Tại trang Đánh giá, nhấn vào nút nổi **"AI Gợi ý giờ xuất phát"**.
- Điền các tùy chọn bao gồm: Loại phương tiện (Ô tô/Xe máy), Phong cách chuyến đi (Chụp ảnh/Chill/Cắm trại), và Đối tượng đi cùng.
- Nhấn **Tạo lịch trình**. Trí tuệ nhân tạo sẽ tự động tính toán thời gian di chuyển, thời tiết hiện tại và đề xuất một lộ trình từng phút (Timeline) tối ưu nhất.

### 5. Khám phá tiện ích xung quanh (Plan B)
- Nhấn vào biểu tượng Bản đồ/Tiện ích trên thanh điều hướng dưới cùng.
- Giao diện chia đôi sẽ xuất hiện: Bên trái là danh sách các quán Cafe, Homestay, Quán ăn; Bên phải là bản đồ tương tác (Leaflet).
- Sử dụng bộ lọc để tìm kiếm các tiện ích đáp ứng tiêu chí như "Mở qua đêm", "Có bãi đỗ xe" nhằm lên phương án dự phòng khi thời tiết xấu.

---

## IV. HƯỚNG DẪN TÍNH NĂNG DÀNH CHO QUẢN TRỊ VIÊN (ADMIN)

Quản trị viên có quyền hạn đặc biệt để duy trì trật tự cộng đồng và hỗ trợ người dùng.

### 1. Truy cập Admin Dashboard
- Sử dụng tài khoản có cấp quyền Quản trị (Ví dụ: Tên đăng nhập: `admin`, Mật khẩu: `admin123`).
- Sau khi đăng nhập thành công, hệ thống sẽ tự động chuyển hướng giao diện sang Bảng điều khiển riêng biệt dành cho Admin.

### 2. Quản lý Đánh giá (Reviews)
- Tại thanh điều hướng bên trái, chọn tab **Quản lý Đánh giá**.
- Lựa chọn một địa điểm cụ thể từ danh sách thả xuống.
- Bảng dữ liệu sẽ hiển thị toàn bộ các bài đánh giá của người dùng tại địa điểm đó.
- Nhấn nút **Xóa** ở cột thao tác để gỡ bỏ các bình luận tiêu cực, rác hoặc vi phạm tiêu chuẩn cộng đồng.

### 3. Quản lý Phản hồi Người dùng (Support Tickets)
- Chuyển sang tab **Phản hồi Người dùng**.
- Bảng danh sách sẽ hiển thị các mã yêu cầu (Ticket), tiêu đề và trạng thái xử lý (Đang xử lý, Chờ phản hồi, Đã giải quyết).
- Dùng tính năng này để theo dõi và cập nhật trạng thái khắc phục sự cố hệ thống dựa trên báo cáo từ người dùng thực tế.
