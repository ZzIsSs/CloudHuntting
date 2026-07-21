import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CloudGameLayer from '../CloudGameLayer/CloudGameLayer';
import TopRightNav from '../TopRightNav/TopRightNav';
import styles from './SupportTickets.module.css';
import { postTicket } from '../../bridge/s4_api';

const ISSUE_CATEGORIES = [
  { id: 'bug', label: '🐛 Lỗi ứng dụng', desc: 'Ứng dụng bị crash, hiển thị sai, không hoạt động' },
  { id: 'data', label: '📊 Dữ liệu không chính xác', desc: 'Tỷ lệ mây sai, địa điểm không đúng, bản đồ lệch' },
  { id: 'account', label: '👤 Tài khoản & Đăng nhập', desc: 'Không đăng nhập được, mất tài khoản, quên mật khẩu' },
  { id: 'suggestion', label: '💡 Góp ý cải thiện', desc: 'Đề xuất tính năng mới hoặc cải thiện trải nghiệm' },
  { id: 'other', label: '📝 Khác', desc: 'Vấn đề không thuộc các mục trên' },
];

export default function SupportTickets() {
  const navigate = useNavigate();
  const [category, setCategory] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [sending, setSending] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    navigate('/');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!category || !title.trim() || !description.trim()) {
      alert('Vui lòng điền đầy đủ thông tin!');
      return;
    }
    if (title.trim().length < 5) {
      alert('Tiêu đề phải chứa ít nhất 5 ký tự!');
      return;
    }
    if (description.trim().length < 10) {
      alert('Mô tả phải chứa ít nhất 10 ký tự!');
      return;
    }

    setSending(true);
    try {
      const categoryLabel = ISSUE_CATEGORIES.find(c => c.id === category)?.label || category;
      const fullDesc = `[${categoryLabel}]\n${description.trim()}` + (email ? `\n\nEmail liên hệ: ${email}` : '');
      await postTicket(title.trim(), fullDesc);
      setSubmitted(true);
    } catch (err) {
      alert('Lỗi khi gửi báo cáo: ' + err.message);
    } finally {
      setSending(false);
    }
  };

  const handleReset = () => {
    setCategory('');
    setTitle('');
    setDescription('');
    setEmail('');
    setSubmitted(false);
  };

  return (
    <div className={styles.pageWrapper}>
      <CloudGameLayer />
      <TopRightNav onLogout={handleLogout} />

      <div className={styles.supportContainer}>
        {/* Header */}
        <div className={styles.header}>
          <button className={styles.backBtn} onClick={() => navigate(-1)}>
            ← Quay lại
          </button>
          <h1 className={styles.headerTitle}>📮 Báo Cáo Sự Cố</h1>
          <p className={styles.headerDesc}>Cho chúng tôi biết vấn đề bạn đang gặp phải để được hỗ trợ nhanh nhất</p>
        </div>

        {!submitted ? (
          <form className={styles.reportForm} onSubmit={handleSubmit}>
            {/* Category Selection */}
            <div className={styles.formSection}>
              <label className={styles.sectionLabel}>Loại sự cố</label>
              <div className={styles.categoryGrid}>
                {ISSUE_CATEGORIES.map(cat => (
                  <button
                    type="button"
                    key={cat.id}
                    className={`${styles.categoryCard} ${category === cat.id ? styles.categoryActive : ''}`}
                    onClick={() => setCategory(cat.id)}
                  >
                    <span className={styles.categoryLabel}>{cat.label}</span>
                    <span className={styles.categoryDesc}>{cat.desc}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Title */}
            <div className={styles.formSection}>
              <label className={styles.sectionLabel} htmlFor="report-title">Tiêu đề sự cố</label>
              <input
                id="report-title"
                type="text"
                className={styles.textInput}
                placeholder="VD: Không thể xem bản đồ sau khi quét địa điểm"
                value={title}
                onChange={e => setTitle(e.target.value)}
                maxLength={120}
              />
            </div>

            {/* Description */}
            <div className={styles.formSection}>
              <label className={styles.sectionLabel} htmlFor="report-desc">Mô tả chi tiết</label>
              <textarea
                id="report-desc"
                className={styles.textArea}
                placeholder="Hãy mô tả chi tiết vấn đề bạn gặp phải: bạn đang làm gì, lỗi xảy ra như thế nào, và bạn muốn điều gì xảy ra..."
                value={description}
                onChange={e => setDescription(e.target.value)}
                rows={5}
              />
            </div>

            {/* Email (optional) */}
            <div className={styles.formSection}>
              <label className={styles.sectionLabel} htmlFor="report-email">Email liên hệ <span className={styles.optional}>(không bắt buộc)</span></label>
              <input
                id="report-email"
                type="email"
                className={styles.textInput}
                placeholder="email@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
              />
            </div>

            {/* Submit */}
            <button type="submit" className={styles.submitBtn} disabled={sending}>
              {sending ? (
                <><span className={styles.spinner}></span> Đang gửi...</>
              ) : (
                '📨 Gửi báo cáo sự cố'
              )}
            </button>
          </form>
        ) : (
          <div className={styles.successBox}>
            <div className={styles.successIcon}>✅</div>
            <h2 className={styles.successTitle}>Đã gửi báo cáo thành công!</h2>
            <p className={styles.successDesc}>
              Cảm ơn bạn đã phản hồi. Đội ngũ hỗ trợ sẽ xem xét và phản hồi trong thời gian sớm nhất.
            </p>
            <div className={styles.successActions}>
              <button className={styles.submitBtn} onClick={handleReset}>📝 Gửi báo cáo khác</button>
              <button className={styles.secondaryBtn} onClick={() => navigate(-1)}>← Quay lại ứng dụng</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
