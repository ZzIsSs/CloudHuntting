import { useState } from 'react';
import styles from './AiScheduleModal.module.css';

export default function AmenitiesModal({ onClose, locName }) {
  const locationName = locName || "Vị trí của bạn";
  const [expandedIndex, setExpandedIndex] = useState(null);

  // Dữ liệu thực tế cho các bạn đi săn mây sớm (4h - 6h sáng)
  const amenities = [
    { 
      type: 'Quán Cafe Xuyên Đêm / Mở Sớm', 
      icon: '☕', 
      desc: `Các quán cafe hoạt động 24/7 hoặc mở từ tờ mờ sáng để bạn trú rét và nhâm nhi đồ uống nóng.`, 
      color: '#0369a1', bg: '#f0f9ff', border: '#bae6fd',
      places: [
        'Route 66 Cafe (Mở 24/7 - 64 Thi Sách, Phường 6)',
        'The Beti Dalat (Mở 24/7 - 7A Lê Thị Hồng Gấm)',
        'Thức Coffee (Mở 24/7 - Ngã 3 Bà Triệu, Phường 1)',
        'Bohem Coffee (Mở từ 5:00 sáng - 1B Hoàng Hoa Thám)'
      ]
    },
    { 
      type: 'Quán Ăn Sáng Mở Cửa Sớm', 
      icon: '🍲', 
      desc: 'Điểm tâm sáng nóng hổi, xua tan cái lạnh giá của sương mù Đà Lạt rạng sáng.', 
      color: '#9d174d', bg: '#fdf4ff', border: '#fbcfe8',
      places: [
        'Sữa đậu nành Hoa Sữa (Tăng Bạt Hổ - Bán đến 3-4h sáng)',
        'Bánh mì xíu mại Hoàng Diệu (Mở từ 5:30 sáng)',
        'Phở Hiếu (Tăng Bạt Hổ - Mở từ 5:30 sáng)',
        'Bún bò ấp Ánh Sáng (Mở từ 5:30 sáng)'
      ]
    },
    { 
      type: 'Trải Nghiệm An Toàn Gần Trung Tâm', 
      icon: '🚶‍♂️', 
      desc: 'Thay vì đi đường đèo nguy hiểm, bạn có thể dạo quanh trung tâm thành phố lúc sáng tinh mơ.', 
      color: '#166534', bg: '#f0fdf4', border: '#bbf7d0',
      places: [
        'Dạo Hồ Xuân Hương ngắm sương mù mặt hồ',
        'Chợ Đà Lạt lúc rạng sáng (Nhịp sống chợ đầu mối 4-5h)',
        'Chụp ảnh tại Quảng trường Lâm Viên (Không kẹt xe)',
        'Ghé Ga Đà Lạt chụp ảnh check-in kiến trúc Pháp cổ'
      ]
    },
  ];

  const toggleExpand = (idx) => {
    if (expandedIndex === idx) {
      setExpandedIndex(null);
    } else {
      setExpandedIndex(idx);
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>🎯 Tiện Ích Gần Bạn</h2>
          <button className={styles.closeBtn} onClick={onClose}>×</button>
        </div>
        
        <div className={styles.modalBody}>
          <div className={styles.resultContainer} style={{ padding: '10px 0' }}>
            <p style={{ marginBottom: '20px', color: '#334155', fontSize: '1.05rem', lineHeight: '1.5' }}>
              Dưới đây là một số gợi ý tiện ích xung quanh khu vực <b>{locationName}</b> để bạn nghỉ ngơi và thư giãn.
            </p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {amenities.map((item, idx) => {
                const isExpanded = expandedIndex === idx;
                return (
                  <div 
                    key={idx} 
                    onClick={() => toggleExpand(idx)}
                    style={{ 
                      background: item.bg, 
                      padding: '15px', 
                      borderRadius: '10px', 
                      border: `1px solid ${item.border}`,
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <h4 style={{ margin: '0 0 8px 0', color: item.color, display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1.1rem' }}>
                        {item.icon} {item.type}
                      </h4>
                      <span style={{ color: item.color, fontWeight: 'bold', fontSize: '1.4rem', lineHeight: '1' }}>
                        {isExpanded ? '−' : '+'}
                      </span>
                    </div>
                    <p style={{ margin: 0, color: '#475569', fontSize: '0.95rem', lineHeight: '1.4' }}>
                      {item.desc}
                    </p>
                    
                    {isExpanded && (
                      <div style={{ 
                        marginTop: '15px', 
                        paddingTop: '15px', 
                        borderTop: `1px dashed ${item.border}` 
                      }}>
                        <ul style={{ margin: 0, paddingLeft: '20px', color: '#334155' }}>
                          {item.places.map((place, pIdx) => (
                            <li key={pIdx} style={{ marginBottom: '8px', fontSize: '0.95rem' }}>
                              📍 <b>{place}</b>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            <button 
                onClick={onClose} 
                style={{ marginTop: '25px', width: '100%', padding: '12px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #0284c7, #2563eb)', color: 'white', fontWeight: 'bold', cursor: 'pointer', fontSize: '1rem' }}
            >
              Đóng
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
