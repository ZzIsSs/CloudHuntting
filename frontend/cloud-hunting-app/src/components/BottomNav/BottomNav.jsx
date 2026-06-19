import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import styles from './BottomNav.module.css';
import AmenitiesModal from '../AiSchedule/AmenitiesModal';

export default function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();
  const [showAlternatives, setShowAlternatives] = useState(false);

  return (
    <>
      <div className={styles.bottomNav}>
        <button className={styles.navItem} onClick={() => setShowAlternatives(true)}>
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

      {showAlternatives && (
        <AmenitiesModal 
          onClose={() => setShowAlternatives(false)} 
          locName={location.state?.cloudData?.center_location || "Vị trí của bạn"}
        />
      )}
    </>
  );
}
