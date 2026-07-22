import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import styles from './BookingMap.module.css';
import SovereigntyOverlay from '../LocationMap/SovereigntyOverlay';

// Fix icon đường dẫn mặc định của Leaflet
import iconMarker from 'leaflet/dist/images/marker-icon.png';
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const customIcon = L.icon({
  iconUrl: iconMarker,
  iconRetinaUrl: iconRetina,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const redCenterIcon = L.divIcon({
  className: 'custom-red-spot-pin',
  html: `<div style="
    background: linear-gradient(135deg, #ef4444, #991b1b);
    width: 38px;
    height: 38px;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    border: 3px solid #ffffff;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
  "><span style="transform: rotate(45deg); font-size: 18px;">🎯</span></div>`,
  iconSize: [38, 38],
  iconAnchor: [19, 38],
  popupAnchor: [0, -38]
});

function MapFlyTo({ selectedPlace }) {
  const map = useMap();
  useEffect(() => {
    if (selectedPlace?.lat && selectedPlace?.lon) {
      map.flyTo([selectedPlace.lat, selectedPlace.lon], 18, { duration: 1.2 });
    }
  }, [map, selectedPlace]);
  return null;
}

function CenterSurveyButton({ targetSpot }) {
  const map = useMap();
  if (!targetSpot?.lat || !targetSpot?.lon) return null;

  return (
    <div className="leaflet-top leaflet-right" style={{ pointerEvents: 'auto', margin: '14px', zIndex: 1000 }}>
      <button
        onClick={(e) => {
          e.stopPropagation();
          map.flyTo([targetSpot.lat, targetSpot.lon], 15, { duration: 1.2 });
        }}
        style={{
          background: 'linear-gradient(135deg, #ef4444, #dc2626)',
          color: 'white',
          border: '2px solid white',
          padding: '8px 16px',
          borderRadius: '20px',
          fontWeight: 800,
          fontSize: '0.85rem',
          cursor: 'pointer',
          boxShadow: '0 4px 15px rgba(220, 38, 38, 0.45)',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          transition: 'all 0.2s',
          fontFamily: 'Inter, sans-serif'
        }}
        title="Đưa bản đồ về nơi trung tâm đang khảo sát"
      >
        <span>🎯</span>
        <span>Về trung tâm khảo sát</span>
      </button>
    </div>
  );
}

export default function BookingMap({ places = [], selectedPlace = null, targetSpot = null }) {
  const defaultLat = targetSpot?.lat || 11.9404;
  const defaultLon = targetSpot?.lon || 108.4583;

  return (
    <div className={styles.mapSection}>
      <div className={styles.mapContainer}>
        <MapContainer
          center={[defaultLat, defaultLon]}
          zoom={13}
          style={{ width: '100%', height: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap contributors'
          />
          <SovereigntyOverlay />
          <MapFlyTo selectedPlace={selectedPlace} />
          <CenterSurveyButton targetSpot={targetSpot} />

          {/* Ghim Đỏ: Trung Tâm Khảo Sát Săn Mây */}
          {targetSpot?.lat && targetSpot?.lon && (
            <Marker
              position={[targetSpot.lat, targetSpot.lon]}
              icon={redCenterIcon}
              zIndexOffset={1000}
            >
              <Popup autoPan={false}>
                <div style={{ fontFamily: 'Inter, sans-serif', textAlign: 'center', padding: '2px' }}>
                  <div style={{ background: '#fee2e2', color: '#dc2626', padding: '2px 8px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 800, display: 'inline-block', marginBottom: '4px' }}>
                    🚩 TRUNG TÂM KHẢO SÁT
                  </div>
                  <h4 style={{ margin: '0', color: '#b91c1c', fontSize: '1.05rem', fontWeight: 800 }}>{targetSpot.name}</h4>
                </div>
              </Popup>
            </Marker>
          )}

          {places.map((place) => {
            if (!place.lat || !place.lon) return null;
            return (
              <Marker
                key={place.id}
                position={[place.lat, place.lon]}
                icon={customIcon}
              >
                <Popup autoPan={false}>
                  <div style={{ fontFamily: 'Inter, sans-serif' }}>
                    <h4 style={{ margin: '0 0 5px 0', color: '#0ea5e9', fontSize: '1rem' }}>{place.name}</h4>
                    <p style={{ margin: '0', fontSize: '0.85rem', color: '#0284c7', fontWeight: 600 }}>
                      📍 {place.distance_label || '1.2 km'}
                    </p>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>

        {/* Thông tin định vị popup dưới góc */}
        {selectedPlace && (
          <div className={styles.bookingWidget}>
            <div className={styles.widgetInfo}>
              <h3 style={{ color: '#0ea5e9' }}>🎯 Đang chọn: {selectedPlace.name}</h3>
              <p>📍 {selectedPlace.address || 'Đà Lạt, Lâm Đồng'}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
