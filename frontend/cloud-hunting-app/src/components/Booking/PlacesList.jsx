import React, { useState, useEffect } from 'react';
import styles from './PlacesList.module.css';

export default function PlacesList() {
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPlaces() {
      try {
        const token = localStorage.getItem('accessToken');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        // Tọa độ trung tâm Đà Lạt tạm thời
        const res = await fetch('http://127.0.0.1:8000/api/v1/places/nearby?lat=11.94&lon=108.44&radius_km=10', {
          headers
        });
        if (!res.ok) throw new Error('Network error');
        const data = await res.json();
        if (data.places) {
          setPlaces(data.places);
        }
      } catch (e) {
        console.error("Lỗi khi tải danh sách địa điểm:", e);
      } finally {
        setLoading(false);
      }
    }
    fetchPlaces();
  }, []);

  if (loading) {
    return <div className={styles.placesList} style={{ padding: '20px' }}>Đang tải danh sách địa điểm...</div>;
  }

  return (
    <div className={styles.placesList}>
      {places.map((place) => (
        <div 
          key={place.id} 
          className={styles.placeCard} 
          style={place.highlight ? { borderColor: '#bae6fd', boxShadow: '0 8px 20px rgba(0,0,0,0.08)' } : {}}
        >
          <img 
            src={place.primary_photo_url || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=200&q=80'} 
            alt={place.category} 
            className={styles.placeImage} 
          />
          <div className={styles.placeInfo}>
            <div>
              <div className={styles.placeTitle}>{place.name}</div>
              <span className={styles.placeCategory}>
                {place.category === 'hotel' ? 'Khách sạn' : place.category === 'homestay' ? 'Homestay' : place.category === 'cafe' ? 'Quán Cafe' : place.category === 'camping' ? 'Cắm trại' : place.category}
              </span>
            </div>
            <div className={styles.placeStats}>
              <span className={styles.rating}>⭐ {place.avg_rating} ({place.review_count})</span>
              <span>📍 Cách {place.distance_label}</span>
              <span className={styles.price}>{place.price_label}</span>
            </div>
          </div>
        </div>
      ))}
      {places.length === 0 && (
        <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
          Không tìm thấy địa điểm nào gần đây.
        </div>
      )}
    </div>
  );
}
