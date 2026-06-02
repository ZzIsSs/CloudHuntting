# Báo cáo: Service 4 - Quản lý Nội dung & Chăm sóc Khách hàng (Content & CSKH)

## 1. Tổng quan
**Service 4** đóng vai trò quản lý các nội dung công khai và hệ thống hỗ trợ người dùng trong nền tảng Cloud Huntting. Service này được chia thành 3 mảng chính:
- **Posts / News (Bài viết / Tin tức):** Cho phép người dùng chia sẻ trải nghiệm (Posts) và quản trị viên đăng các thông báo, tin tức (News).
- **Reviews (Đánh giá):** Hệ thống đánh giá địa điểm (locations) kèm theo điểm số từ 1 đến 5 sao.
- **Tickets (Hỗ trợ CSKH):** Kênh giao tiếp riêng tư giữa người dùng và ban quản trị để giải quyết các vấn đề phát sinh.

Service 4 hiện tại đã được tích hợp đầy đủ hệ thống Xác thực và Phân quyền (Authentication & RBAC) từ `Service 3 (Auth)`, đảm bảo tính bảo mật và quyền riêng tư của dữ liệu.

---

## 2. Cấu trúc Cơ sở dữ liệu (Database Models)
Các bảng dữ liệu được định nghĩa bằng SQLAlchemy trong file `models.py`:

1. **Post (Bài viết):** 
   - Lưu trữ tiêu đề, nội dung, ID tác giả (`author_id`), trạng thái xuất bản, và loại bài viết (`POST` hoặc `NEWS`).
2. **Review (Đánh giá):**
   - Lưu trữ đánh giá cho một địa điểm cụ thể (`location_id`), số điểm (`rating`), nội dung bình luận (`comment`), và người đánh giá (`user_id`).
3. **Ticket (Phiếu hỗ trợ):**
   - Lưu trữ yêu cầu hỗ trợ của người dùng bao gồm tiêu đề, mô tả chi tiết, trạng thái (`open`, `in_progress`, `resolved`, `closed`), và người tạo (`user_id`).
4. **TicketMessage (Tin nhắn hỗ trợ):**
   - Lưu trữ lịch sử trò chuyện (các tin nhắn) bên trong một `Ticket`. Liên kết qua `ticket_id` và lưu người gửi (`sender_id`).

---

## 3. Các API Endpoints
Tất cả các API được đặt dưới prefix `/api/v1/content`.

### 3.1. Quản lý Bài viết (Posts)
- **`POST /posts`**: Tạo bài viết mới (Yêu cầu đăng nhập).
- **`GET /posts`**: Lấy danh sách các bài viết đã xuất bản (Public, không cần đăng nhập).
- **`GET /posts/{id}`**: Lấy chi tiết một bài viết cụ thể.
- **`DELETE /posts/{id}`**: Xóa bài viết (Chỉ tác giả hoặc Admin mới có quyền xóa).

### 3.2. Quản lý Đánh giá (Reviews)
- **`POST /reviews`**: Gửi một đánh giá mới (Yêu cầu đăng nhập).
- **`GET /reviews/location/{location_id}`**: Xem danh sách đánh giá của một địa điểm (Public).

### 3.3. Hệ thống CSKH (Tickets & Messages)
- **`POST /tickets`**: Người dùng tạo một phiếu hỗ trợ mới.
- **`GET /tickets`**: Lấy danh sách phiếu hỗ trợ (User thường chỉ thấy ticket của mình; Admin/Moderator thấy toàn bộ).
- **`GET /tickets/{ticket_id}`**: Lấy chi tiết ticket kèm theo toàn bộ lịch sử tin nhắn. Bảo mật: User chỉ xem được ticket của chính mình.
- **`POST /tickets/{ticket_id}/messages`**: Gửi tin nhắn phản hồi vào một ticket.
- **`PUT /tickets/{ticket_id}`**: Cập nhật trạng thái của ticket (Chỉ Admin/Moderator mới có quyền).

---

## 4. Hướng dẫn Demo và Giải thích Kết quả

Để demo Service 4, ta cần chạy cùng lúc Service 3 (Auth) để lấy Access Token, sau đó dùng token này gọi các API của Service 4.

