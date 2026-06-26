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
  const [isOpenAmenityDropdown, setIsOpenAmenityDropdown] = useState(false);

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

            {/* Hộp chọn lọc Tiện nghi dạng Dropdown Multi-Select gọn gàng */}
            <div style={{ position: 'relative', marginLeft: '6px' }}>
              <button
                onClick={() => setIsOpenAmenityDropdown(!isOpenAmenityDropdown)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 16px',
                  borderRadius: '12px',
                  border: selectedAmenities.length > 0 ? '2px solid #0ea5e9' : '1px solid #cbd5e1',
                  background: selectedAmenities.length > 0 ? '#e0f2fe' : '#ffffff',
                  color: selectedAmenities.length > 0 ? '#0284c7' : '#334155',
                  fontWeight: selectedAmenities.length > 0 ? 'bold' : '600',
                  cursor: 'pointer',
                  fontSize: '0.88rem',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.03)',
                  transition: 'all 0.2s',
                  fontFamily: 'Inter, sans-serif'
                }}
              >
                <span>⚡ Tiện nghi {selectedAmenities.length > 0 ? `(${selectedAmenities.length})` : ''}</span>
                <span style={{ fontSize: '0.7rem' }}>{isOpenAmenityDropdown ? '▲' : '▼'}</span>
              </button>

              {isOpenAmenityDropdown && (
                <div style={{
                  position: 'absolute',
                  top: 'calc(100% + 8px)',
                  right: 0,
                  width: '240px',
                  background: 'white',
                  borderRadius: '16px',
                  border: '1px solid #e2e8f0',
                  boxShadow: '0 12px 30px rgba(0,0,0,0.15)',
                  padding: '12px',
                  zIndex: 300,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                  textAlign: 'left'
                }}>
                  <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#64748b', borderBottom: '1px solid #f1f5f9', paddingBottom: '6px', marginBottom: '2px' }}>
                    ☑️ Chọn nhiều tiện nghi:
                  </div>
                  {[
                    { id: 'cloud_view', label: '☁️ View Săn Mây' },
                    { id: 'parking', label: '🅿️ Có bãi đỗ xe' },
                    { id: 'wifi', label: '📶 Wifi mạnh' },
                    { id: '247', label: '🌙 Mở cửa đêm 4h sáng' }
                  ].map(item => {
                    const checked = selectedAmenities.includes(item.id);
                    return (
                      <label
                        key={item.id}
                        onClick={(e) => {
                          e.preventDefault();
                          toggleAmenity(item.id);
                        }}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          padding: '8px 10px',
                          borderRadius: '8px',
                          background: checked ? '#f0f9ff' : 'transparent',
                          color: checked ? '#0284c7' : '#334155',
                          fontWeight: checked ? 700 : 500,
                          cursor: 'pointer',
                          fontSize: '0.86rem',
                          transition: 'background 0.15s'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => {}}
                          style={{ cursor: 'pointer', accentColor: '#0ea5e9', width: '16px', height: '16px' }}
                        />
                        <span>{item.label}</span>
                      </label>
                    );
                  })}
                  {selectedAmenities.length > 0 && (
                    <button
                      onClick={() => setSelectedAmenities([])}
                      style={{
                        marginTop: '4px',
                        padding: '6px',
                        border: 'none',
                        background: '#fee2e2',
                        color: '#dc2626',
                        borderRadius: '6px',
                        fontSize: '0.8rem',
                        fontWeight: 700,
                        cursor: 'pointer'
                      }}
                    >
                      ✕ Bỏ chọn tất cả
                    </button>
                  )}
                </div>
              )}
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
            targetSpot={{ lat: targetLat, lon: targetLon, name: targetName }}
          />
        </div>
      </div>
    </div>
  );
}
