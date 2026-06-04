# 📝 Hướng dẫn Tích hợp API: Phân hệ Đánh giá & Bình luận (Review System)

Tài liệu này tóm tắt cấu trúc dữ liệu, các endpoints và code JavaScript mẫu để lập trình viên Frontend dễ dàng tích hợp tính năng Đánh giá, Bình luận và Kiểm duyệt.

---

## 📂 1. Cấu trúc Đối tượng Đánh giá (Review Object Structure)

Khi lấy danh sách đánh giá từ API, một đối tượng bình luận chi tiết (`ReviewDetailOut`) sẽ có cấu trúc JSON như sau:

```json
{
  "id": 12,
  "location_id": 2,
  "rating": 5,
  "comment": "Đồi Đa Phú săn mây hôm nay siêu đẹp, trời quang đãng!",
  "image_url": "https://example.com/images/daphu_sunset.jpg",
  "user_id": 3,
  "username": "user",
  "is_approved": true,
  "helpful_count": 5,
  "created_at": "2026-06-04T13:00:00Z",
  "updated_at": "2026-06-04T13:15:00Z"
}
```

### Chi tiết các trường dữ liệu:
*   `id` (int): ID duy nhất của bình luận.
*   `location_id` (int): ID của địa điểm săn mây (Ánh xạ từ 1 tới 10 cho các Hotspots Đà Lạt).
*   `rating` (int): Số sao đánh giá từ 1 đến 5.
*   `comment` (string, optional): Nội dung chữ của bình luận.
*   `image_url` (string, optional): Đường dẫn ảnh đính kèm do người dùng tải lên.
*   `user_id` (int): ID người viết bình luận.
*   `username` (string): Tên tài khoản người viết (đã được tự động JOIN để lấy ra tên thay vì hiển thị ID thô).
*   `is_approved` (boolean): Trạng thái duyệt (chỉ Admin/Moderator mới thấy trạng thái `false`).
*   `helpful_count` (int): Số lượt người dùng khác bình chọn "Hữu ích" (Like).
*   `created_at` (ISO Datetime): Thời điểm viết bình luận.
*   `updated_at` (ISO Datetime, optional): Thời điểm chỉnh sửa bình luận gần nhất.

---

## 🚀 2. Danh sách các API Endpoints

Cổng API Gateway chính: `http://127.0.0.1:8000`  
Tất cả các endpoints dưới đây đều đi qua Gateway qua tiền tố `/content`.

### 2.1. Đăng bình luận mới
*   **Endpoint:** `POST /content/reviews`
*   **Headers:** `Authorization: Bearer <JWT_TOKEN>`
*   **Request Body (JSON):**
    ```json
    {
      "location_id": 2,
      "rating": 5,
      "comment": "Nội dung bình luận...",
      "image_url": "https://url-anh-cua-ban.jpg"
    }
    ```
*   **Lưu ý:**
    *   Nếu tài khoản gửi lên có quyền là `admin` hoặc `moderator`, bình luận sẽ tự động được duyệt (`is_approved = true`).
    *   Nếu là `user` thường, bình luận mặc định ở trạng thái chờ duyệt (`is_approved = false`) và chưa hiển thị công khai.

### 2.2. Lấy danh sách bình luận công khai (dành cho mọi user/khách vãng lai)
*   **Endpoint:** `GET /content/reviews/location/{location_id}`
*   **Request Params:** `skip` (mặc định 0), `limit` (mặc định 10)
*   **Response:** Trả về danh sách dạng mảng chứa các bình luận **đã được duyệt** (`is_approved = true`).

### 2.3. Lấy toàn bộ bình luận kiểm duyệt (chỉ dành cho Admin / Moderator)
*   **Endpoint:** `GET /content/reviews/location/{location_id}/all`
*   **Headers:** `Authorization: Bearer <JWT_TOKEN>`
*   **Response:** Trả về mảng chứa toàn bộ bình luận (bao gồm cả các bình luận đang chờ duyệt `is_approved = false`).

### 2.4. Phê duyệt bình luận (chỉ dành cho Admin / Moderator)
*   **Endpoint:** `PUT /content/reviews/{review_id}/approve`
*   **Headers:** `Authorization: Bearer <JWT_TOKEN>`
*   **Response:** Trả về đối tượng bình luận đã được cập nhật trạng thái duyệt.

### 2.5. Chỉnh sửa bình luận (chỉ dành cho Tác giả bình luận)
*   **Endpoint:** `PUT /content/reviews/{review_id}`
*   **Headers:** `Authorization: Bearer <JWT_TOKEN>`
*   **Request Body (JSON):**
    ```json
    {
      "rating": 4,
      "comment": "Nội dung bình luận đã chỉnh sửa...",
      "image_url": "https://url-anh-moi.jpg"
    }
    ```
*   **Lưu ý:** Sau khi chỉnh sửa, nếu người chỉnh sửa là `user` thường thì bình luận sẽ tự động bị ẩn đi và chuyển về trạng thái chờ duyệt (`is_approved = false`).

### 2.6. Thích bình luận / Đánh giá bình luận Hữu ích (Công khai)
*   **Endpoint:** `POST /content/reviews/{review_id}/helpful`
*   **Response:** Tăng trường `helpful_count` lên 1 và trả về đối tượng bình luận mới.

### 2.7. Xóa bình luận (Tác giả hoặc Admin / Moderator)
*   **Endpoint:** `DELETE /content/reviews/{review_id}`
*   **Headers:** `Authorization: Bearer <JWT_TOKEN>`
*   **Response:** Trạng thái `204 No Content` nếu xóa thành công.

---

## 💻 3. Code JavaScript Mẫu gọi API (Fetch API Examples)

```javascript
// Gán API Base URL
const API_BASE = "http://127.0.0.1:8000";

// Lấy Headers chuẩn chứa token
function getAuthHeaders() {
    const token = localStorage.getItem('ch_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// 1. Lấy bình luận đã duyệt
async function fetchPublicReviews(locationId) {
    const res = await fetch(`${API_BASE}/content/reviews/location/${locationId}`);
    if (!res.ok) throw new Error("Không thể tải bình luận");
    return await res.json();
}

// 2. Viết bình luận mới
async function createReview(locationId, rating, comment, imageUrl = null) {
    const res = await fetch(`${API_BASE}/content/reviews`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
            location_id: locationId,
            rating: rating,
            comment: comment,
            image_url: imageUrl
        })
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Không thể gửi bình luận");
    }
    return await res.json();
}

// 3. Like bình luận hữu ích
async function likeReview(reviewId) {
    const res = await fetch(`${API_BASE}/content/reviews/${reviewId}/helpful`, {
        method: 'POST'
    });
    if (!res.ok) throw new Error("Không thể like bình luận");
    return await res.json();
}

// 4. Sửa bình luận
async function editReview(reviewId, rating, comment, imageUrl = null) {
    const res = await fetch(`${API_BASE}/content/reviews/${reviewId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({ rating, comment, image_url: imageUrl })
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Lỗi chỉnh sửa");
    }
    return await res.json();
}

// 5. Duyệt bình luận (Admin)
async function approveReview(reviewId) {
    const res = await fetch(`${API_BASE}/content/reviews/${reviewId}/approve`, {
        method: 'PUT',
        headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error("Duyệt bình luận thất bại");
    return await res.json();
}

// 6. Xóa bình luận
async function deleteReview(reviewId) {
    const res = await fetch(`${API_BASE}/content/reviews/${reviewId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error("Xóa bình luận thất bại");
    return true;
}
```
