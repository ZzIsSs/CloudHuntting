# src/s2_booking/geocoding.py
import requests
import re

DEFAULT_COORDS = (11.940419, 108.458313)  # Chợ Đà Lạt


def get_coordinates(address: str) -> tuple[float, float]:
    """
    Chuyển tên địa điểm thành tọa độ GPS.
    Copy từ S1 geocoding_service.py — dùng chung Nominatim API.
    """
    if not address or not address.strip():
        return DEFAULT_COORDS

    try:
        url = "https://nominatim.openstreetmap.org/search"

        address_normalized = re.sub(r'\s+', ' ', address.lower().strip())
        dalat_variants = ["đà lạt", "da lat", "dalat", "đa lạt", "đalạt"]
        has_dalat = any(v in address_normalized for v in dalat_variants)

        search_query = address if has_dalat else f"{address}, Đà Lạt, Lâm Đồng, Việt Nam"

        params  = {"q": search_query, "format": "json", "limit": 1}
        headers = {"User-Agent": "CloudHuntingApp_S2/1.0"}

        response = requests.get(url, params=params, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])

        # Thử lại với tên rút gọn
        simplified = re.sub(
            r'(nhà nghỉ|khách sạn|hotel|homestay|quán|cafe|cà phê)\s*',
            '', address, flags=re.IGNORECASE
        ).strip()

        if simplified and simplified != address:
            params["q"] = f"{simplified}, Đà Lạt, Lâm Đồng"
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"])

    except Exception:
        pass

    return DEFAULT_COORDS