import React from 'react';
import styles from './BookingMap.module.css';

export default function BookingMap() {
  return (
    <div className={styles.mapSection}>
      <div className={styles.mapContainer}>
        <div className={styles.mapPlaceholder}>
          <div className={styles.mapPin}></div>
        </div>
        
        {/* Thông tin đặt chỗ popup */}
        <div className={styles.bookingWidget}>
          <div className={styles.widgetInfo}>
            <h3>Khu cắm trại Mây Lang Thang</h3>
            <p>✅ Còn 3 lều trống hôm nay • 🌡️ 14°C Lạnh, khô ráo</p>
          </div>
          <button className={styles.btnBook}>Đặt ngay</button>
        </div>
      </div>
    </div>
  );
}
