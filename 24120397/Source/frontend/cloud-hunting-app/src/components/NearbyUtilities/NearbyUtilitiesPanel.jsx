import { useState, useEffect } from 'react';
import styles from './NearbyUtilitiesPanel.module.css';
import { fetchNearbyUtilities } from '../../bridge/s2_api';

export default function NearbyUtilitiesPanel({ onBack, locName, lat: propLat, lon: propLon }) {
  const [utilities, setUtilities] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fallback to Chợ Đà Lạt if lat/lon not provided
  const lat = propLat || 11.9404;
  const lon = propLon || 108.4583;

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await fetchNearbyUtilities(lat, lon);
        setUtilities(data.places || []);
      } catch (err) {
        console.error('Error fetching utilities:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [lat, lon]);

  return (
    <div className={styles.panelContainer}>
      <div className={styles.panelHeader}>
        <button className={styles.backBtn} onClick={onBack}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
          Quay lại Đánh giá
        </button>
        <h2>Tiện ích quanh {locName}</h2>
      </div>
      
      <div className={styles.panelBody}>
        {loading ? (
          <div className={styles.loading}>Đang tải danh sách tiện ích...</div>
        ) : utilities.length === 0 ? (
          <div className={styles.empty}>Không tìm thấy tiện ích nào gần đây.</div>
        ) : (
          <div className={styles.utilitiesList}>
            {utilities.map(item => (
              <div key={item.id} className={styles.utilityCard}>
                {item.photos && item.photos.length > 0 && (
                  <img src={item.photos[0].url} alt={item.name} className={styles.utilImage} />
                )}
                <div className={styles.utilInfo}>
                  <div className={styles.utilHeader}>
                    <h3>{item.name}</h3>
                  </div>
                  <p className={styles.category}>{item.category} • Cách đây {item.distance_km || '1.5'} km</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
