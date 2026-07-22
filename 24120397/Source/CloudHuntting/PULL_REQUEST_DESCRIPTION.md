## 📝 Báo cáo Tóm tắt (Executive Summary)
Bản cập nhật này tập trung vào việc **tối ưu hóa toàn diện hiệu năng (Performance)**, **độ ổn định (Stability)** và **cải tiến luồng dữ liệu (Data Flow)** của Backend, đặc biệt là Service 1 (S1 - Metrics). Bằng cách tận dụng tối đa cơ sở dữ liệu nội bộ (S5) và chuyển đổi các phép tính phụ thuộc mạng sang thuật toán CPU cục bộ, hệ thống đã giải quyết dứt điểm tình trạng giật lag, treo server và crash ngầm trên môi trường Windows.

- **Mức độ khẩn cấp**: High (Nâng cấp trải nghiệm người dùng ngay lập tức).
- **Kết quả đo lường**: Giảm độ trễ trung bình của S1 từ **~8.5 - 10 giây** xuống chỉ còn **~0.014 giây** (Tốc độ tăng hơn 500 lần). Khắc phục 100% lỗi crash do bảng mã font chữ.

---

## 🛠️ Chi tiết Thay đổi & Kiến trúc (Changelog & Architecture)

### 1. Phân tách Kiến trúc: Luồng Tính Toán vs Luồng Phục Vụ (Smart Fallback S1 - S5)
* **Vấn đề trước đây**: Hệ thống bị thắt cổ chai do gom chung "tính toán AI nặng nề" và "trả dữ liệu cho khách hàng" vào cùng một API. Mỗi khi user tìm kiếm, hệ thống phải chạy lại toàn bộ quy trình: Tải model AI -> Gọi API Open-Meteo -> Tính toán -> Phản hồi.
* **Giải pháp triển khai**: Tách bạch kiến trúc thành 2 luồng độc lập, giúp hệ thống vận hành trơn tru và logic hơn:
  
  **A. Luồng "Tính toán hệ thống" (Background Auto-Scan)**
  - Tự động hóa ngầm: Tại S1 (`tasks.py`), một tiến trình Scheduler (chạy ngầm) được thiết lập để tự động kích hoạt mỗi 1 giờ.
  - Xử lý dữ liệu nặng: Tiến trình này tự động quét qua danh sách 10 Hotspots định cứng, gọi `WeatherService` và chạy mô hình AI (`predict_cloud_probability`) để tính ra xác suất mây cho hiện tại và dự báo lên tới 96 giờ tới.
  - Đồng bộ Database: Sau khi tính xong, S1 đóng gói kết quả và gọi `POST /api/s5/forecast` sang S5 để **ghi đè/cập nhật (upsert) liên tục** vào SQLite. Nhờ vậy, kho dữ liệu của S5 luôn "tươi mới" mà không cần bất kỳ tác động nào từ phía người dùng.

  **B. Luồng "Phục vụ khách hàng" (Cơ chế 3 Tầng - 3-Tier Fallback)**
  Khi người dùng thực sự thao tác tìm kiếm trên giao diện, S1 (`src/s1_metrics/routes.py`) sẽ không tính toán lại mà áp dụng cơ chế 3 tầng để phục vụ:
  - **Tầng 1 (Ưu tiên Data có sẵn - Siêu tốc)**: S1 lập tức truy vấn S5 (`GET /api/s5/forecast/{hotspot}`). Nếu mốc thời gian user yêu cầu khớp với data đã lưu (chênh lệch <= 1 giờ), S1 lấy data ra trả về ngay lập tức (bypass 100% việc gọi AI và Open-Meteo). Tốc độ đáp ứng tính bằng mili-giây với cờ báo `Dữ liệu siêu tốc`.
  - **Tầng 2 (Nội suy Nearest Hotspot)**: Nếu user nhập vào một vị trí hoang vu không nằm trong danh sách Hotspot, S1 tự động đo khoảng cách bằng Haversine, tìm Hotspot gần nhất (< 15km) và lấy dữ liệu của Hotspot đó (từ S5) để đại diện trả về kèm cảnh báo "Dữ liệu ước tính từ trạm gần nhất".
  - **Tầng 3 (Real-time Fallback Dự phòng)**: Trong trường hợp xấu nhất (S5 bị sập, hoặc user tra cứu dự báo vượt quá số ngày S5 lưu trữ), S1 mới tự động kích hoạt lại quy trình cũ: Gọi API Open-Meteo theo thời gian thực và tự chạy mô hình AI để bảo đảm luôn có dữ liệu trả về cho user mà không bao giờ bị gián đoạn (Zero Downtime).

