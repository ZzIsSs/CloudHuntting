import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import CloudGameLayer from '../../components/CloudGameLayer/CloudGameLayer';
import Carousel from '../../components/Carousel/Carousel';
import BottomNav from '../../components/BottomNav/BottomNav';
import TopRightNav from '../../components/TopRightNav/TopRightNav';
import AmenitiesModal from '../../components/AiSchedule/AmenitiesModal';
import styles from './CarouselPage.module.css';

export default function CarouselPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const cloudData = location.state?.cloudData;
  const [showAiScheduleModal, setShowAiScheduleModal] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/');
  };

  const validSpots = cloudData?.top_spots?.filter(spot => spot.probability > 0);
  const noSpotsAvailable = cloudData && validSpots.length === 0;

  return (
    <div className={styles.container}>
      <CloudGameLayer />
      <TopRightNav onLogout={handleLogout} />
      
      {/* Truyền dữ liệu đã lọc vào Carousel hoặc hiển thị thông báo rỗng */}
      {noSpotsAvailable ? (
        <div style={{ 
          position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', 
          zIndex: 10, width: '85%', maxWidth: '450px',
          background: 'rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.6)',
          borderRadius: '24px',
          padding: '35px 25px',
          textAlign: 'center', color: '#1e293b', 
          boxShadow: '0 15px 35px rgba(0, 0, 0, 0.2), inset 0 0 0 1px rgba(255, 255, 255, 0.5)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '15px' 
        }}>
          <div style={{ fontSize: '3.5rem', margin: '-10px 0 5px 0', filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.15))' }}>🌧️🥺</div>
          <h2 style={{ margin: 0, fontSize: '1.6rem', lineHeight: '1.4', fontWeight: '900', letterSpacing: '-0.5px', color: '#0f172a' }}>
            Rất tiếc! Hôm nay không có biển mây nào
          </h2>
          <p style={{ margin: '5px 0 15px 0', fontSize: '1.05rem', color: '#334155', lineHeight: '1.5', fontWeight: '600' }}>
            Thời tiết hiện tại sương mù dày đặc hoặc có mưa, đi đường đèo sẽ rất nguy hiểm. Đừng buồn nhé, an toàn là trên hết!
          </p>
          <button 
            onClick={() => setShowAiScheduleModal(true)}
            style={{ 
              padding: '14px 28px', 
              background: 'linear-gradient(135deg, #f59e0b, #ea580c)', 
              color: 'white', border: 'none', borderRadius: '30px', 
              fontWeight: 'bold', fontSize: '1.1rem', cursor: 'pointer', 
              boxShadow: '0 8px 20px rgba(234, 88, 12, 0.4)', 
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)', 
              display: 'flex', alignItems: 'center', gap: '10px' 
            }}
            onMouseOver={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 12px 25px rgba(234, 88, 12, 0.5)'; }}
            onMouseOut={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(234, 88, 12, 0.4)'; }}
          >
            <span>🎯</span> Khám phá địa điểm thay thế
          </button>
        </div>
      ) : (
        <Carousel data={validSpots} />
      )}
      
      {/* Hiển thị tóm tắt về tâm dò */}
      {cloudData && (
        <div style={{ position: 'absolute', top: '10%', width: '100%', textAlign: 'center', color: '#fff', textShadow: '1px 1px 2px rgba(0,0,0,0.5)', zIndex: 10 }}>
          <h3>Kết quả xung quanh: {cloudData.center_location}</h3>
        </div>
      )}

      <BottomNav />

      {/* Tích hợp S6 Modal */}
      {showAiScheduleModal && (
        <AmenitiesModal 
          onClose={() => setShowAiScheduleModal(false)} 
          locName={cloudData?.center_location || "Vị trí của bạn"}
        />
      )}
    </div>
  );
}
