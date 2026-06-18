# Vấn Đề "Always-On" Trong CloudHunting — Tài Liệu Giao Việc

> **Mục đích tài liệu:** Cung cấp đủ ngữ cảnh để thành viên được giao hiểu rõ vấn đề và đề xuất/triển khai giải pháp cải thiện.
>
> **Người đọc:** Thành viên nhóm phụ trách cải thiện hạ tầng/deployment.

---

## 1. Vấn Đề Là Gì?

Hiện tại, để hệ thống **CloudHunting** hoạt động đầy đủ — đặc biệt là các **chức năng tự động chạy ngầm (auto/background)** — người vận hành phải:

1. Bật laptop lên
2. Chạy lệnh `python start_all.py`
3. **Giữ nguyên, không được tắt terminal hoặc laptop**

Ngay khi nhấn `Ctrl+C`, tắt terminal, hoặc laptop ngủ/shutdown → **toàn bộ 3 cơ chế tự động đều dừng lại ngay lập tức**.

---

## 2. Kiến Trúc Khởi Động Hiện Tại

File [start_all.py](file:///d:/User/HCMUS/Tư duy tính toán/Đồ án/github_TDTT/CloudHuntting/start_all.py) dùng `subprocess.Popen` để khởi động **7 tiến trình uvicorn** độc lập:

```
python start_all.py
│
├── uvicorn src.s3_auth.main:app       (port 8003)
├── uvicorn src.s4_content.main:app    (port 8004)
├── uvicorn src.s5_statistics.main:app (port 8005) ← có Scheduler
├── uvicorn src.s1_metrics.main:app    (port 8001) ← có Scheduler
├── uvicorn src.s2_booking.main:app    (port 8002)
├── uvicorn src.s6_recommend.main:app  (port 8006) ← có Scheduler
└── uvicorn src.gateway.main:app       (port 8000)
```

Script `start_all.py` sau khi khởi động các service sẽ vào vòng lặp vô tận `while True: time.sleep(1)`. Khi bị ngắt (Ctrl+C), nó sẽ `.terminate()` tất cả các subprocess con.

---

## 3. Các Chức Năng Bắt Buộc Phải Chạy Liên Tục

Có **3 cơ chế tự động (scheduler)** trong hệ thống, tất cả đều dùng thư viện `APScheduler` với `BackgroundScheduler`. Đây là loại scheduler chạy **trong cùng tiến trình Python của server** — không có persistence, không có daemon riêng.

---

### 🤖 3.1 — Bot Auto-Scan Hotspots (Service 1)

**File:** [src/s1_metrics/tasks.py](file:///d:/User/HCMUS/Tư duy tính toán/Đồ án/github_TDTT/CloudHuntting/src/s1_metrics/tasks.py) | [src/s1_metrics/main.py](file:///d:/User/HCMUS/Tư duy tính toán/Đồ án/github_TDTT/CloudHuntting/src/s1_metrics/main.py)

**Tần suất:** Mỗi **3 giờ** + chạy ngay lần đầu khi startup

**Chức năng:** Tự động quét **10 hotspot săn mây cố định** tại Đà Lạt, lấy dữ liệu thời tiết thực từ Open-Meteo, chạy mô hình AI dự đoán xác suất mây, sau đó gửi kết quả sang Service 5 để lưu lịch sử.

```python
# tasks.py — Cách được khởi động:
def start_bot():
    scheduler.add_job(auto_scan_hotspots, "interval", hours=3)   # Lặp mỗi 3h
    scheduler.start()
    scheduler.add_job(auto_scan_hotspots, "date")                 # Chạy ngay lập tức
```

**Tại sao phải liên tục?**
- Bot này là **nguồn dữ liệu chủ động duy nhất** tự động bơm lịch sử vào database của S5.
- Mỗi lần scan tạo ra **10 bản ghi** (1 cho mỗi hotspot) trong bảng `cloud_metrics_log`.
- Nếu bot dừng → S5 không có dữ liệu mới → thống kê xu hướng mây sẽ không cập nhật → S6 scoring bị lỗi thời.

**Hậu quả khi dừng:**
- Database S5 không có dữ liệu mới theo thời gian thực.
- Mỗi lần restart, interval đếm lại từ đầu → có thể bỏ lỡ nhiều chu kỳ 3 giờ.

---

### 🧹 3.2 — Cleanup Job (Service 5)

**File:** [src/s5_statistics/main.py](file:///d:/User/HCMUS/Tư duy tính toán/Đồ án/github_TDTT/CloudHuntting/src/s5_statistics/main.py) | [src/s5_statistics/services.py](file:///d:/User/HCMUS/Tư duy tính toán/Đồ án/github_TDTT/CloudHuntting/src/s5_statistics/services.py)

**Tần suất:** Mỗi **24 giờ**

**Chức năng:** Tự động xóa tất cả bản ghi trong bảng `cloud_metrics_log` có `timestamp` cũ hơn **30 ngày** để tránh database phình to.

```python
# main.py — Cách được cấu hình trong lifespan event:
scheduler.add_job(scheduled_cleanup, 'interval', hours=24)

# services.py — Logic xóa:
def cleanup_old_records(db: Session):
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    deleted_count = db.query(CloudMetricsLog)\
        .filter(CloudMetricsLog.timestamp < cutoff_date).delete()
    db.commit()
```

**Tại sao phải liên tục?**
- Bot S1 tạo ~80 bản ghi/ngày. Sau 1 tháng tích lũy → ~2.400 bản ghi.
- Nếu cleanup không chạy, database sẽ tích lũy vô hạn → ảnh hưởng hiệu suất truy vấn.

**Hậu quả khi dừng:**
- Database phình to dần theo thời gian.
- Không gây lỗi ngay lập tức nhưng ảnh hưởng lâu dài đến tốc độ truy vấn.

---

### 🔔 3.3 — Opportunity Scanner (Service 6)

**File:** [src/s6_recommend/main.py](file:///d:/User/HCMUS/Tư duy tính toán/Đồ án/github_TDTT/CloudHuntting/src/s6_recommend/main.py)

**Tần suất:** Mỗi **1 phút**

**Chức năng:** Liên tục quét xác suất mây tại các địa điểm trong hệ thống. Khi phát hiện địa điểm có xác suất ≥ 85%, tự động tạo **thông báo cơ hội săn mây mới** vào News Feed. Áp dụng cooldown 12 giờ để chống spam.

```python
# main.py — Cách được cấu hình:
scheduler.add_job(scheduled_scan, "interval", minutes=1)
```

**Tại sao phải liên tục?**
- Cửa sổ thời gian có biển mây đẹp thường rất ngắn (vài giờ). Nếu scanner dừng, sẽ bỏ lỡ các cơ hội này và không gửi thông báo kịp thời cho người dùng.
- Đây là **tính năng đặc trưng** của ứng dụng — cảnh báo proactive thay vì người dùng phải tự kiểm tra.

**Hậu quả khi dừng:**
- Không có thông báo cơ hội nào được tạo ra.
- News Feed (`GET /api/s6/notifications`) trở nên tĩnh và không có giá trị.

---

### 📊 Tổng hợp 3 cơ chế cần "Always-On"

| Cơ chế | Service | File | Tần suất | Tác động nếu dừng |
|:--|:--|:--|:--|:--|
| Bot Auto-Scan Hotspots | S1 | `tasks.py` | Mỗi 3 giờ | Không có dữ liệu lịch sử mới → thống kê S5 lỗi thời |
| Cleanup Job | S5 | `main.py` | Mỗi 24 giờ | Database phình to dần |
| Opportunity Scanner | S6 | `main.py` | Mỗi 1 phút | Không có cảnh báo cơ hội săn mây |

---

## 4. Tại Sao Vấn Đề Này Tồn Tại?

### Nguyên nhân kỹ thuật cốt lõi: **In-Process Scheduler**

Cả 3 scheduler đều dùng `APScheduler.BackgroundScheduler`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(my_function, "interval", hours=3)
scheduler.start()
```

`BackgroundScheduler` chạy trên một **thread riêng** nhưng vẫn **nằm trong cùng tiến trình Python** với uvicorn. Điều này có nghĩa:

```
[Tiến trình Python / uvicorn]
        │
        ├── Thread chính: Xử lý HTTP requests
        └── Background Thread: APScheduler (chạy các job định kỳ)
```

Khi tiến trình Python bị kill (do Ctrl+C, tắt laptop, hoặc crash) → **cả 2 thread đều chết**.

### Hành vi khi restart

- Scheduler **không lưu trạng thái** (stateless) — không biết mình đã chạy được bao lâu.
- Sau mỗi lần restart, tất cả interval job đều **đếm lại từ 0**.
- Ví dụ: Bot S1 chạy được 2.5 giờ rồi restart → chờ thêm 3 giờ mới chạy lần tiếp theo (mất cả 2.5 giờ đó).

---

## 5. Phạm Vi Ảnh Hưởng

Ngoài 3 scheduler trên, khi ứng dụng dừng còn ảnh hưởng đến:

| Chức năng | Ảnh hưởng |
|:--|:--|
| `POST /api/s1/predict` | Người dùng không gọi được API dự báo |
| `GET /api/s5/statistics` | Không truy vấn được thống kê |
| `POST /api/s6/recommend` | Không lên được lịch trình |
| `GET /api/s6/notifications` | Không xem được cảnh báo |
| Toàn bộ API Gateway | Không phản hồi |

Tuy nhiên, **các chức năng trên chỉ cần server đang chạy tại thời điểm được gọi** — chúng không cần "liên tục". Chỉ 3 scheduler mới thực sự cần "always-on".

---

## 6. Giải Pháp Tham Khảo

Dưới đây là 4 hướng tiếp cận từ đơn giản đến phức tạp.

---

### 💡 Giải pháp A — Deploy lên Cloud Miễn Phí (Đơn giản nhất)

Không thay đổi code, chỉ thay đổi nơi chạy.

**Lựa chọn 1: Railway (`railway.app`)**
- Free tier: 500 giờ/tháng (~20 ngày liên tục)
- Hỗ trợ multi-service (phù hợp kiến trúc hiện tại)
- Deploy trực tiếp từ GitHub
- SQLite file được giữ lại (persistent volume)

**Lựa chọn 2: Oracle Cloud Free Tier (`cloud.oracle.com`)**
- **Hoàn toàn miễn phí vĩnh viễn** (2 VM Ubuntu, 1 OCPU + 1GB RAM mỗi cái)
- Cần biết Linux cơ bản, SSH
- Dùng `systemd` hoặc `screen`/`tmux` để giữ process sau khi đóng SSH
- Cần thẻ Visa để đăng ký (không bị charge tiền)

**Độ phức tạp triển khai:** ⭐⭐ (Railway) / ⭐⭐⭐ (Oracle)

> [!NOTE]
> **Đây là giải pháp ít thay đổi code nhất.** Nếu nhóm chỉ muốn giải quyết vấn đề "phải giữ laptop" mà không muốn refactor code thì đây là hướng đi nhanh nhất.

---

### 💡 Giải pháp B — Tách Scheduler Thành Process Riêng

Thay vì APScheduler chạy trong cùng process uvicorn, tạo **file script riêng** chỉ để chạy các task định kỳ.

**Ý tưởng:**
```
# Thay vì:
[uvicorn S1] → [APScheduler thread bên trong]

# Thành:
[uvicorn S1]       ← chỉ xử lý HTTP
[python worker.py] ← chỉ chạy scheduler (process độc lập)
```

**Cách triển khai:**
1. Tạo file `worker.py` tại thư mục gốc
2. Import các hàm job từ các service và cấu hình scheduler
3. Chạy song song: `python start_all.py` và `python worker.py`

```python
# worker.py (ví dụ)
from apscheduler.schedulers.background import BlockingScheduler
from src.s1_metrics.tasks import auto_scan_hotspots
from src.s5_statistics.services import cleanup_old_records
from src.s6_recommend.services import scan_and_notify_opportunities

scheduler = BlockingScheduler()  # Dùng BlockingScheduler thay vì BackgroundScheduler
scheduler.add_job(auto_scan_hotspots, "interval", hours=3)
scheduler.add_job(cleanup_s5, "interval", hours=24)
scheduler.add_job(scan_s6, "interval", minutes=1)
scheduler.start()
```

**Lợi ích:** Khi uvicorn bị crash/restart, worker vẫn tiếp tục chạy (và ngược lại).

**Độ phức tạp:** ⭐⭐

---

### 💡 Giải pháp C — Dùng Celery + Redis (Chuyên nghiệp)

Thay `APScheduler` bằng **Celery Beat** (task queue có persistence), dùng **Redis** làm message broker.

**Kiến trúc mới:**
```
[uvicorn services]          ← HTTP server (không có scheduler)
[Celery Worker]             ← Chạy các background task
[Celery Beat]               ← Lập lịch định kỳ
[Redis]                     ← Message broker (trung gian)
```

**Lợi ích chính:**
- **Persistence:** Task schedule được lưu trong Redis, restart không mất lịch
- **Retry:** Nếu task lỗi, tự động retry
- **Monitoring:** Có Flower UI để xem trạng thái task
- **Scale:** Có thể thêm nhiều worker

**Hạn chế:**
- Cần cài thêm Redis server
- Phải refactor code: chuyển các hàm job thành Celery task
- Phức tạp hơn đáng kể

**Độ phức tạp:** ⭐⭐⭐⭐

> [!NOTE]
> **Celery là giải pháp production-grade** nhưng có thể quá phức tạp so với yêu cầu của đồ án. Nên cân nhắc kỹ trước khi chọn.

---

### 💡 Giải pháp D — APScheduler Với JobStore SQLAlchemy (Ít thay đổi nhất)

Giữ nguyên APScheduler nhưng thêm **JobStore** để lưu trạng thái scheduler vào database. Khi restart, scheduler biết mình đã chạy đến đâu.

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

# Thêm jobstore:
jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
}
scheduler = BackgroundScheduler(jobstores=jobstores)
```

**Lợi ích:** Thay đổi code **tối thiểu**, scheduler có persistence sau restart.

**Hạn chế:** Không giải quyết được vấn đề "phải giữ máy bật" — chỉ cải thiện hành vi sau khi restart (không mất lịch).

**Độ phức tạp:** ⭐

---

## 7. So Sánh Tổng Hợp

| Giải pháp | Giải quyết "phải giữ máy" | Thay đổi code | Chi phí | Độ khó |
|:--|:--|:--|:--|:--|
| A — Deploy Cloud (Railway) | ✅ Hoàn toàn | ❌ Không cần | Free (hạn chế giờ) | ⭐⭐ |
| A — Deploy Cloud (Oracle) | ✅ Hoàn toàn | ❌ Không cần | Free vĩnh viễn | ⭐⭐⭐ |
| B — Tách Worker Process | ⚠️ Một phần | ✅ Nhỏ | Free | ⭐⭐ |
| C — Celery + Redis | ✅ Hoàn toàn | ✅ Lớn | Free (tự host) | ⭐⭐⭐⭐ |
| D — APScheduler JobStore | ❌ Không | ✅ Rất nhỏ | Free | ⭐ |

---

## 8. Gợi Ý Hướng Đi Cho Đồ Án

> [!IMPORTANT]
> Tùy vào thời gian và mục tiêu của nhóm, hãy chọn một trong hai hướng sau:

**Nếu ưu tiên demo nhanh, ít thay đổi code:**
→ Chọn **Giải pháp A (Railway)**. Đẩy code lên GitHub → kết nối Railway → deploy. Không cần thay đổi gì trong source code.

**Nếu muốn cải thiện kiến trúc ứng dụng (có giá trị kỹ thuật hơn):**
→ Chọn **Giải pháp B (Worker Process) + Giải pháp D (APScheduler JobStore)** kết hợp. Code thay đổi ít nhưng kiến trúc tốt hơn đáng kể.

---

## 9. Tài Nguyên Tham Khảo

- APScheduler Documentation: https://apscheduler.readthedocs.io/
- APScheduler JobStore SQLAlchemy: https://apscheduler.readthedocs.io/en/stable/userguide.html#jobstores
- Railway Deployment Guide: https://docs.railway.app/getting-started
- Oracle Cloud Always Free: https://www.oracle.com/cloud/free/
- Celery Documentation: https://docs.celeryq.dev/

---

## 10. Câu Hỏi Cần Làm Rõ Trước Khi Bắt Đầu

Người được giao cần xác nhận với nhóm trưởng các điểm sau:

- [ ] Mục tiêu là **demo cho giáo viên** hay **chạy thực tế dài hạn**?
- [ ] Có được phép thay đổi cấu trúc code của S1, S5, S6 không?
- [ ] Có thẻ Visa để đăng ký Oracle Cloud không?
- [ ] Nhóm có người biết Linux/SSH để quản lý VPS không?
- [ ] Deadline cải thiện tính năng này là khi nào?
