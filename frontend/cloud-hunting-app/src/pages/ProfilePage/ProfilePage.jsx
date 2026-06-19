import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import TopRightNav from '../../components/TopRightNav/TopRightNav';
import { fetchMyReviews } from '../../bridge/s4_api';
import styles from './ProfilePage.module.css';

export default function ProfilePage() {
  const navigate = useNavigate();
  const [displayName, setDisplayName] = useState('Người dùng');
  const [email, setEmail] = useState('Chưa cập nhật email');
  const [avatarInitial, setAvatarInitial] = useState('U');
  const [myReviews, setMyReviews] = useState([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const reviews = await fetchMyReviews();
        setMyReviews(reviews);
      } catch (err) {
        console.error('Lỗi tải đánh giá', err);
      }
    };
    loadData();
  }, []);

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
        const name = payload.display_name || payload.username || 'Người dùng';
        setDisplayName(name);
        setAvatarInitial(name.charAt(0).toUpperCase());
        
        if (payload.email) {
          setEmail(payload.email);
        }
      } catch (e) {
        console.error('Failed to parse JWT in ProfilePage', e);
      }
    }
  }, []);
  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/');
  };

  return (
    <div className={styles['profileContainer']} style={{
      background: 'linear-gradient(135deg, #38bdf8, #7dd3fc, #bae6fd)',
      backgroundSize: 'cover',
      height: '100vh',
      width: '100vw',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      overflow: 'hidden',
      position: 'relative'
    }}>
      {/* Background Animated Orbs */}
      <div className={`${styles.orb} ${styles['orb-1']}`}></div>
      <div className={`${styles.orb} ${styles['orb-2']}`}></div>
      <div className={`${styles.orb} ${styles['orb-3']}`}></div>

      <TopRightNav onLogout={handleLogout} />

      {/* Profile Wrapper */}
      <div className={styles['profile-wrapper']}>
        <div className={styles['profile-panel']}>
          
          {/* Left Side: User Info */}
          <div className={styles['profile-left']}>
            <button className={styles['back-btn']} onClick={() => navigate('/')}>← Quay lại</button>
            <div className={styles['avatar-container']}>{avatarInitial}</div>
            <div className={styles['profile-name']}>{displayName}</div>
            <div className={styles['profile-username']}>{email}</div>
            
            <div className={styles['profile-stats']}>
              <div className={styles['stat-item']}>
                <span className={styles['stat-value']}>{myReviews.length}</span>
                <span className={styles['stat-label']}>Bài đánh giá</span>
              </div>
            </div>

          </div>

          {/* Right Side: Posts List */}
          <div className={styles['profile-right']}>
            <div className={styles['right-header']}>
              <div className={styles['right-title']}>Các bài viết đã đăng</div>
            </div>

            <div className={styles['posts-list']}>
              {myReviews.length === 0 && (
                <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
                  Bạn chưa có bài đánh giá nào.
                </div>
              )}
              {myReviews.map(rv => (
                <div key={rv.id} className={styles['post-card']}>
                  <div className={styles['post-header']}>
                    <div className={styles['post-location']}>
                      📍 {rv.location_name || 'Đánh giá Săn Mây'}
                    </div>
                    <div className={styles['post-time']}>
                      {rv.created_at ? new Date(rv.created_at.endsWith('Z') ? rv.created_at : rv.created_at + 'Z').toLocaleString('vi-VN') : 'Vừa xong'}
                    </div>
                  </div>
                  <div className={styles['post-content']}>
                    {rv.comment}
                  </div>
                  <div className={styles['post-footer']}>
                    <div className={styles['post-stat']} style={{ color: '#f59e0b' }}>⭐ {rv.rating}/5</div>
                    <div className={`${styles['post-stat']} ${styles.likes}`}>❤️ {rv.helpful_count || 0}</div>
                    {/* <div className={styles['post-stat']}>💬 {rv.comments?.length || 0} Bình luận</div> */}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>


    </div>
  );
}
