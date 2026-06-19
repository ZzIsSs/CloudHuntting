import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import styles from './Carousel.module.css';

const placeholderSvg = `
<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
    <rect width="100" height="60" fill="#f0f9ff"/>
    <path d="M 0 60 Q 25 30 50 50 T 100 40 L 100 60 Z" fill="#a3e635"/>
    <path d="M 0 60 Q 30 40 60 55 T 100 50 L 100 60 Z" fill="#84cc16"/>
    <circle cx="45" cy="22" r="6" fill="white"/>
    <circle cx="55" cy="25" r="8" fill="white"/>
    <circle cx="38" cy="26" r="5" fill="white"/>
    <rect x="38" y="22" width="17" height="9" rx="4.5" fill="white"/>
    <circle cx="20" cy="15" r="4" fill="rgba(255,255,255,0.7)"/>
    <circle cx="28" cy="18" r="6" fill="rgba(255,255,255,0.7)"/>
    <rect x="20" y="15" width="8" height="9" rx="4" fill="rgba(255,255,255,0.7)"/>
</svg>`;

const fallbackData = [
  { location_name: 'Đồi chè Cầu Đất (11.894, 108.530)', probability: 95.5, distance_km: 25.4 },
  { location_name: 'Đỉnh Hòn Bồ (11.968, 108.481)', probability: 88.0, distance_km: 12.0 },
  { location_name: 'Đồi Đa Phú (11.986, 108.432)', probability: 82.5, distance_km: 10.5 },
  { location_name: 'Đồi Thiên Phúc Đức (11.972, 108.437)', probability: 75.0, distance_km: 8.2 },
  { location_name: 'Trại Mát (11.944, 108.497)', probability: 68.0, distance_km: 15.0 },
];

function getVisibleCount() {
  if (window.innerWidth <= 600) return 1;
  if (window.innerWidth <= 900) return 2;
  return 3;
}

function getItemWidth() {
  if (window.innerWidth <= 600) return 100;
  if (window.innerWidth <= 900) return 50;
  return 33.3333;
}

export default function Carousel({ data }) {
  const navigate = useNavigate();
  const location = useLocation();
  const items = data && data.length > 0 ? data : fallbackData;
  const [currentIndex, setCurrentIndex] = useState(0);
  const [visibleCount, setVisibleCount] = useState(getVisibleCount);

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      const newVisible = getVisibleCount();
      setVisibleCount(newVisible);
      setCurrentIndex((prev) => Math.min(prev, Math.max(0, items.length - newVisible)));
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [items.length]);

  const canPrev = currentIndex > 0;
  const canNext = currentIndex < items.length - visibleCount;

  const handlePrev = useCallback(() => {
    if (canPrev) setCurrentIndex((i) => i - 1);
  }, [canPrev]);

  const handleNext = useCallback(() => {
    if (canNext) setCurrentIndex((i) => i + 1);
  }, [canNext]);

  const handleCardClick = useCallback(
    (item) => {
      const nameOnly = item.location_name.split('(')[0].trim().toLowerCase();
      navigate(`/ranking?name=${encodeURIComponent(nameOnly)}`, { 
        state: { 
          ...location.state, 
          image_url: item.image_url,
          lat: item.lat,
          lon: item.lon
        } 
      });
    },
    [navigate, location.state]
  );

  const trackOffset = currentIndex * getItemWidth();

  return (
    <div className={styles.carouselContainer}>
      {/* Left Arrow */}
      <button
        className={`${styles.navArrow} ${!canPrev ? styles.disabled : ''}`}
        onClick={handlePrev}
        disabled={!canPrev}
      >
        <svg viewBox="0 0 60 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M 60 0 L 0 40 L 60 80 Z" fill="#0284c7" />
        </svg>
      </button>

      {/* Track */}
      <div className={styles.trackWrapper}>
        <div
          className={styles.track}
          style={{ transform: `translateX(-${trackOffset}%)` }}
        >
          {items.map((item, index) => {
            const nameOnly = item.location_name.split('(')[0].trim().toLowerCase();
            return (
              <div
                key={index}
                className={styles.card}
                onClick={() => handleCardClick(item)}
              >
                {item.image_url ? (
                  <div className={styles.cardImage}>
                    <img 
                      src={item.image_url} 
                      alt={nameOnly} 
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                    />
                  </div>
                ) : (
                  <div
                    className={styles.cardImage}
                    dangerouslySetInnerHTML={{ __html: placeholderSvg }}
                  />
                )}
                <div className={styles.cardTitle}>{nameOnly}</div>
                <div className={styles.cardSubtitle}>
                  Tỉ lệ mây: {item.probability}% | {item.distance_km}km
                </div>
                {item.best_time && (
                  <div style={{ fontSize: '0.85rem', color: '#0369a1', marginTop: '4px', fontWeight: 'bold', background: '#e0f2fe', padding: '2px 8px', borderRadius: '12px', display: 'inline-block' }}>
                    ⏰ Giờ đẹp: {item.best_time.includes('T') ? new Date(item.best_time).toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' }) : item.best_time}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Arrow */}
      <button
        className={`${styles.navArrow} ${!canNext ? styles.disabled : ''}`}
        onClick={handleNext}
        disabled={!canNext}
      >
        <svg viewBox="0 0 60 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M 0 0 L 60 40 L 0 80 Z" fill="#0284c7" />
        </svg>
      </button>
    </div>
  );
}
