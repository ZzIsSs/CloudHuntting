import { useNavigate, useLocation } from 'react-router-dom';
import CloudGameLayer from '../../components/CloudGameLayer/CloudGameLayer';
import StatsChart from '../../components/StatsChart/StatsChart';
import TopRightNav from '../../components/TopRightNav/TopRightNav';
import styles from './DetailPage.module.css';

export default function DetailPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const cloudData = location.state?.cloudData;
  const timeOffset = location.state?.timeOffset;

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
      <StatsChart data={validSpots} timeOffset={timeOffset} />
    </div>
  );
}
