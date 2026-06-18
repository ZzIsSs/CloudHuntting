# Giải pháp Toàn diện: Đảm bảo "Always-On" không cần sửa Code (Chuyển đổi sang Railway)

Tài liệu này trình bày kế hoạch giải quyết triệt để vấn đề hệ thống bị gián đoạn, mất dữ liệu và sai lệch lịch trình tác vụ ngầm. 
Thay vì phải can thiệp sâu vào mã nguồn để cấu trúc lại Database và Scheduler (như khi dùng Render), chúng ta sẽ chọn phương án **Zero-Code Change (Không sửa code)** bằng cách chuyển nền tảng triển khai sang **Railway**.

---

## 1. Tại sao lại bỏ Render và UptimeRobot?
Mặc dù UptimeRobot giúp "ping" server liên tục để chống lại cơ chế Idle Sleep của Render, hệ thống vẫn đối mặt với **2 rủi ro chí mạng** trên Render:

1.  **Ổ cứng tạm thời (Ephemeral Disk):** Render tự động restart container định kỳ. Khi đó, toàn bộ các file SQLite (`.db`) lưu trữ tài khoản, lịch sử thời tiết bị xóa sạch.
2.  **Reset Lịch trình (Stateless Scheduler):** `BackgroundScheduler` lưu trạng thái trong RAM. Mỗi lần Render restart, các tác vụ như "Dọn rác mỗi 24h" (S5) hay "Quét thời tiết 3h/lần" (S1) sẽ bị đếm lại từ đầu, dẫn đến việc bỏ lỡ chu kỳ.

---

## 2. Ưu điểm của Giải pháp Railway

Bằng cách đưa hệ thống lên Railway, chúng ta giải quyết được bài toán mà **không cần thay đổi bất kỳ dòng code nào** trong dự án, với sự thuận tiện tối đa trong việc triển khai:

*   **Triển khai Dễ dàng (Easy Deployment):** Kết nối trực tiếp với tài khoản GitHub, Railway sẽ tự động build và deploy mỗi khi có code mới được đẩy lên (CI/CD). Không cần biết về Linux, SSH hay Docker.
*   **Hoạt động Xuyên suốt (Always-On):** Container trên Railway không bị "ngủ" như trên Render, giúp các tác vụ ngầm (`BackgroundScheduler`) của S1, S5, S6 chạy đúng lịch trình và liên tục.
*   **Ổ cứng lưu trữ cố định (Persistent Volumes):** Railway cho phép gắn một "ổ đĩa ảo" vào dịch vụ. Điều này giải quyết triệt để vấn đề mất dữ liệu SQLite (`app.db`, `cloud_hunting.db`...) mỗi khi hệ thống khởi động lại.
*   **Mở rộng linh hoạt:** Dễ dàng nâng cấp cấu hình hoặc chuyển sang dùng database chuyên nghiệp (PostgreSQL) có sẵn trên Railway chỉ bằng vài cú click và thay đổi biến môi trường.

---

## 3. Các bước Triển khai trên Railway

Toàn bộ quá trình được thực hiện trên giao diện web của Railway.

**Bước 1: Đăng ký và Tạo Project từ GitHub**
1. Đăng ký tài khoản tại `railway.app` bằng tài khoản GitHub của bạn.
2. Trên trang Dashboard, chọn **New Project** -> **Deploy from GitHub repo**.
3. Chọn repository `CloudHuntting` của dự án. Railway sẽ tự động phân tích mã nguồn.

**Bước 2: Cấu hình Service và Lệnh Khởi động**
1. Railway sẽ tạo một service cho dự án. Click vào service đó.
2. Vào tab **Settings**, trong mục **Deploy**, tìm đến phần **Start Command**.
3. Nhập lệnh để cài đặt thư viện và chạy file `start_all.py`:
   ```bash
   pip install -r requirements.txt && python start_all.py
   ```
4. Trong mục **Networking**, Railway sẽ tự động phát hiện port `8000` của Gateway và tạo một đường dẫn công khai dạng `*.up.railway.app`.

**Bước 3: Cấu hình Ổ đĩa cố định (Persistent Volume) để giữ lại dữ liệu SQLite**
Đây là bước quan trọng nhất để chống mất dữ liệu.
1.  Trong service của bạn, vào tab **Volumes**.
2.  Click **Add Volume** và tạo một ổ đĩa mới với đường dẫn **Mount Path** là `/data`. Đây sẽ là nơi lưu trữ an toàn.
3.  Quay lại tab **Settings** -> **Start Command**. Chúng ta sẽ dùng một "mẹo" nhỏ để hướng tất cả các file `.db` vào ổ đĩa `/data` mà **không cần sửa code Python**.
4.  Cập nhật lại **Start Command** thành lệnh sau:
    ```bash
    ln -sf /data/app.db app.db && ln -sf /data/cloud_hunting.db cloud_hunting.db && ln -sf /data/s6_preferences.db s6_preferences.db && pip install -r requirements.txt && python start_all.py
    ```
    *Giải thích: Lệnh `ln -sf` tạo các "lối tắt" (symbolic links). Khi ứng dụng ghi vào file `app.db` ở thư mục gốc, hệ điều hành sẽ tự động chuyển hướng dữ liệu đó vào file `/data/app.db` nằm trên ổ đĩa cố định.*

**Hoàn tất!** Sau khi lưu lại, Railway sẽ tự động deploy lại. Giờ đây hệ thống CloudHunting của bạn đã thực sự **Always-On** và **Stateful** (giữ lại được dữ liệu) trên Railway, giải quyết dứt điểm vấn đề của Render mà không cần động vào 1 dòng code Python.

> [!NOTE]
> **Hướng đi nâng cao:** Để hệ thống chạy ổn định và chuyên nghiệp hơn trong tương lai, bạn có thể cân nhắc tạo một dịch vụ **PostgreSQL** ngay trên Railway và cấu hình các biến môi trường `DATABASE_URL` như trong file `DEPLOY_DATABASE_GUIDE.md`. Việc này cũng không yêu cầu sửa code.