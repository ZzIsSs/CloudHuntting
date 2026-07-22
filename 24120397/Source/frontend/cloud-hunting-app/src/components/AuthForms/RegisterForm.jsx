import { useState } from 'react';
import cardStyles from '../CenterCard/CenterCard.module.css';
import { register } from '../../bridge/s3_api';

export default function RegisterForm() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!email || !username || !password || !displayName) {
      setError('Vui lòng nhập đầy đủ thông tin');
      return;
    }

    try {
      setIsLoading(true);
      await register(email, username, password, displayName);
      setSuccess('Đăng ký thành công! Vui lòng đăng nhập.');
      // Reset form
      setEmail('');
      setUsername('');
      setDisplayName('');
      setPassword('');
    } catch (err) {
      setError(err.message || 'Đăng ký thất bại');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form className={cardStyles.formView} onSubmit={handleSubmit}>
      {error && <div style={{ color: 'red', marginBottom: '10px', fontSize: '0.9rem' }}>{error}</div>}
      {success && <div style={{ color: 'green', marginBottom: '10px', fontSize: '0.9rem' }}>{success}</div>}
      
      <div className={cardStyles.inputGroup}>
        <label>Email</label>
        <input 
          type="email" 
          autoComplete="off" 
          placeholder="Nhập email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <div className={cardStyles.inputGroup}>
        <label>Tên hiển thị</label>
        <input 
          type="text" 
          autoComplete="off" 
          placeholder="Tên hiển thị trên hồ sơ" 
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <div className={cardStyles.inputGroup}>
        <label>Tên đăng nhập</label>
        <input 
          type="text" 
          autoComplete="off" 
          placeholder="Tạo tên đăng nhập" 
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <div className={cardStyles.inputGroup}>
        <label>Mật khẩu</label>
        <input 
          type="password" 
          placeholder="Tạo mật khẩu" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <button type="submit" className={cardStyles.submitAction} disabled={isLoading}>
        {isLoading ? 'Đang đăng ký...' : 'Đăng ký'}
      </button>
    </form>
  );
}
