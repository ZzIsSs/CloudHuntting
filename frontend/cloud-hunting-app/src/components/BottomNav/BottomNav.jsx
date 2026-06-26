import { useNavigate, useLocation } from 'react-router-dom';
import styles from './BottomNav.module.css';

export default function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleGoToBooking = () => {
    const cData = location.state?.cloudData || {};
    // Lấy tọa độ khảo sát ban đầu (ưu tiên user_lat/lon gốc, nếu không lấy điểm đầu tiên hoặc trung tâm Đà Lạt)
    const lat = cData.user_lat || cData.top_spots?.[0]?.lat || 11.9404;
    const lon = cData.user_lon || cData.top_spots?.[0]?.lon || 108.4583;
    const rawName = cData.center_location || cData.top_spots?.[0]?.location_name || "Khu vực khảo sát ban đầu";
    const cleanName = rawName.split('(')[0].trim();

    navigate(`/booking?lat=${lat}&lon=${lon}&name=${encodeURIComponent(cleanName)}`);
  };

  return (
    <div className={styles.bottomNav}>
      <button className={styles.navItem} onClick={handleGoToBooking}>
        Các địa điểm tham quan thay thế
      </button>
      <button className={styles.navItem} onClick={() => navigate('/map', { state: location.state })}>
        Bản đồ các địa điểm
      </button>
      <button className={styles.navItem} onClick={() => navigate('/')}>
        Chọn địa điểm mới
      </button>
      <button className={styles.navItem} onClick={() => navigate('/detail', { state: location.state })}>
        Bảng thống kê
      </button>
    </div>
  );
}
