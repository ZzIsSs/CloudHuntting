# Tổng hợp Thay đổi: Hệ thống Đánh giá, Kiểm duyệt & Bình luận lồng nhau (Review System)

Tài liệu này tổng hợp toàn bộ các thay đổi kỹ thuật và tính năng mới đã được triển khai cho hệ thống Đánh giá & Bình luận (Review) trên ứng dụng CloudHunting.

---

## 🚀 1. Các Tính năng Mới (New Features)

1.  **Phân quyền Tài khoản Kiểm duyệt & Admin cứng:**
    *   Tự động khởi tạo (seed) 3 tài khoản mẫu khi chạy hệ thống:
        *   **Admin (Admin cứng):** `admin` / `admin123` (role: `admin`)
        *   **Kiểm duyệt viên (Moderator):** `moderator` / `moderator123` (role: `moderator`)
        *   **Người dùng thường (User):** `user` / `user123` (role: `user`)
2.  **Quản lý & Duyệt đánh giá:**
    *   Người dùng thường gửi đánh giá mới sẽ ở trạng thái **Chờ duyệt** (`is_approved = false`) và chưa hiển thị công khai.
    *   Tài khoản Admin và Moderator được tự động duyệt trực tiếp, đồng thời có thể bấm nút **"Duyệt"** trên giao diện để công khai các đánh giá đang chờ duyệt của User.
3.  **Giới hạn quyền Xóa Đánh giá (Admin-only Delete):**
    *   Chỉ tài khoản Admin cứng (`role: admin`) mới có quyền xóa đánh giá (nút **"Xóa"** chỉ hiển thị cho Admin). Moderator và User thường không được quyền xóa (kể cả đánh giá của chính mình).
    *   Xóa đánh giá gốc sẽ tự động xóa sạch các bình luận phản hồi liên quan trong cơ sở dữ liệu.
4.  **Tác giả được quyền Chỉnh sửa (Edit Review):**
    *   Người viết đánh giá có thể bấm nút **"Sửa"** trên đánh giá của mình để thay đổi điểm số (số sao) và bình luận.
    *   Nếu người chỉnh sửa là User thường, đánh giá sẽ tự động chuyển về trạng thái **"Chờ duyệt"** (ẩn khỏi danh sách công khai) để yêu cầu duyệt lại, tránh gian lận thay đổi nội dung sau khi đã được duyệt.
5.  **Bình luận phản hồi lồng nhau (Review Comments):**
    *   Người dùng đã đăng nhập có thể bình luận phản hồi (reply) vào đánh giá của người khác thông qua nút **"💬 Phản hồi"**.
    *   Danh sách phản hồi hiển thị lồng và thụt lề trực tiếp phía dưới nội dung đánh giá gốc.

---

## 🛠️ 2. Chi tiết các Thay đổi Kỹ thuật (Technical Implementation)

### Phân hệ Backend (`src/s3_auth` & `src/s4_content`)
*   **Database Schema (`src/s4_content/models.py`):**
    *   Bảng `reviews` được nâng cấp thêm các trường `image_url` (đường dẫn ảnh), `helpful_count` (lượt thích), `updated_at` (thời gian cập nhật).
    *   Tạo bảng mới `review_comments` lưu thông tin phản hồi (`id`, `review_id`, `user_id`, `comment`, `created_at`).
*   **Pydantic Schemas (`src/s4_content/schemas.py`):**
    *   Tạo schema `ReviewCommentCreate`, `ReviewCommentOut`, `ReviewCommentDetailOut`.
    *   Cập nhật `ReviewDetailOut` để tự động trả về danh sách `comments` lồng dưới dạng mảng tối ưu.
*   **API Routes (`src/s4_content/routes.py`):**
    *   `POST /reviews`: Thêm đánh giá mới (Admin/Mod tự động duyệt).
    *   `GET /reviews/location/{id}` & `/all`: Trả về đánh giá kèm toàn bộ bình luận con phản hồi được JOIN để lấy tên tài khoản (`username`) trong 1 truy vấn duy nhất.
    *   `PUT /reviews/{id}`: Chỉnh sửa đánh giá (User thường chỉnh sửa sẽ reset `is_approved = False`).
    *   `POST /reviews/{id}/comments`: Đăng bình luận phản hồi cho một đánh giá.
    *   `DELETE /reviews/{id}`: Enforce kiểm tra quyền `RoleEnum.admin`. Xóa toàn bộ comment liên quan trước khi xóa review.
*   **Xác thực nâng cấp (`src/s3_auth/auth.py`):**
    *   Thay thế thư viện `passlib` bằng các hàm băm `bcrypt` native để tương thích hoàn toàn với Python 3.14.
    *   Tự động nạp dữ liệu tài khoản mẫu khi khởi chạy Auth service (`src/s3_auth/main.py`).

### Cổng API Gateway (`src/gateway`)
*   **Gateway Routing (`src/gateway/routes.py` & `config.py`):**
    *   Sửa port dịch vụ Content thành cổng `8004` và ánh xạ chính xác tuyến `/content` sang `/api/v1/content` của backend.

### Giao diện Frontend (`frontend`)
*   **API Client (`frontend/js/api.js`):**
    *   Tích hợp giải mã JWT token để xác định User ID và Role ở Client.
    *   Viết các hàm helper gọi API mới: `apiUpdateReview`, `apiCreateReviewComment`.
    *   Sửa lỗi phân tích JSON ở hàm `apiRequest` chung để xử lý chính xác phản hồi rỗng `204 No Content` của API xóa.
*   **Trang Thống kê & Đánh giá (`frontend/stats.html` & `js/app.js`):**
    *   Thiết kế giao diện đánh giá cộng đồng dưới dạng các thẻ (card) đẹp mắt với rating 5 sao.
    *   Tích hợp hiển thị danh sách phản hồi lồng nhau, ô nhập phản hồi nhanh, trạng thái kiểm duyệt và các nút tương tác (Duyệt, Sửa, Xóa) động dựa theo quyền của tài khoản đăng nhập.

---

## 🧪 3. Hướng dẫn Chạy & Thử nghiệm (How to Test)

1.  Khởi chạy hệ thống bằng lệnh:
    ```powershell
    python start_all.py
    ```
2.  Truy cập **[http://127.0.0.1:8000](http://127.0.0.1:8000)**:
    *   Đăng nhập bằng `user` / `user123` để viết đánh giá mới, chỉnh sửa đánh giá của bản thân, hoặc phản hồi đánh giá của người khác.
    *   Đăng nhập bằng `moderator` / `moderator123` để duyệt các đánh giá đang chờ duyệt.
    *   Đăng nhập bằng `admin` / `admin123` để duyệt đánh giá hoặc xóa các đánh giá không phù hợp.
