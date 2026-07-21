import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import CloudGameLayer from '../../components/CloudGameLayer/CloudGameLayer';
import CenterCard from '../../components/CenterCard/CenterCard';
import TopRightNav from '../../components/TopRightNav/TopRightNav';
import useScore from '../../hooks/useScore';
import styles from './AuthPage.module.css';
import { isAdmin } from '../../utils/authUtils';

export default function AuthPage() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(() => !!localStorage.getItem('accessToken'));
  const { resetScore } = useScore();

  const handleLogin = useCallback(() => {
    if (isAdmin()) {
      navigate('/admin');
    } else {
      setIsLoggedIn(true);
    }
  }, [navigate]);

  const handleLogout = useCallback(() => {
    localStorage.removeItem('accessToken');
    setIsLoggedIn(false);
    resetScore();
  }, [resetScore]);

  return (
    <div className={styles.container}>
      <CloudGameLayer />
      <CenterCard
        isLoggedIn={isLoggedIn}
        onLogin={handleLogin}
        onLogout={handleLogout}
      />
      {isLoggedIn && <TopRightNav onLogout={handleLogout} />}
    </div>
  );
}
