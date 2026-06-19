import { useState } from 'react';
import styles from './CenterCard.module.css';
import LoginForm from '../AuthForms/LoginForm';
import RegisterForm from '../AuthForms/RegisterForm';
import SettingsForm from '../SettingsForm/SettingsForm';

export default function CenterCard({ isLoggedIn, onLogin, onLogout }) {
  const [activeTab, setActiveTab] = useState('login');

  return (
    <div className={styles.centerCard}>
      {!isLoggedIn ? (
        <>
          {/* Auth Tabs */}
          <div className={styles.authTabs}>
            <button
              className={`${styles.authTab} ${activeTab === 'login' ? styles.authTabActive : ''}`}
              onClick={() => setActiveTab('login')}
            >
              Đăng nhập
            </button>
            <button
              className={`${styles.authTab} ${activeTab === 'register' ? styles.authTabActive : ''}`}
              onClick={() => setActiveTab('register')}
            >
              Đăng ký
            </button>
          </div>

          {/* Forms */}
          {activeTab === 'login' ? (
            <LoginForm onLogin={onLogin} />
          ) : (
            <RegisterForm />
          )}
        </>
      ) : (
        <SettingsForm />
      )}
    </div>
  );
}
