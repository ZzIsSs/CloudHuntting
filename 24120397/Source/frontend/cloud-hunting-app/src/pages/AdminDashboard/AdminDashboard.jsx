import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './AdminDashboard.module.css';
import { fetchReviews, deleteReview, generateTourId, fetchTickets, updateTicketStatus } from '../../bridge/s4_api';
import { getCurrentUser } from '../../utils/authUtils';

const LOCATIONS = [
  'Đồi chè Cầu Đất',
  'Đồi Đa Phú',
  'Đồi Du Sinh',
  'Đồi Thiên Phúc Đức',
  'Trại Mát',
  'Đỉnh Hòn Bồ',
  'Đỉnh Pinhatt',
  'Đỉnh Langbiang',
  'Đồi Robin',
  'Đỉnh Rada',
  'Đồi Trọc (Đồi Cô Dâu)',
  'Cây Thông Cô Đơn',
  'Thung lũng Đạ Sar',
  'Đồi Hòn Móng Ngựa',
  'Đỉnh đèo Klong Klanh',
  'Núi Đại Bình',
  'Đồi Cỏ Lau Lạc Dương',
  'Thôn Tu Poh',
  'Đỉnh Bidoup',
  'Đỉnh Samson',
  'Đỉnh Tà Năng',
  'Núi Voi (Đỉnh Rowas)',
  'Samten Hills Dalat',
  'Thảm Gỗ Săn Mây',
  'Đồi Vô Ảnh',
  'Hồ Tuyền Lâm'
];

