import React from 'react';
import styles from './BookingLayout.module.css';
import PlacesList from './PlacesList';
import BookingMap from './BookingMap';

export default function BookingLayout() {
  return (
    <div className={styles.bookingLayout}>
      <div className={styles.header}>
        <div className={styles.headerTitle}>
          <button className={styles.backBtn}>←</button>
          <h1>🏨 Địa điểm lưu trú & Dịch vụ gần Đồi Đa Phú</h1>
        </div>
        <div className={styles.headerActions}>
          <button className={`${styles.filterBtn} ${styles.active}`}>Tất cả</button>
          <button className={styles.filterBtn}>Khách sạn</button>
          <button className={styles.filterBtn}>Homestay</button>
          <button className={styles.filterBtn}>Cắm trại</button>
        </div>
      </div>

      <div className={styles.bodyContent}>
        <PlacesList />
        <BookingMap />
      </div>
    </div>
  );
}
