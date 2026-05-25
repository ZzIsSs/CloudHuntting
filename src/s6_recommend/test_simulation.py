import sys
import os
from unittest.mock import patch

# Đưa thư mục src vào sys.path để có thể import s6_recommend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from s6_recommend.schemas import UserPreferenceRequest, PlanBRequest
from s6_recommend.services import score_locations, generate_itinerary, switch_to_plan_b

def run_simulation():
    print("="*60)
    print("KỊCH BẢN 1: KHU VỰC CÓ MÂY (THỜI TIẾT LÝ TƯỞNG)")
    print("="*60)
    
    # Giả lập S1 luôn trả về 85% mây và S5 trả về trend "Tăng"
    with patch('s6_recommend.services.fetch_s1_prediction', return_value=85.0):
        with patch('s6_recommend.services.fetch_s5_trend', return_value="Tăng"):
            req1 = UserPreferenceRequest(
                user_id="user_test",
                start_time="04:30",
                start_location="Chợ Đà Lạt",
                max_distance_km=30.0,
                travel_style="Sống ảo nhẹ nhàng",
                preferred_vibe="Thương mại",
                vehicle_type="Xe máy"
            )
            
            # Tìm điểm tốt nhất
            best_locs = score_locations(req1)
            print(f"🌟 Điểm đến tốt nhất: {best_locs[0].location_name} (Tỷ lệ mây: {best_locs[0].probability}%)")
            
            # Sinh lịch trình
            itinerary1 = generate_itinerary(req1, best_locs)
            print(f"💬 Thông báo hệ thống: {itinerary1.message}")
            print("\n📅 LỊCH TRÌNH CHI TIẾT:")
            for step in itinerary1.timeline:
                print(f"  ⏰ {step.time} | 📍 {step.location}")
                print(f"     👉 Hành động: {step.action}")
                print(f"     📝 Ghi chú: {step.note}\n")

    print("="*60)
    print("KỊCH BẢN 2: KHU VỰC KHÔNG CÓ MÂY (THỜI TIẾT XẤU)")
    print("="*60)
    
    # Giả lập S1 trả về thời tiết rất xấu (20% mây) cho toàn bộ Đà Lạt
    with patch('s6_recommend.services.fetch_s1_prediction', return_value=20.0):
        with patch('s6_recommend.services.fetch_s5_trend', return_value="Giảm"):
            req2 = PlanBRequest(
                user_id="user_test",
                start_time="04:30",
                start_location="Chợ Đà Lạt",
                current_target_location="Đồi chè Cầu Đất",
                max_distance_km=30.0,
                travel_style="Sống ảo nhẹ nhàng",
                preferred_vibe="Thương mại",
                vehicle_type="Xe máy"
            )
            
            # Kích hoạt tính năng Cứu Nét (Plan B)
            # Bởi vì toàn bộ các điểm đều bị mock là 20%, hệ thống sẽ không tìm được điểm thay thế tốt 
            # và sẽ phải kích hoạt kịch bản dừng chân khẩn cấp.
            itinerary2 = switch_to_plan_b(req2)
            
            print(f"💬 Thông báo hệ thống: {itinerary2.message}")
            print("\n📅 LỊCH TRÌNH KHẨN CẤP (DỪNG CHÂN):")
            for step in itinerary2.timeline:
                print(f"  ⏰ {step.time} | 📍 {step.location}")
                print(f"     👉 Hành động: {step.action}")
                print(f"     📝 Ghi chú: {step.note}\n")

if __name__ == "__main__":
    run_simulation()
