import requests
import re

def get_coordinates(address: str) -> tuple[float, float]:
    """
    Sử dụng OpenStreetMap Nominatim API để chuyển đổi địa chỉ thành tọa độ GPS thực tế.
    Hỗ trợ nhiều biến thể tên: Đà Lạt, Da Lat, DaLat, Dalat, đà lạt...
    """
    default_coords = (11.940419, 108.458313) # Chợ Đà Lạt
    if not address or not address.strip():
        return default_coords
        
    try:
        print(f"🌍 [S1 Geocoding] Đang phân tích tọa độ cho: '{address}'...")
        url = "https://nominatim.openstreetmap.org/search"
        
        # Chuẩn hóa: kiểm tra xem đã chứa từ khóa "Đà Lạt" dưới mọi biến thể chưa
        address_normalized = re.sub(r'\s+', ' ', address.lower().strip())
        dalat_variants = ["đà lạt", "da lat", "dalat", "đa lạt", "đalạt"]
        has_dalat = any(v in address_normalized for v in dalat_variants)
        
        # Nếu chưa chứa, bổ sung ", Đà Lạt, Lâm Đồng, Việt Nam" để Nominatim tìm chính xác hơn
        search_query = address if has_dalat else f"{address}, Đà Lạt, Lâm Đồng, Việt Nam"
        
        params = {
            "q": search_query,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "CloudHuntingApp_S1/1.0"
        }
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                print(f"✅ [S1 Geocoding] Thành công: '{address}' → ({lat}, {lon})")
                return lat, lon
        
        # Nếu không tìm thấy, thử lần 2 chỉ với tên ngắn gọn + Đà Lạt
        # (Loại bỏ các từ phụ như "nhà nghỉ", "khách sạn", "quán cafe"...)
        simplified = re.sub(r'(nhà nghỉ|khách sạn|hotel|homestay|quán|cafe|cà phê)\s*', '', address, flags=re.IGNORECASE).strip()
        if simplified and simplified != address:
            print(f"🔄 [S1 Geocoding] Thử lại với tên rút gọn: '{simplified}'...")
            params["q"] = f"{simplified}, Đà Lạt, Lâm Đồng"
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    print(f"✅ [S1 Geocoding] Thành công (rút gọn): '{simplified}' → ({lat}, {lon})")
                    return lat, lon
                
        print(f"⚠️ [S1 Geocoding] Không tìm thấy tọa độ cho '{address}'. Trả về mặc định (Chợ Đà Lạt).")
    except Exception as e:
        print(f"❌ [S1 Geocoding] Lỗi khi gọi API: {e}. Trả về mặc định.")
        
    return default_coords
