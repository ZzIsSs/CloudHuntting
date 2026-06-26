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

function MapFlyTo({ selectedPlace }) {
  const map = useMap();
  useEffect(() => {
    if (selectedPlace?.lat && selectedPlace?.lon) {
      map.flyTo([selectedPlace.lat, selectedPlace.lon], 18, { duration: 1.2 });
    }
  }, [map, selectedPlace]);
  return null;
}

export default function BookingMap({ places = [], selectedPlace = null }) {
  const defaultLat = 11.9404;
  const defaultLon = 108.4583;

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

          {places.map((place) => {
            if (!place.lat || !place.lon) return null;
            return (
              <Marker
                key={place.id}
                position={[place.lat, place.lon]}
                icon={customIcon}
              >
                <Popup>
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