### 2. Triệt tiêu Điểm nghẽn Cổ chai (Latency Bottleneck)
* **Vấn đề trước đây**: Khi user tìm kiếm, hệ thống cần tính khoảng cách từ vị trí user đến tất cả các Hotspot để lập danh sách `< 15km`. Code cũ trong `get_real_distance` đã sử dụng thư viện `requests.get` để gọi sang API định tuyến OSRM (`router.project-osrm.org`) lấy khoảng cách đường bộ. Việc gọi vòng lặp tuần tự 10 lần tốn trung bình 0.8s/lần -> Tổng cộng mất ~8 giây thời gian chết (blocking I/O).
* **Giải pháp triển khai** (`src/s1_metrics/nearby_service.py`):
  - Gỡ bỏ hoàn toàn việc gọi API OSRM khỏi hàm `get_real_distance`.
  - Thay thế bằng **Công thức lượng giác Haversine** để tính khoảng cách đường chim bay dựa trên vĩ độ/kinh độ.
  - Phép tính thuần túy thực hiện trực tiếp trên CPU nội bộ với `math.sin`, `math.cos`. Nhờ đó, việc tính khoảng cách cho toàn bộ hotspot hoàn thành trong vài micro-giây, giải phóng hoàn toàn thời gian chờ của luồng phản hồi. (Chênh lệch vài km giữa đường bộ và đường chim bay là hoàn toàn chấp nhận được cho việc quét bán kính 15km).

### 3. Khắc phục Crash ngầm trên Windows (Environment Stability)
* **Vấn đề trước đây**: Khi chạy backend qua terminal của Windows (cmd/powershell), hệ thống sử dụng bảng mã `cp1258`. Khi background tasks (VD: Bot quét S5) hoặc quá trình khởi động mô hình AI thực thi hàm `print()` chứa emoji (🚀, ✅, ☁️) hoặc ký tự có dấu, Windows Console không thể giải mã, ném ra exception `UnicodeEncodeError` và crash ngầm tiến trình S1.
* **Giải pháp triển khai** (`src/s1_metrics/main.py`, `ai_service.py`, `tasks.py`):
  - Dọn dẹp lại cấu trúc Log: Loại bỏ toàn bộ các Emoji và các cụm từ tiếng Việt có dấu ở các hàm chạy ngầm tự động. Đảm bảo mọi string output ra `stdout` chỉ chứa ký tự chuẩn ASCII.
  - S1 hiện tại có thể khởi chạy trơn tru thông qua file `start_all.py` ở mọi môi trường mà không lo sập dịch vụ bất ngờ.

---

## 📸 Kịch bản Kiểm thử đã Xác nhận (Verified Test Cases)

- **Test Tốc độ (Benchmark)**: Thực hiện `POST /api/s1/predict` trực tiếp bằng Python Script, xác nhận `Total Time` giảm từ `8.4s` xuống ổn định ở mức `0.014s`.
- **Test Thuật toán Fuzzy Matching & Logic S5**: 
  - Input đầu vào cố tình ghi sai/viết thường: `trai mat`
  - Hệ thống `geocoding_service.py` vẫn dịch thành công ra tọa độ GPS qua Nominatim.
  - Thuật toán `Haversine` quét ra được 7 điểm xung quanh có `distance <= 15km`.
  - S1 query S5 thành công cho cả 7 điểm và trả ra kết quả với `Dữ liệu siêu tốc` (Status: OK).
- **Test Start-up**: Lệnh `python start_all.py` không còn văng lỗi font chữ, các port tự động bind thành công.

---

## ⚠️ Lưu ý & Kế hoạch tiếp theo cho Reviewer
1. **Frontend (Chưa triển khai)**: Vì logic backend đã phản hồi siêu tốc và có cơ chế sửa lỗi nhập nhằng (fuzzy search), bước tiếp theo chúng ta mới tiến hành refactor frontend (Đổi ô nhập địa điểm thành Dropdown/Autocomplete và ẩn tùy chọn kéo Bán kính). Frontend update sẽ được tạo ở Pull Request tiếp theo.
2. Code hiện tại đã an toàn để Merge vào nhánh chính (`main`/`production`) và triển khai lên server Render.