### Bước 1: Khởi động Service
Mở terminal và khởi động Service 4 bằng lệnh:
```bash
uvicorn src.s4_content.main:app --host 127.0.0.1 --port 8004 --reload
```
Truy cập **Swagger UI** tại: `http://127.0.0.1:8004/docs`.

*(Lưu ý: Bạn cũng cần chạy Service Auth trên port tương ứng, ví dụ 8003, để có thể đăng nhập).*

### Bước 2: Chuẩn bị Token Xác thực (Auth)
1. Qua Service Auth (`http://127.0.0.1:8003/docs`), tạo (đăng ký) 2 tài khoản: 
   - Một tài khoản **User** bình thường.
   - Một tài khoản **Admin**.
2. Dùng API Login để lấy `access_token` cho cả 2 tài khoản này.
3. Quay lại Swagger UI của Service 4 (`http://127.0.0.1:8004/docs`), bấm vào nút **Authorize** (ổ khóa màu xanh góc phải trên cùng) và nhập `Bearer <access_token>` của tài khoản **User**.

### Bước 3: Demo Tính năng Posts (Bài viết)
1. **Tạo bài viết (`POST /posts`)**:
   - Truyền vào JSON: `{"title": "Kinh nghiệm săn mây Đà Lạt", "content": "Rất đẹp...", "article_type": "POST", "is_published": true}`.
   - **Kết quả kỳ vọng**: Trả về thông tin bài viết vừa tạo, kèm theo `id` và `author_id` chính là ID của tài khoản đang đăng nhập. Mã lỗi `201 Created`.
2. **Xem danh sách (`GET /posts`)**:
   - Bấm Execute (không cần token).
   - **Kết quả kỳ vọng**: Trả về danh sách dạng mảng chứa bài viết vừa tạo.
3. **Xóa bài viết (`DELETE /posts/{id}`)**:
   - Dùng token của User khác không phải tác giả gọi xóa -> **Kết quả**: Lỗi `403 Forbidden` (Not enough permissions to delete this post).
   - Dùng token của Admin gọi xóa -> **Kết quả**: Thành công `204 No Content`.

### Bước 4: Demo Tính năng CSKH (Tickets)
**Lưu ý:** trước khi demo phải đảm bảo tất cả các thư viện được liệt kê trong file `requirements.txt` đều đã được cài đặt.
1. **Người dùng tạo Ticket (`POST /tickets`)**:
   - Đăng nhập bằng token của **User**.
   - Gửi data: `{"title": "Lỗi thanh toán", "description": "Tôi không nạp tiền được"}`.
   - **Kết quả kỳ vọng**: Trả về ticket mới với `status: "open"`.
2. **Chat trong Ticket (`POST /tickets/{ticket_id}/messages`)**:
   - Gửi data: `{"message": "Cho mình hỏi bao lâu thì xử lý xong?"}`.
   - **Kết quả kỳ vọng**: Trả về tin nhắn vừa được lưu.
3. **Lấy danh sách Ticket (`GET /tickets`)**:
   - Đứng dưới góc độ User -> **Kết quả**: Trả về danh sách chỉ chứa các ticket do chính User này tạo.
   - Đổi sang token của **Admin** và gọi lại API này -> **Kết quả**: Trả về toàn bộ ticket của tất cả mọi người trên hệ thống.
4. **Admin xử lý Ticket (`PUT /tickets/{ticket_id}`)**:
   - Dùng token của **Admin**, cập nhật trạng thái: `{"status": "in_progress"}`.
   - **Kết quả kỳ vọng**: Trạng thái ticket chuyển từ `open` sang `in_progress`.
   - Nếu dùng token của **User** gọi API cập nhật trạng thái này -> **Kết quả**: Lỗi `403 Forbidden` (Not enough permissions to update ticket status).

### Tổng kết kết quả demo
Nếu tất cả các bước demo trả về đúng "Kết quả kỳ vọng", điều đó chứng minh:
- Models và Database liên kết chính xác.
- Pydantic Validation hoạt động tốt (ví dụ: gửi thiếu chữ sẽ báo lỗi `422 Unprocessable Entity`).
- Hệ thống Phân quyền (RBAC - Role Based Access Control) hoạt động hoàn hảo, chặn đứng các truy cập trái phép.