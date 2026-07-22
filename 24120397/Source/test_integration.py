# test_integration.py
import requests
import uuid
import sys

# Đảm bảo hiển thị ký tự tiếng Việt UTF-8 không bị lỗi trên Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

AUTH_URL = "http://127.0.0.1:8003"
BOOKING_URL = "http://127.0.0.1:8002"

def check_service_running(url, name):
    try:
        r = requests.get(f"{url}/health")
        if r.status_code == 200:
            print(f"✅ Phân hệ {name} đang chạy tại {url}")
            return True
    except requests.exceptions.ConnectionError:
        pass
    print(f"❌ Phân hệ {name} CHƯA được bật tại {url}")
    return False

def run_tests():
    print("=" * 60)
    print("   BẮT ĐẦU KIỂM THỬ TÍCH HỢP S3_AUTH VÀ S2_BOOKING")
    print("=" * 60)
    
    # 1. Kiểm tra trạng thái các service
    auth_ok = check_service_running(AUTH_URL, "S3_Auth (Cổng 8003)")
    booking_ok = check_service_running(BOOKING_URL, "S2_Booking (Cổng 8002)")
    
    if not auth_ok or not booking_ok:
        print("\n⚠️ Vui lòng chạy cả hai dịch vụ trước khi thực hiện test:")
        print("  - Chạy Auth:    python src/s3_auth/main.py")
        print("  - Chạy Booking: python src/s2_booking/main.py")
        sys.exit(1)
        
    username = f"testuser_{uuid.uuid4().hex[:6]}"
    email = f"{username}@example.com"
    password = "SecurePassword123"
    
    # 2. Đăng ký tài khoản mới qua S3
    print(f"\n1. Đăng ký tài khoản mới qua S3: Username={username} ...")
    r_reg = requests.post(f"{AUTH_URL}/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    print(f"   Status code: {r_reg.status_code}")
    assert r_reg.status_code == 200, f"Đăng ký thất bại: {r_reg.text}"
    user_data = r_reg.json()
    print(f"   Đăng ký thành công! User ID: {user_data.get('id')}, Quyền: {user_data.get('role')}")
    
    # 3. Đăng nhập qua S3 để lấy JWT Token
    print("\n2. Đăng nhập để nhận JWT Access Token...")
    r_login = requests.post(f"{AUTH_URL}/auth/login", json={
        "username": username,
        "password": password
    })
    print(f"   Status code: {r_login.status_code}")
    assert r_login.status_code == 200, f"Đăng nhập thất bại: {r_login.text}"
    token_data = r_login.json()
    token = token_data.get("access_token")
    print(f"   JWT Token nhận được: {token[:45]}...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 4. Tìm kiếm địa điểm xung quanh qua S2 (sử dụng Token của S3)
    print("\n3. Tìm kiếm địa điểm gần điểm săn mây (Yêu cầu JWT Token)...")
    # Tọa độ Đồi Chè Cầu Đất (Vĩ độ 11.85, Kinh độ 108.55)
    r_places = requests.get(
        f"{BOOKING_URL}/api/v1/places/nearby?lat=11.85&lon=108.55&radius_km=30",
        headers=headers
    )
    print(f"   Status code: {r_places.status_code}")
    assert r_places.status_code == 200, f"Tìm địa điểm thất bại: {r_places.text}"
    places_data = r_places.json()
    places = places_data.get("places", [])
    print(f"   Tìm thấy {len(places)} địa điểm xung quanh.")
    for p in places[:3]:
        print(f"     - [ID: {p.get('id')}] {p.get('name')} ({p.get('category')}) - Cách: {p.get('distance_km')} km")
        
    if not places:
        print("   Không tìm thấy địa điểm nào để tiếp tục kiểm thử đặt chỗ.")
        return
        
    target_place = places[0]
    place_id = target_place["id"]
    
    # 5. Kiểm tra thời gian trống (Availability) của địa điểm
    print(f"\n4. Kiểm tra lịch trống của {target_place['name']} ngày 2026-06-01...")
    r_avail = requests.get(
        f"{BOOKING_URL}/api/v1/places/{place_id}/availability?date=2026-06-01",
        headers=headers
    )
    print(f"   Status code: {r_avail.status_code}")
    assert r_avail.status_code == 200, f"Kiểm tra lịch trống thất bại: {r_avail.text}"
    avail_data = r_avail.json()
    print(f"   Các slot trống còn lại: {avail_data.get('available_slots')}")
    
    # 6. Thực hiện đặt chỗ (POST /bookings) kèm theo Idempotency-Key
    idempotency_key = str(uuid.uuid4())
    booking_headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": idempotency_key
    }
    booking_body = {
        "place_id": place_id,
        "booking_date": "2026-06-01",
        "start_time": "08:00",
        "end_time": "09:30",
        "party_size": 4,
        "notes": "Đặt chỗ test tích hợp hệ thống"
    }
    
    print(f"\n5. Thực hiện tạo đặt chỗ tại {target_place['name']}...")
    r_book = requests.post(
        f"{BOOKING_URL}/api/v1/bookings",
        headers=booking_headers,
        json=booking_body
    )
    print(f"   Status code: {r_book.status_code}")
    assert r_book.status_code == 201, f"Tạo đặt chỗ thất bại: {r_book.text}"
    booking_data = r_book.json()
    booking_id = booking_data.get("id")
    print(f"   Đặt chỗ thành công! Booking ID: {booking_id}, Trạng thái: {booking_data.get('status')}")
    
    # 6a. Thử gửi lại trùng Idempotency-Key (Đảm bảo tính Idempotency)
    print("\n5a. Gửi lại request đặt chỗ với cùng Idempotency-Key để kiểm tra tính Idempotent...")
    r_book_retry = requests.post(
        f"{BOOKING_URL}/api/v1/bookings",
        headers=booking_headers,
        json=booking_body
    )
    print(f"   Status code (phải trả về 200 thay vì 201 hoặc báo lỗi): {r_book_retry.status_code}")
    assert r_book_retry.status_code == 200, "Tính Idempotent không được xử lý chính xác"
    print("   ✅ Xác nhận tính Idempotent hoạt động tốt!")

    # 7. Xem danh sách đặt chỗ của người dùng hiện tại
    print("\n6. Lấy danh sách đặt chỗ của người dùng hiện tại...")
    r_list = requests.get(f"{BOOKING_URL}/api/v1/bookings", headers=headers)
    print(f"   Status code: {r_list.status_code}")
    assert r_list.status_code == 200, f"Lấy danh sách đặt chỗ thất bại: {r_list.text}"
    bookings_list = r_list.json()
    print(f"   Tìm thấy {len(bookings_list)} đặt chỗ của bạn.")
    for b in bookings_list:
        print(f"     - [Booking: {b.get('id')}] Địa điểm: {b.get('place_id')}, Ngày: {b.get('booking_date')} lúc {b.get('start_time')}, Trạng thái: {b.get('status')}")
        
    # 8. Hủy đặt chỗ vừa tạo
    print(f"\n7. Tiến hành hủy đặt chỗ {booking_id}...")
    r_cancel = requests.patch(
        f"{BOOKING_URL}/api/v1/bookings/{booking_id}/cancel",
        headers=headers,
        json={"reason": "Test hủy đặt chỗ tự động"}
    )
    print(f"   Status code: {r_cancel.status_code}")
    assert r_cancel.status_code == 200, f"Hủy đặt chỗ thất bại: {r_cancel.text}"
    cancelled_data = r_cancel.json()
    print(f"   Hủy thành công! Trạng thái mới: {cancelled_data.get('status')}")
    
    print("\n" + "=" * 60)
    print("   🎉 KIỂM THỬ HOÀN TẤT: TẤT CẢ CÁC BƯỚC ĐÃ VƯỢT QUA THÀNH CÔNG!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
