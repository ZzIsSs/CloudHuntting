import { useNavigate } from 'react-router-dom';
import CloudGameLayer from '../../components/CloudGameLayer/CloudGameLayer';
import ReviewCard from '../../components/ReviewCard/ReviewCard';
import TopRightNav from '../../components/TopRightNav/TopRightNav';
import styles from './RankingPage.module.css';

export default function RankingPage() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('cloudHuntingScore');
    navigate('/');
  };

  return (
    <div className={styles.container}>
      <CloudGameLayer spawnRate="slow" />
      <TopRightNav onLogout={handleLogout} />
      <ReviewCard />
    </div>
  );
}