// Khong dung MOCK_TICKETS nua, fetch tu API

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('reviews'); // 'reviews' | 'tickets'
  
  // Tickets state
  const [tickets, setTickets] = useState([]);
  const [loadingTickets, setLoadingTickets] = useState(false);
  const [expandedTicketId, setExpandedTicketId] = useState(null);
  
  // Reviews state
  const [selectedLocation, setSelectedLocation] = useState(LOCATIONS[0]);
  const [reviews, setReviews] = useState([]);
  const [loadingReviews, setLoadingReviews] = useState(false);
  
  const adminUser = getCurrentUser();

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    window.location.href = '/';
  };

  const loadReviews = useCallback(async () => {
    try {
      setLoadingReviews(true);
      const tourId = generateTourId(selectedLocation.toLowerCase());
      const data = await fetchReviews(tourId);
      
      if (Array.isArray(data)) {
        setReviews(data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
      } else {
        setReviews([]);
      }
    } catch (err) {
      console.error('Failed to load reviews:', err);
      setReviews([]);
    } finally {
      setLoadingReviews(false);
    }
  }, [selectedLocation]);

  useEffect(() => {
    if (activeTab === 'reviews') {
      loadReviews();
    } else if (activeTab === 'tickets') {
      loadTickets();
    }
  }, [activeTab, loadReviews]); // Note: we define loadTickets below but let's define it before useEffect

  const loadTickets = useCallback(async () => {
    try {
      setLoadingTickets(true);
      const data = await fetchTickets();
      if (Array.isArray(data)) {
        setTickets(data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
      }
    } catch (err) {
      console.error('Failed to load tickets:', err);
      setTickets([]);
    } finally {
      setLoadingTickets(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'tickets') {
      loadTickets();
    }
  }, [activeTab, loadTickets]);

  const handleDeleteReview = async (reviewId) => {
    if (!window.confirm('Bạn có chắc muốn xóa đánh giá này không?')) return;
    try {
      await deleteReview(reviewId);
      loadReviews();
    } catch (error) {
      alert('Lỗi khi xóa: ' + error.message);
    }
  };

  const handleUpdateTicketStatus = async (ticketId, newStatus) => {
    try {
      await updateTicketStatus(ticketId, newStatus);
      loadTickets();
    } catch (error) {
      alert('Lỗi khi cập nhật trạng thái: ' + error.message);
    }
  };

  return (
    <div className={styles.adminWrapper}>
      {/* Sidebar */}
      <div className={styles.sidebar}>
        <div className={styles.brand}>
          <span className={styles.icon}>☁️</span>
          <h2>CloudHunting</h2>
          <span className={styles.badge}>ADMIN</span>
        </div>
        
        <div className={styles.userInfo}>
          <div className={styles.avatar}>A</div>
          <div className={styles.userDetails}>
            <span className={styles.userName}>{adminUser?.username || 'Admin'}</span>
            <span className={styles.userRole}>Quản trị viên hệ thống</span>
          </div>
        </div>

        <nav className={styles.navMenu}>
          <button 
            className={`${styles.navItem} ${activeTab === 'reviews' ? styles.active : ''}`}
            onClick={() => setActiveTab('reviews')}
          >
            ⭐ Quản lý Đánh giá
          </button>
          <button 
            className={`${styles.navItem} ${activeTab === 'tickets' ? styles.active : ''}`}
            onClick={() => setActiveTab('tickets')}
          >
            📨 Phản hồi Người dùng
          </button>
        </nav>

        <button className={styles.logoutBtn} onClick={handleLogout}>
          🚪 Đăng xuất
        </button>
      </div>

      {/* Main Content */}
      <div className={styles.mainContent}>
        {activeTab === 'reviews' && (
          <div className={styles.tabContent}>
            <div className={styles.contentHeader}>
              <h1>Quản lý Đánh giá (Reviews)</h1>
              <p>Quản lý các bài đánh giá của người dùng tại các địa điểm săn mây.</p>
            </div>
            
            <div className={styles.filterSection}>
              <label>Chọn địa điểm để xem đánh giá:</label>
              <select 
                value={selectedLocation} 
                onChange={(e) => setSelectedLocation(e.target.value)}
                className={styles.locationSelect}
              >
                {LOCATIONS.map(loc => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
            </div>

            <div className={styles.tableContainer}>
              {loadingReviews ? (
                <div className={styles.loading}>Đang tải dữ liệu...</div>
              ) : reviews.length === 0 ? (
                <div className={styles.emptyState}>Không có đánh giá nào cho địa điểm này.</div>
              ) : (
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Người dùng</th>
                      <th>Đánh giá</th>
                      <th>Nội dung</th>
                      <th>Ngày gửi</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reviews.map(review => (
                      <tr key={review.id}>
                        <td>{review.id}</td>
                        <td className={styles.cellUser}>
                          <strong>{review.display_name}</strong>
                          <br/><small>@{review.username}</small>
                        </td>
                        <td>{'⭐'.repeat(review.rating)}</td>
                        <td className={styles.cellComment}>{review.comment}</td>
                        <td>{new Date(review.created_at).toLocaleString('vi-VN')}</td>
                        <td>
                          <button 
                            className={styles.deleteBtn}
                            onClick={() => handleDeleteReview(review.id)}
                            title="Xóa đánh giá này"
                          >
                            Xóa 🗑️
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}

        {activeTab === 'tickets' && (
          <div className={styles.tabContent}>
            <div className={styles.contentHeader}>
              <h1>Phản hồi từ Người dùng</h1>
              <p>Báo cáo lỗi, góp ý và các vấn đề từ người dùng.</p>
            </div>
            
            <div className={styles.tableContainer}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Mã Ticket</th>
                    <th>Người dùng</th>
                    <th>Tiêu đề</th>
                    <th>Ngày gửi</th>
                    <th>Trạng thái</th>
                    <th>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {loadingTickets ? (
                    <tr><td colSpan="6" style={{textAlign: 'center'}}>Đang tải tickets...</td></tr>
                  ) : tickets.length === 0 ? (
                    <tr><td colSpan="6" style={{textAlign: 'center'}}>Không có ticket nào.</td></tr>
                  ) : tickets.map(ticket => (
                    <React.Fragment key={ticket.id}>
                      <tr>
                        <td>TCK-{ticket.id}</td>
                        <td>User {ticket.user_id}</td>
                        <td>{ticket.title}</td>
                        <td>{new Date(ticket.created_at).toLocaleString('vi-VN')}</td>
                        <td>
                          <span className={`${styles.statusBadge} ${
                            ticket.status === 'in_progress' ? styles.statusWarning : 
                            ticket.status === 'resolved' ? styles.statusSuccess : styles.statusDefault
                          }`}>
                            {ticket.status}
                          </span>
                        </td>
                        <td>
                          <button 
                            className={styles.viewBtn} 
                            onClick={() => setExpandedTicketId(expandedTicketId === ticket.id ? null : ticket.id)}
                          >
                            {expandedTicketId === ticket.id ? 'Đóng lại' : 'Xem chi tiết'}
                          </button>
                        </td>
                      </tr>
                      {expandedTicketId === ticket.id && (
                        <tr>
                          <td colSpan="6" style={{backgroundColor: '#f8fafc', padding: '16px'}}>
                            <div style={{marginBottom: '12px'}}>
                              <strong>Mô tả chi tiết:</strong>
                              <pre style={{whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: '8px 0', color: '#475569'}}>{ticket.description}</pre>
                            </div>
                            {ticket.status !== 'resolved' && (
                              <button 
                                onClick={() => handleUpdateTicketStatus(ticket.id, 'resolved')}
                                style={{
                                  backgroundColor: '#10b981', color: 'white', padding: '6px 12px',
                                  border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 600
                                }}
                              >
                                ✓ Đánh dấu Đã xử lý
                              </button>
                            )}
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
