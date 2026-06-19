import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './ScheduleLayout.module.css';
import ScheduleTimeline from './ScheduleTimeline';
import WeatherAlert from './WeatherAlert';

export default function ScheduleLayout() {
  const [notifications, setNotifications] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchNotifications() {
      try {
        const token = localStorage.getItem('accessToken');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        const res = await fetch('http://127.0.0.1:8000/api/s6/notifications', { headers });
        if (res.ok) {
          const data = await res.json();
          setNotifications(data);
        }
      } catch (e) {
        console.error("Lỗi fetch thông báo:", e);
      }
    }
    fetchNotifications();
  }, []);

  return (
    <div className={styles.scheduleLayout}>
      <div className={styles.header}>
        <div className={styles.headerTitle}>
          <button className={styles.backBtn} onClick={() => navigate(-1)}>←</button>
          <h1>🤖 Lịch trình AI đề xuất: Đồi Đa Phú</h1>
        </div>
        <button className={styles.planBBtn}>Chuyển sang Plan B</button>
      </div>

      <ScheduleTimeline />
      
      {notifications.length > 0 ? (
        notifications.map((notif, idx) => (
          <WeatherAlert key={idx} message={notif.message} />
        ))
      ) : (
        <WeatherAlert message="Thời tiết hiện tại rất đẹp, chưa có cảnh báo nào!" />
      )}
    </div>
  );
}
