import { useState, useCallback } from 'react';
import CloudGameLayer from '../../components/CloudGameLayer/CloudGameLayer';
import CenterCard from '../../components/CenterCard/CenterCard';
import TopRightNav from '../../components/TopRightNav/TopRightNav';
import useScore from '../../hooks/useScore';
import styles from './AuthPage.module.css';

export default function AuthPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(() => !!localStorage.getItem('accessToken'));
  const { resetScore } = useScore();

  const handleLogin = useCallback(() => {
    setIsLoggedIn(true);
  }, []);

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
