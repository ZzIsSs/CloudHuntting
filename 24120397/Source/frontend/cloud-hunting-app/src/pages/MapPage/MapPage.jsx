import { useNavigate, useLocation } from 'react-router-dom';
import CloudGameLayer from '../../components/CloudGameLayer/CloudGameLayer';
import LocationMap from '../../components/LocationMap/LocationMap';
import TopRightNav from '../../components/TopRightNav/TopRightNav';
import styles from './MapPage.module.css';

export default function MapPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const cloudData = location.state?.cloudData;

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/');
  };

  // Lọc các điểm có xác suất > 0
  const validSpots = cloudData?.top_spots?.filter(spot => spot.probability > 0);

  return (
    <div className={styles.container}>
      <CloudGameLayer />
      <TopRightNav onLogout={handleLogout} />
      <LocationMap data={validSpots} />
    </div>
  );
}
