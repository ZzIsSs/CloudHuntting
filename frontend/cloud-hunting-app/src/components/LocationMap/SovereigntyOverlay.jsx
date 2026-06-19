import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

/**
 * Lớp phủ chủ quyền biển đảo Việt Nam
 * Hiển thị tên: Biển Đông, Quần đảo Hoàng Sa, Quần đảo Trường Sa
 * Sử dụng custom pane để luôn nằm trên các layer khác
 */

const sovereigntyLabels = [
  {
    name: 'BIỂN ĐÔNG',
    subtitle: 'East Sea',
    position: [15.5, 114.0],
    fontSize: 22,
    color: '#0047AB',
    minZoom: 4,
    maxZoom: 18,
  },
  {
    name: 'Quần đảo Hoàng Sa',
    subtitle: 'Paracel Islands',
    position: [16.5, 112.0],
    fontSize: 14,
    color: '#B22222',
    minZoom: 5,
    maxZoom: 18,
  },
  {
    name: 'Quần đảo Trường Sa',
    subtitle: 'Spratly Islands',
    position: [10.0, 114.5],
    fontSize: 14,
    color: '#B22222',
    minZoom: 5,
    maxZoom: 18,
  },
];

function createLabelIcon(label) {
  return L.divIcon({
    className: 'sovereignty-label',
    html: `
      <div style="
        text-align: center;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        white-space: nowrap;
        user-select: none;
      ">
        <div style="
          font-size: ${label.fontSize}px;
          font-weight: 800;
          color: ${label.color};
          text-shadow:
            -1px -1px 0 #fff,
             1px -1px 0 #fff,
            -1px  1px 0 #fff,
             1px  1px 0 #fff,
             0 0 8px rgba(255,255,255,0.95);
          letter-spacing: 3px;
        ">
          ${label.name}
        </div>
        <div style="
          font-size: 10px;
          font-weight: 600;
          color: ${label.color};
          opacity: 0.65;
          text-shadow: 0 0 3px white;
          margin-top: 2px;
          font-style: italic;
        ">
          ${label.subtitle}
        </div>
      </div>
    `,
    iconSize: [280, 55],
    iconAnchor: [140, 27],
  });
}

export default function SovereigntyOverlay() {
  const map = useMap();

  useEffect(() => {
    // Tạo custom pane để label nằm trên tất cả layer khác
    if (!map.getPane('sovereigntyPane')) {
      map.createPane('sovereigntyPane');
      map.getPane('sovereigntyPane').style.zIndex = 650;
      map.getPane('sovereigntyPane').style.pointerEvents = 'none';
    }

    const markers = [];

    sovereigntyLabels.forEach((label) => {
      const icon = createLabelIcon(label);

      const marker = L.marker(label.position, {
        icon: icon,
        pane: 'sovereigntyPane',
        interactive: false,
      });

      markers.push({ marker, label });
    });

    // Hiển thị / ẩn label theo zoom level
    function updateVisibility() {
      const zoom = map.getZoom();
      markers.forEach(({ marker, label }) => {
        if (zoom >= label.minZoom && zoom <= label.maxZoom) {
          if (!map.hasLayer(marker)) marker.addTo(map);
        } else {
          if (map.hasLayer(marker)) map.removeLayer(marker);
        }
      });
    }

    updateVisibility();
    map.on('zoomend', updateVisibility);

    // Cleanup khi component unmount
    return () => {
      map.off('zoomend', updateVisibility);
      markers.forEach(({ marker }) => {
        if (map.hasLayer(marker)) map.removeLayer(marker);
      });
    };
  }, [map]);

  return null;
}
