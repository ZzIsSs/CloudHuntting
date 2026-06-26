import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import styles from './BookingLayout.module.css';
import PlacesList from './PlacesList';
import BookingMap from './BookingMap';
import CloudGameLayer from '../CloudGameLayer/CloudGameLayer';
import TopRightNav from '../TopRightNav/TopRightNav';
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

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/');
  };

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', overflow: 'hidden', position: 'relative', background: '#bae6fd' }}>
      <CloudGameLayer />
      <TopRightNav onLogout={handleLogout} />

      <div className={styles.bookingLayout} style={{ position: 'absolute', top: '55%', left: '50%', transform: 'translate(-50%, -50%)', width: '95%', maxWidth: '1400px', height: '85vh', zIndex: 10, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div className={styles.header} style={{ flexShrink: 0 }}>
          <div className={styles.headerTitle}>
            <button className={styles.backBtn} onClick={() => navigate(-1)}>←</button>
            <h1>🌟 Tiện ích quanh {targetName}</h1>
          </div>

          <div className={styles.headerActions} style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center' }}>
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

            {/* Hộp chọn lọc Tiện nghi dạng Dropdown gọn gàng */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: '6px' }}>
              <span style={{ fontWeight: '600', color: '#0284c7', fontSize: '0.9rem' }}>⚡ Tiện nghi:</span>
              <select
                value={selectedAmenities[0] || 'all'}
                onChange={(e) => {
                  const val = e.target.value;
                  setSelectedAmenities(val === 'all' ? [] : [val]);
                  setSelectedPlace(null);
                }}
                style={{
                  padding: '8px 16px',
                  borderRadius: '12px',
                  border: selectedAmenities.length > 0 ? '2px solid #0ea5e9' : '1px solid #cbd5e1',
                  background: selectedAmenities.length > 0 ? '#e0f2fe' : '#ffffff',
                  color: selectedAmenities.length > 0 ? '#0284c7' : '#334155',
                  fontWeight: selectedAmenities.length > 0 ? 'bold' : '600',
                  cursor: 'pointer',
                  outline: 'none',
                  fontSize: '0.88rem',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
                  transition: 'all 0.2s',
                  fontFamily: 'Inter, sans-serif'
                }}
              >
                <option value="all">🌟 Tất cả tiện nghi</option>
                <option value="cloud_view">☁️ View Săn Mây</option>
                <option value="parking">🅿️ Có bãi đỗ xe</option>
                <option value="wifi">📶 Wifi mạnh</option>
                <option value="247">🌙 Mở cửa đêm 4h sáng</option>
              </select>
            </div>
          </div>
        </div>

        <div className={styles.bodyContent} style={{ flex: 1, display: 'flex', overflow: 'hidden', minHeight: 0 }}>
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
    </div>
  );
}
