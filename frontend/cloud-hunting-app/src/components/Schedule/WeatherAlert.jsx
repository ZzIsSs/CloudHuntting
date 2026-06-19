import React from 'react';
import styles from './WeatherAlert.module.css';

export default function WeatherAlert({ message }) {
  if (!message) return null;
  
  return (
    <div className={styles.alertBanner}>
      ⚠️ Cảnh báo từ S6-AI: {message}
    </div>
  );
}
