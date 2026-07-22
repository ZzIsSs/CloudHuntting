import { useState } from 'react';
import styles from './AiScheduleModal.module.css';
import { recommendItinerary } from '../../bridge/s6_api';
import { getSmartStartTime } from '../../utils/timeUtils';

export default function AiScheduleModal({ onClose, locName, lat, lon, timeOffset = 0 }) {
  const [timeAvailable, setTimeAvailable] = useState(getSmartStartTime(timeOffset));
  const [vehicle, setVehicle] = useState('Xe máy');
  const [style, setStyle] = useState('Sống ảo');
  const [vibe, setVibe] = useState('Cặp đôi');
  const [loading, setLoading] = useState(false);
  const [schedule, setSchedule] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const preferences = {
        user_id: 1,
        start_time: timeAvailable,
        vehicle_type: vehicle,
        travel_style: style,
        preferred_vibe: vibe,
        start_location: "Chợ Đà Lạt", // hardcode as starting point
        max_distance_km: 50,
        selected_location: locName // Bắt buộc truyền lên backend để AI biết đang chọn điểm nào
      };
      const res = await recommendItinerary(preferences);
      setSchedule(res);
    } catch (err) {
      alert("Lỗi khi gọi AI: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>✨ Lên lịch trình A.I cho {locName}</h2>
          <button className={styles.closeBtn} onClick={onClose}>×</button>
        </div>
        
        <div className={styles.modalBody}>
          {!schedule ? (
            <form onSubmit={handleSubmit} className={styles.aiForm}>
              <div className={styles.formGroup}>
                <label>Giờ xuất phát dự kiến:</label>
                <input type="time" value={timeAvailable} onChange={e => setTimeAvailable(e.target.value)} required />
              </div>
              <div className={styles.formGroup}>
                <label>Phương tiện:</label>
                <select value={vehicle} onChange={e => setVehicle(e.target.value)}>
                  <option value="Xe máy">Xe máy</option>
                  <option value="Ô tô">Ô tô</option>
                </select>
              </div>
              <div className={styles.formGroup}>
                <label>Phong cách:</label>
                <select value={style} onChange={e => setStyle(e.target.value)}>
                  <option value="Sống ảo">Sống ảo</option>
                  <option value="Cắm trại">Cắm trại</option>
                  <option value="Chill">Chill</option>
                  <option value="Khám phá">Khám phá</option>
                </select>
              </div>
              <div className={styles.formGroup}>
                <label>Bạn đi cùng ai (Vibe):</label>
                <select value={vibe} onChange={e => setVibe(e.target.value)}>
                  <option value="Cặp đôi">Cặp đôi</option>
                  <option value="Nhóm bạn">Nhóm bạn</option>
                  <option value="Gia đình">Gia đình</option>
                  <option value="Một mình">Một mình</option>
                </select>
              </div>
              <button type="submit" className={styles.submitBtn} disabled={loading}>
                {loading ? 'Đang phân tích...' : 'Tạo lịch trình'}
              </button>
            </form>
          ) : (
            <div className={styles.resultContainer}>
              <div className={styles.successMessage} style={{ marginBottom: '15px', color: '#0284c7', fontWeight: 'bold' }}>
                {schedule.message ? `✅ ${schedule.message}` : "✅ Đã tạo xong lịch trình phù hợp với bạn!"}
              </div>
              
              {schedule.recommended_locations && schedule.recommended_locations[0].score === 0 && (
                <div style={{ background: '#fef2f2', padding: '15px', borderRadius: '10px', marginBottom: '20px', border: '1px solid #fecaca' }}>
                  <h4 style={{ color: '#ef4444', margin: '0 0 10px 0' }}>🎯 Tiện ích quanh bạn:</h4>
                  <ul style={{ margin: 0, paddingLeft: '20px', color: '#7f1d1d' }}>
                    {schedule.recommended_locations.map((loc, idx) => (
                      <li key={idx} style={{ marginBottom: '5px' }}>{loc.location_name}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className={styles.timeline}>
                {schedule.timeline && schedule.timeline.map((step, idx) => (
                  <div key={idx} className={styles.timelineItem}>
                    <div className={styles.timeTag}>{step.time}</div>
                    <div className={styles.stepContent}>
                      <h4>{step.action}</h4>
                      {step.location && <p className={styles.locationTag}>📍 {step.location}</p>}
                      {step.note && <p className={styles.stepNote}>{step.note}</p>}
                    </div>
                  </div>
                ))}
              </div>
              <button className={styles.submitBtn} onClick={() => setSchedule(null)} style={{ marginTop: '20px', background: '#64748b' }}>
                Tạo lại
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
