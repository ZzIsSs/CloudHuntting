import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import styles from './BookingLayout.module.css';
import PlacesList from './PlacesList';
import BookingMap from './BookingMap';
import { fetchNearbyUtilities } from '../../bridge/s2_api';

export default function BookingLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Nhận tọa độ và tên điểm săn mây từ trang xếp hạng truyền sang
  const targetLat = location.state?.lat || 11.9404;
  const targetLon = location.state?.lon || 108.4583;
  const targetName = location.state?.name || 'ta';

  const [allPlaces, setAllPlaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('all');
  const [selectedAmenities, setSelectedAmenities] = useState([]);
  useEffect(() => {
    async function loadFilteredData() {
      try {
        setLoading(true);
        // Chỉ gửi các tham số tiện nghi chuẩn DB xuống Backend
        const dbAmenities = selectedAmenities.filter(a => a === 'cloud_view' || a === 'wifi');
        const data = await fetchNearbyUtilities(targetLat, targetLon, 'all', dbAmenities, 25, 50);
        let list = data?.places || [];

        // Ánh xạ thông minh đặc thù du lịch Đà Lạt cho các chip mở rộng
        if (selectedAmenities.includes('parking')) {
          list = list.filter(p => ['hotel', 'restaurant', 'homestay', 'camping'].includes(p.category));
        }
        if (selectedAmenities.includes('247')) {
          list = list.filter(p => p.category === 'camping' || p.category === 'homestay' || (p.amenities || []).includes('cloud_view'));
        }

        setAllPlaces(list);
      } catch (err) {
        console.error('Lỗi tải danh sách trực tiếp:', err);
        setAllPlaces([]);
      } finally {
        setLoading(false);
      }
    }
    loadFilteredData();
  }, [selectedAmenities]);

  // Đếm động Live Counts theo tiêu chí thực tế
  const categoryKeys = ['cafe', 'homestay', 'restaurant', 'hotel', 'camping'];
  const liveCounts = {
    all: allPlaces.length,
    ...categoryKeys.reduce((acc, cat) => {
      acc[cat] = allPlaces.filter(p => p.category === cat).length;
      return acc;
    }, {})
  };

  const toggleAmenity = (am) => {
    setSelectedAmenities(prev => 
      prev.includes(am) ? prev.filter(x => x !== am) : [...prev, am]
    );
  };

  const getCatLabel = (cat) => {
    switch (cat) {
      case 'cafe': return '☕ Cafe';
      case 'homestay': return '🏨 Homestay';
      case 'restaurant': return '🍜 Ăn uống';
      case 'hotel': return '🏢 Khách sạn';
      case 'camping': return '⛺ Cắm trại';
      default: return cat;
    }
  };

  const [selectedPlace, setSelectedPlace] = useState(null);

  // Lọc ra danh sách gửi xuống PlacesList theo tab đang chọn
  const displayPlaces = activeCategory === 'all' 
    ? allPlaces 
    : allPlaces.filter(p => p.category === activeCategory);

  return (
    <div className={styles.bookingLayout}>
      <div className={styles.header}>
        <div className={styles.headerTitle}>
          <button className={styles.backBtn} onClick={() => navigate(-1)}>←</button>
          <h1>🌟 Tiện ích quanh {targetName}</h1>
        </div>

        <div className={styles.headerActions} style={{marginTop: '15px'}}>
          <button 
            className={`${styles.filterBtn} ${activeCategory === 'all' ? styles.active : ''}`}
            onClick={() => { setActiveCategory('all'); setSelectedPlace(null); }}
          >
            🌟 Tất cả ({liveCounts.all})
          </button>
          {categoryKeys.map(cat => (
            <button 
              key={cat}
              className={`${styles.filterBtn} ${activeCategory === cat ? styles.active : ''}`}
              onClick={() => { setActiveCategory(cat); setSelectedPlace(null); }}
            >
              {getCatLabel(cat)} ({liveCounts[cat] || 0})
            </button>
          ))}
        </div>
        
        {/* Hàng lọc Tiện nghi nhanh */}
        <div style={{ display: 'flex', gap: '10px', marginTop: '15px', flexWrap: 'wrap' }}>
          <span style={{ fontWeight: '600', color: '#334155', alignSelf: 'center' }}>⚡ Lọc tiện nghi:</span>
          {[
            { id: 'cloud_view', label: '☁️ View Săn Mây' },
            { id: 'parking', label: '🅿️ Có bãi đỗ xe' },
            { id: 'wifi', label: '📶 Wifi mạnh' },
            { id: '247', label: '🌙 Mở cửa đêm 4h sáng' }
          ].map(chip => (
            <button
              key={chip.id}
              onClick={() => toggleAmenity(chip.id)}
              style={{
                padding: '6px 14px',
                borderRadius: '20px',
                border: selectedAmenities.includes(chip.id) ? '2px solid #0ea5e9' : '1px solid #cbd5e1',
                background: selectedAmenities.includes(chip.id) ? '#e0f2fe' : 'white',
                color: selectedAmenities.includes(chip.id) ? '#0284c7' : '#475569',
                fontWeight: selectedAmenities.includes(chip.id) ? 'bold' : 'normal',
                cursor: 'pointer',
                transition: 'all 0.2s',
                fontSize: '0.85rem'
              }}
            >
              {selectedAmenities.includes(chip.id) ? '☑️ ' : '☐ '}{chip.label}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.bodyContent}>
        <PlacesList 
          places={displayPlaces} 
          loading={loading} 
          onSelectPlace={setSelectedPlace}
          selectedPlaceId={selectedPlace?.id}
        />
        <BookingMap 
          places={displayPlaces}
          selectedPlace={selectedPlace}
        />
      </div>
    </div>
  );
}
