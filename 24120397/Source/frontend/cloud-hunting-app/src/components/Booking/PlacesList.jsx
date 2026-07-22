import React from 'react';
import styles from './PlacesList.module.css';

export default function PlacesList({ places = [], loading = false, onSelectPlace = () => {}, selectedPlaceId = null }) {
  if (loading) {
    return <div className={styles.placesList} style={{ padding: '20px' }}>Đang lọc danh sách địa điểm theo tiêu chí thực tế...</div>;
  }

  return (
    <div className={styles.placesList}>
      {places.map((place) => {
        const isSelected = place.id === selectedPlaceId;
        return (
          <div 
            key={place.id} 
            onClick={() => onSelectPlace(place)}
            className={styles.placeCard} 
            style={{
              borderColor: isSelected ? '#0ea5e9' : place.highlight ? '#bae6fd' : 'rgba(226, 232, 240, 0.5)',
              borderWidth: isSelected ? '2px' : '1px',
              boxShadow: isSelected ? '0 8px 25px rgba(14, 165, 233, 0.25)' : place.highlight ? '0 8px 20px rgba(0,0,0,0.08)' : '0 4px 10px rgba(0,0,0,0.03)',
              background: isSelected ? '#f0f9ff' : '#ffffff'
            }}
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
              <div className={styles.placeStats} style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, color: '#0284c7' }}>📍 Cách {place.distance_label || '1.2 km'}</span>
              </div>
            </div>
          </div>
        );
      })}
      {places.length === 0 && (
        <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
          Không tìm thấy địa điểm nào phù hợp bộ lọc hiện tại.
        </div>
      )}
    </div>
  );
}
