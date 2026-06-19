import { useState } from 'react';
import cardStyles from '../CenterCard/CenterCard.module.css';
import { login } from '../../bridge/s3_api';

export default function LoginForm({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!username || !password) {
      setError('Vui lòng nhập đầy đủ thông tin');
      return;
    }

    try {
      setIsLoading(true);
      await login(username, password);
      if (onLogin) onLogin();
    } catch (err) {
      setError(err.message || 'Đăng nhập thất bại');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form className={cardStyles.formView} onSubmit={handleSubmit}>
      {error && <div style={{ color: 'red', marginBottom: '10px', fontSize: '0.9rem' }}>{error}</div>}
      <div className={cardStyles.inputGroup}>
        <label>Tên đăng nhập</label>
        <input 
          type="text" 
          autoComplete="off" 
          placeholder="Nhập tên đăng nhập" 
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <div className={cardStyles.inputGroup}>
        <label>Mật khẩu</label>
        <input 
          type="password" 
          placeholder="Nhập mật khẩu" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <button type="submit" className={cardStyles.submitAction} disabled={isLoading}>
        {isLoading ? 'Đang đăng nhập...' : 'Đăng nhập'}
      </button>
    </form>
  );
}
