# Hướng dẫn Cấu hình Database khi Deploy Hệ thống CloudHunting

Hệ thống đã được cập nhật cấu hình linh hoạt để hỗ trợ chuyển đổi tự động giữa **SQLite (cho phát triển cục bộ - Local Dev)** và **PostgreSQL (cho môi trường chạy thật - Production Deploy)** thông qua các biến môi trường (Environment Variables). 

Dưới đây là thông tin chi tiết dành cho người phụ trách deploy hệ thống lên Web (Render/Railway/Docker...).

---

## 1. Yêu cầu về Database
Hệ thống sử dụng các database độc lập cho từng microservice. Khi deploy lên Cloud, bạn cần chuẩn bị chuỗi kết nối **PostgreSQL URL** (ví dụ từ dịch vụ Neon.tech, Supabase, hoặc Render PostgreSQL).

*Bạn có thể dùng chung **1 chuỗi kết nối PostgreSQL** cho tất cả các service bên dưới, hoặc cấu hình **các database/schema riêng biệt** tùy theo nhu cầu phân tách dữ liệu.*

Ví dụ định dạng chuỗi kết nối (Connection String):
```text
postgresql://<username>:<password>@<host>:<port>/<database_name>?sslmode=require
```

---

## 2. Các Biến Môi Trường (Environment Variables) Cần Cấu Hình
Khi deploy ứng dụng (ví dụ trên Render.com), hãy khai báo **4 biến môi trường** sau tại cấu hình Environment:

| Tên biến (Key) | Service sử dụng | Ghi chú |
|---|---|---|
| `DATABASE_URL` | **S3 Auth** & **S4 Content** | Quản lý tài khoản người dùng và thông tin địa điểm săn mây. |
| `S2_DATABASE_URL` | **S2 Booking** | Quản lý đặt dịch vụ/chỗ. |
| `S5_DATABASE_URL` | **S5 Statistics** | Lưu trữ lịch sử thời tiết và kết quả dự đoán. |
| `S6_DATABASE_URL` | **S6 Recommend** | Lưu trữ nhật ký đề xuất và tùy chọn của người dùng. |

*Lưu ý: Nếu không khai báo các biến này, hệ thống sẽ tự động fallback sang sử dụng SQLite cục bộ (tạo file `.db` tạm thời trong container), điều này sẽ làm mất dữ liệu khi container khởi động lại.*

---

## 3. Quá trình Khởi tạo Bảng (Database Migration)
* **Tự động chạy:** Người deploy không cần thực hiện migration thủ công. Khi các dịch vụ FastAPI khởi động, chúng đã được thiết lập sẵn mã lệnh tự động kiểm tra và khởi tạo các bảng dữ liệu nếu chưa tồn tại (`Base.metadata.create_all`).
* **Đồng bộ hóa Driver:** File `requirements.txt` đã được thêm sẵn gói `psycopg2-binary` nên hệ thống sẽ tự động tải driver kết nối PostgreSQL khi cài đặt dependencies trên server.

---

## 4. Kiểm tra Trạng thái Kết nối
Sau khi deploy xong và cấu hình các biến môi trường:
* Bạn có thể kiểm tra xem các bảng đã được tự động tạo trong database PostgreSQL hay chưa.
* Vào các API docs của Gateway (ví dụ `https://your-domain.com/docs`) hoặc log của các service xem có thông báo lỗi kết nối DB hay không.
