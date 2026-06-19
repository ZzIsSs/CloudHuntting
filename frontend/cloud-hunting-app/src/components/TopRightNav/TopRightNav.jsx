import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './TopRightNav.module.css';

export default function TopRightNav({ onLogout }) {
  const [displayName, setDisplayName] = useState('Khách');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      try {
        let base64Url = token.split('.')[1];
        let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const padLength = (4 - (base64.length % 4)) % 4;
        base64 += '='.repeat(padLength);
        
        const jsonPayload = decodeURIComponent(
          atob(base64)
            .split('')
            .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
            .join('')
        );
        
        const payload = JSON.parse(jsonPayload);
        if (payload.display_name) {
          setDisplayName(payload.display_name);
        } else if (payload.username) {
          setDisplayName(payload.username);
        }
      } catch (e) {
        console.error('Failed to parse JWT in TopRightNav', e);
      }
    }
  }, []);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownRef]);

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  return (
    <div className={styles.userProfile} ref={dropdownRef} onClick={toggleDropdown}>
      <div className={styles.greeting}>Chào, {displayName} <span>▼</span></div>
      <div className={`${styles.profileDropdown} ${isDropdownOpen ? styles.open : ''}`}>
          <div className={styles.dropdownItem} onClick={() => navigate('/profile')}>Thông tin tài khoản</div>
          <div className={styles.dropdownItem} onClick={() => navigate('/support')}>Hỗ trợ (Tickets)</div>
          <div className={`${styles.dropdownItem} ${styles.textDanger}`} onClick={onLogout}>Đăng xuất</div>
      </div>
    </div>
  );
}
