## 📝 Mô tả công việc
- Bổ sung tài khoản admin cứng và moderator mẫu vào database phục vụ kiểm duyệt bình luận.
- Mở rộng bảng `Review` trong cơ sở dữ liệu: hỗ trợ đánh giá sao (1-5), nội dung chữ, đường dẫn ảnh đính kèm, lượt hữu ích, mốc thời gian tạo và cập nhật.
- Tác giả được quyền chỉnh sửa đánh giá của chính mình. Sau khi sửa, đánh giá tự động chuyển sang trạng thái chờ duyệt (is_approved = false) để kiểm duyệt lại nhằm tránh gian lận.
- Phân quyền xóa: Giới hạn nghiêm ngặt chỉ tài khoản Admin (`role: admin`) mới được xóa đánh giá. Moderator và User thường không có quyền xóa.
- Bổ sung tính năng bình luận/phản hồi lồng nhau (Review Comments) dưới đánh giá của người khác, hiển thị thụt dòng và đồng bộ trực tiếp lên giao diện.
- Viết tài liệu đặc tả API chi tiết cho Frontend Dev và cập nhật giao diện hiển thị động trên trang thống kê.

## 🛠️ Chi tiết thay đổi
- [x] Thêm file: [api_review_spec.md](file:///f:/CloudHunting/CloudHuntting/api_review_spec.md) (đặc tả API đánh giá)
- [x] Thêm file: [review_system_updates.md](file:///f:/CloudHunting/CloudHuntting/review_system_updates.md) (tổng hợp thay đổi hệ thống)
- [x] Cập nhật hàm: Thêm bảng `ReviewComment` trong `src/s4_content/models.py`
- [x] Cập nhật hàm: Thêm các schemas `ReviewComment` và lồng vào `ReviewDetailOut` trong `src/s4_content/schemas.py`
- [x] Cập nhật hàm: Cập nhật `delete_review` (chỉ admin), `get_location_reviews` (lồng comments), và thêm API `create_review_comment` trong `src/s4_content/routes.py`
- [x] Cập nhật hàm: Thay thế `passlib` bằng `bcrypt` native trong `src/s3_auth/auth.py`
- [x] Cập nhật hàm: Tự động seed tài khoản mẫu trong `src/s3_auth/main.py`
- [x] Cập nhật hàm: Sửa cấu hình port dịch vụ Content thành `8004` trong `src/gateway/config.py`
- [x] Cập nhật hàm: Tích hợp API sửa/phản hồi và sửa lỗi xử lý response 204 trống trong `frontend/js/api.js`
- [x] Cập nhật hàm: Cập nhật logic Sửa, Phản hồi lồng dưới Review, phân quyền nút Xóa chỉ cho Admin trong `frontend/js/app.js`

## 📸 Hình ảnh minh họa / Log kết quả
### Log kiểm thử API:
```
--- 1. Create a Review (User) ---
Create review status: 201
Created review ID: 1

--- 2. Approve the Review (Moderator) ---
Approve review status: 200

--- 3. Comment on the Review (User) ---
Create comment status: 201
Created comment: {'id': 1, 'review_id': 1, 'user_id': 3, 'comment': 'Cam on ban da chia se nhe!', 'created_at': '2026-06-04T13:17:21', 'username': 'user'}

--- 4. Get Reviews for Location 1 (Public, should contain comment) ---
Get reviews status: 200
Found review with nested comments:
{
  "location_id": 1,
  "rating": 4,
  "comment": "Dia diem rat dep, nen di som.",
  "image_url": null,
  "id": 1,
  "user_id": 3,
  "is_approved": true,
  "helpful_count": 0,
  "created_at": "2026-06-04T13:17:21",
  "updated_at": "2026-06-04T13:17:21",
  "username": "user",
  "comments": [
    {
      "id": 1,
      "review_id": 1,
      "user_id": 3,
      "comment": "Cam on ban da chia se nhe!",
      "created_at": "2026-06-04T13:17:21",
      "username": "user"
    }
  ]
}

--- 5. Edit the Review (User) ---
Update review status: 200
Updated review (is_approved should be False): {'location_id': 1, 'rating': 5, 'comment': 'Thong tin da duoc cap nhat: tuyet voi lam!', 'image_url': None, 'id': 1, 'user_id': 3, 'is_approved': False, 'helpful_count': 0, 'created_at': '2026-06-04T13:17:21', 'updated_at': '2026-06-04T13:17:21'}

--- 6. Test Delete Review - Should FAIL for User ---
Delete by User status (Expect 403): 403
Response: {"detail":"Only admins can delete reviews"}

--- 7. Test Delete Review - Should FAIL for Moderator ---
Delete by Moderator status (Expect 403): 403
Response: {"detail":"Only admins can delete reviews"}

--- 8. Test Delete Review - Should SUCCEED for Admin ---
Delete by Admin status (Expect 204): 204
```

## ⚠️ Lưu ý cho Reviewer
- Vì có thêm bảng mới `review_comments` vào database, reviewer sau khi kéo nhánh về cần khởi động lại toàn bộ hệ thống để SQLAlchemy sinh bảng mới tự động trong `app.db`.
- Đã thay thế thư viện `passlib` cũ bằng `bcrypt` native do lỗi không tương thích phiên bản trên Python 3.14+.
