import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Top 10 địa điểm săn mây nổi tiếng tại Đà Lạt
# Nguồn: https://www.traveloka.com/vi-vn/explore/destination/dia-diem-san-may-da-lat/193581
import json
import os

# Đường dẫn tới file JSON lưu cấu hình dùng chung
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOTSPOTS_JSON_PATH = os.path.join(BASE_DIR, "shared", "hotspots.json")

try:
    with open(HOTSPOTS_JSON_PATH, "r", encoding="utf-8") as f:
        HOTSPOTS = json.load(f)
except Exception as e:
    print(f"⚠️ [Pipeline] Không thể đọc file hotspots.json: {e}")
    HOTSPOTS = []

def get_historical_weather(lat, lon, start_date, end_date):
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,pressure_msl,cloud_cover_low,cloud_cover_high,dew_point_2m"
        f"&timezone=Asia%2FHo_Chi_Minh"
    )
    
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        raise Exception(f"Lỗi khi gọi API: {response.text}")
        
    data = response.json()
    hourly = data.get('hourly', {})
    
    if not hourly:
        return pd.DataFrame()
        
    df = pd.DataFrame(hourly)
    df['time'] = pd.to_datetime(df['time'])
    return df

def generate_labels(df):
    """
    Tự động gắn nhãn (Auto-labeling) dựa trên quy tắc chuyên gia đã cải tiến.
    """
    print("Đang tiến hành gắn nhãn tự động cho tập dữ liệu tổng hợp...")
    
    # Tính toán chênh lệch nhiệt độ và điểm sương (càng nhỏ càng dễ ngưng tụ)
    df['spread'] = df['temperature_2m'] - df['dew_point_2m']
    
    # Tiêu chí KHOA HỌC KHÍ TƯỢNG cho biển mây (Cloud Sea / Sea of Clouds):
    #
    # [1] relative_humidity_2m >= 92%
    #     Cơ sở: Biển mây hình thành khi không khí gần bão hòa hoàn toàn (100%).
    #     Ngưỡng 85% cũ chỉ là không khí ẩm, chưa đủ để mây tầng thấp ngưng tụ đặc.
    #
    # [2] spread (T - Td) <= 1.5°C
    #     Cơ sở: Khi spread < 2°C không khí gần điểm sương. Chọn 1.5°C để
    #     chọn những điều kiện ngưng tụ mạnh hơn → biển mây dày đặc, đẹp hơn.
    #
    # [3] wind_speed_10m: 1.0 <= x <= 8 km/h (có giới hạn HAI ĐẦU)
    #     Cơ sở: Gió > 8 km/h gây nhiễu loạn, phá vỡ lớp nghịch nhiệt → mây tan.
    #     Nhưng gió < 1 km/h → không khí tĩnh hoàn toàn, sương mù ứ đọng thành
    #     màn dày đặc, không tạo được "biển mây lăn" đẹp (rolling sea of clouds).
    #
    # [4] cloud_cover_low >= 70%
    #     Cơ sở: 50% mây thấp chỉ là mây rải rác (scattered). Cần >= 70% để
    #     tạo thành lớp stratus liên tục — biển mây thực sự nhìn từ trên cao.
    #
    # [5] cloud_cover_high <= 30%
    #     Cơ sở: Mây cao (cirrus, cirrostratus) dày đặc che khuất ánh nắng mặt trời
    #     mọc, triệt tiêu hiệu ứng "mây nhuộm hồng/vàng" lúc bình minh — mất đi
    #     giá trị thẩm mỹ của cảnh săn mây.
    #
    # [6] pressure_msl >= 1012 hPa  (ĐIỀU KIỆN THÊM MỚI)
    #     Cơ sở: Vùng áp cao (anticyclone) tạo ra "sinking air" — khí quyển ổn định,
    #     giữ nguyên lớp nghịch nhiệt và ngăn đối lưu. Đây là điều kiện tiên quyết
    #     cho biển mây ổn định, kéo dài vào buổi sáng.
    condition = (
        (df['relative_humidity_2m'] >= 92) &          # Bão hòa gần hoàn toàn
        (df['spread'] <= 1.5) &                       # Nhiệt độ ≈ điểm sương
        (df['wind_speed_10m'] >= 1.0) &               # Đủ gió để mây lăn đẹp
        (df['wind_speed_10m'] <= 8.0) &               # Không đủ mạnh để phá mây
        (df['cloud_cover_low'] >= 70) &               # Lớp mây thấp đủ dày → biển mây
        (df['cloud_cover_high'] <= 30) &              # Bầu trời trên cao quang đãng
        (df['pressure_msl'] >= 1012)                  # Áp cao → khí quyển ổn định
    )

    df['is_cloud_hunting_good'] = condition.astype(int)
    return df

def main():
    end_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    all_dfs = []
    
    print(f"Bắt đầu thu thập dữ liệu lịch sử từ {start_date} đến {end_date}...")
    
    try:
        for spot in HOTSPOTS:
            print(f"👉 Đang tải dữ liệu cho: {spot['name']}...")
            df_spot = get_historical_weather(spot['lat'], spot['lon'], start_date, end_date)
            if not df_spot.empty:
                df_spot['location'] = spot['name']
                all_dfs.append(df_spot)
            time.sleep(1) # Tránh bị Open-Meteo rate limit
            
        if not all_dfs:
            print("Không tải được bất kỳ dữ liệu nào.")
            return
            
        # Gộp tất cả dataframe lại
        df_total = pd.concat(all_dfs, ignore_index=True)
        
        # Xóa missing
        df_total = df_total.dropna()
        
        # Sinh nhãn
        df_total = generate_labels(df_total)
        
        # Lọc giờ sáng sớm
        df_total['hour'] = df_total['time'].dt.hour
        df_morning = df_total[df_total['hour'].isin([3, 4, 5, 6, 7])].copy()
        
        print("\n--- THỐNG KÊ TẬP DỮ LIỆU TOÀN QUỐC ---")
        print(f"Tổng số mẫu dữ liệu rạng sáng: {len(df_morning)}")
        print(f"Số mẫu có biển mây lý tưởng: {df_morning['is_cloud_hunting_good'].sum()}")
        
        for spot in HOTSPOTS:
            spot_data = df_morning[df_morning['location'] == spot['name']]
            spot_clouds = spot_data['is_cloud_hunting_good'].sum()
            print(f"- {spot['name']}: {spot_clouds} ngày mây đẹp / {len(spot_data)} ngày")
        
        # Lưu CSV
        output_path = "historical_weather.csv"
        df_morning.to_csv(output_path, index=False)
        print(f"\n✅ Đã lưu tập dữ liệu siêu to khổng lồ vào {output_path}")
        
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    main()
