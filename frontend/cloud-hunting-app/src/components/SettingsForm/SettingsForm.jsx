import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import cardStyles from '../CenterCard/CenterCard.module.css';
import styles from './SettingsForm.module.css';
import { predictCloud } from '../../bridge/s1_api';

export default function SettingsForm() {
  const navigate = useNavigate();
  const [locationName, setLocationName] = useState('Đà Lạt');
  const [range, setRange] = useState(15);
  const [timeOffset, setTimeOffset] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const timeLabel = timeOffset === 0 ? 'Hiện tại' : `+${timeOffset} giờ`;

  const handleScan = async () => {
    if (!locationName) return;
    setIsLoading(true);
    setError('');
    
    try {
      const data = await predictCloud(locationName, range, timeOffset);
      // Truyền dữ liệu sang trang kết quả
      navigate('/results', { state: { cloudData: data, timeOffset } });
    } catch (err) {
      setError(err.message || 'Lỗi khi dò mây');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={cardStyles.formView}>
      {error && <div style={{ color: 'red', marginBottom: '10px', fontSize: '0.9rem', textAlign: 'center' }}>{error}</div>}
      
      <div className={cardStyles.inputGroup}>
        <label>Địa điểm trung tâm</label>
        <input
          type="text"
          autoComplete="off"
          placeholder="Ví dụ: Đà Lạt"
          value={locationName}
          onChange={(e) => setLocationName(e.target.value)}
          disabled={isLoading}
        />
      </div>

      <div className={cardStyles.inputGroup}>
        <label className={styles.sliderLabel}>
          <span>Phạm vi dò</span>
          <span className={styles.sliderValue}>{range} km</span>
        </label>
        <input
          type="range"
          min="1"
          max="50"
          value={range}
          className={styles.slider}
          onChange={(e) => setRange(Number(e.target.value))}
          disabled={isLoading}
        />
      </div>

      <div className={cardStyles.inputGroup}>
        <label className={styles.sliderLabel}>
          <span>Thời gian</span>
          <span className={styles.sliderValue}>{timeLabel}</span>
        </label>
        <input
          type="range"
          min="0"
          max="72"
          step="1"
          value={timeOffset}
          className={styles.slider}
          onChange={(e) => setTimeOffset(Number(e.target.value))}
          disabled={isLoading}
        />
      </div>

      <button className={styles.scanBtn} onClick={handleScan} disabled={isLoading}>
        {isLoading ? 'ĐANG DÒ...' : 'DÒ'}
      </button>
    </div>
  );
}
