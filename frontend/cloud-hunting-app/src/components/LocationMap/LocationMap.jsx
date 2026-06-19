import { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import styles from './LocationMap.module.css';
import SovereigntyOverlay from './SovereigntyOverlay';

const fallbackData = [
  { location_name: 'Đồi chè Cầu Đất (11.8942, 108.5303)', probability: 95.5 },
  { location_name: 'Đỉnh Hòn Bồ (11.9688, 108.4811)', probability: 88.0 },
  { location_name: 'Đồi Đa Phú (11.9863, 108.4325)', probability: 82.5 },
  { location_name: 'Đồi Thiên Phúc Đức (11.9721, 108.4377)', probability: 75.0 },
  { location_name: 'Trại Mát (11.9443, 108.4975)', probability: 68.0 },
];

// Parse coordinates from location_name string OR use raw lat/lon if available
function parseLocation(loc) {
  // Ưu tiên sử dụng data trả về từ API S1 (đã có sẵn lat, lon, name rõ ràng)
  if (loc.lat !== undefined && loc.lon !== undefined) {
    return {
      lat: loc.lat,
      lng: loc.lon, // react-leaflet dùng thuộc tính lng
      name: loc.location_name,
      probability: loc.probability,
      suggestion: loc.suggestion || '',
    };
  }

  // Fallback (Dự phòng) cho mảng fallbackData cũ
  const match = loc.location_name.match(/\(([^,]+),\s*([^)]+)\)/);
  if (!match) return null;
  return {
    lat: parseFloat(match[1]),
    lng: parseFloat(match[2]),
    name: loc.location_name.split('(')[0].trim(),
    probability: loc.probability,
    suggestion: '',
  };
}

// Create custom div icon for ranked markers
function createMarkerIcon(rank) {
  const markerStyles = {
    gold: 'border-radius:50%;border:3px solid white;background:linear-gradient(135deg,#fcd34d,#d97706);width:36px;height:36px;font-size:18px;box-shadow:0 0 20px rgba(217,119,6,0.6);display:flex;justify-content:center;align-items:center;font-weight:800;color:white;font-family:Inter,sans-serif;text-shadow:1px 1px 2px rgba(0,0,0,0.5);',
    silver: 'border-radius:50%;border:3px solid white;background:linear-gradient(135deg,#f1f5f9,#94a3b8);width:30px;height:30px;font-size:15px;box-shadow:0 0 15px rgba(148,163,184,0.6);display:flex;justify-content:center;align-items:center;font-weight:800;color:white;font-family:Inter,sans-serif;text-shadow:1px 1px 2px rgba(0,0,0,0.5);',
    bronze: 'border-radius:50%;border:3px solid white;background:linear-gradient(135deg,#fdba74,#c2410c);width:26px;height:26px;font-size:13px;box-shadow:0 0 10px rgba(194,65,12,0.6);display:flex;justify-content:center;align-items:center;font-weight:800;color:white;font-family:Inter,sans-serif;text-shadow:1px 1px 2px rgba(0,0,0,0.5);',
    default: 'border-radius:50%;border:2px solid white;background:linear-gradient(135deg,#9ca3af,#4b5563);width:16px;height:16px;display:flex;justify-content:center;align-items:center;',
  };

  let style, size, text;
  if (rank === 0) { style = markerStyles.gold; size = [36, 36]; text = '1'; }
  else if (rank === 1) { style = markerStyles.silver; size = [30, 30]; text = '2'; }
  else if (rank === 2) { style = markerStyles.bronze; size = [26, 26]; text = '3'; }
  else { style = markerStyles.default; size = [16, 16]; text = ''; }

  return L.divIcon({
    className: '',
    html: `<div style="${style}">${text}</div>`,
    iconSize: size,
    iconAnchor: [size[0] / 2, size[1] / 2],
  });
}

// Auto-fit bounds to markers
function FitBounds({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (positions.length > 0) {
      map.fitBounds(positions, { padding: [50, 50] });
    }
  }, [map, positions]);
  return null;
}

export default function LocationMap({ data }) {
  const navigate = useNavigate();
  const location = useLocation();
  const hasSearched = !!location.state?.cloudData;
  const items = data && data.length > 0 ? data : (hasSearched ? [] : fallbackData);

  // Sort by probability descending for ranking
  const sorted = [...items].sort((a, b) => b.probability - a.probability);
  const parsed = sorted.map(parseLocation).filter(Boolean);
  const positions = parsed.map((p) => [p.lat, p.lng]);

  const centerLat = location.state?.cloudData?.center_lat || 11.9404;
  const centerLon = location.state?.cloudData?.center_lon || 108.4583;

  return (
    <div className={styles.mapWrapper}>
      <div className={styles.mapHeader}>
        <button className={styles.backBtn} onClick={() => navigate('/results', { state: location.state })}>
          ← Quay lại
        </button>
        Bản Đồ Các Địa Điểm Săn Mây
      </div>
      <div className={styles.mapContainer}>
        <MapContainer
          center={[centerLat, centerLon]}
          zoom={12}
          style={{ width: '100%', height: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            maxZoom={19}
          />
          <SovereigntyOverlay />
          <FitBounds positions={positions} />
          {parsed.map((loc, index) => (
            <Marker
              key={index}
              position={[loc.lat, loc.lng]}
              icon={createMarkerIcon(index)}
            >
              <Popup>
                <div style={{ fontFamily: 'Inter, sans-serif' }}>
                  <div style={{ fontWeight: 800, color: '#0284c7', marginBottom: 5, fontSize: '1.1rem' }}>
                    {loc.name}{' '}
                    {index < 3 && (
                      <span style={{ color: '#ea580c' }}>(Top {index + 1})</span>
                    )}
                  </div>
                  <div style={{ marginBottom: 4 }}>
                    Tỉ lệ săn mây: <b>{loc.probability}%</b>
                  </div>
                  {loc.suggestion && (
                    <div style={{ fontSize: '0.9rem', color: '#4b5563', fontStyle: 'italic' }}>
                      💡 {loc.suggestion}
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
