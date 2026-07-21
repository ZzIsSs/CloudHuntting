/**
 * Giải mã chuỗi JWT Base64
 * @param {string} token 
 * @returns {Object|null} Payload của token
 */
export function decodeJWT(token) {
  if (!token) return null;
  
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
    
    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error('Invalid token', e);
    return null;
  }
}

/**
 * Lấy thông tin user hiện tại từ localStorage
 * @returns {Object|null} { id, role, username, display_name, email }
 */
export function getCurrentUser() {
  const token = localStorage.getItem('accessToken');
  const payload = decodeJWT(token);
  
  if (!payload) return null;
  
  return {
    id: parseInt(payload.sub, 10) || null,
    role: payload.role || 'user',
    username: payload.username || '',
    displayName: payload.display_name || '',
    email: payload.email || ''
  };
}

/**
 * Kiểm tra xem user hiện tại có phải là admin không
 * @returns {boolean}
 */
export function isAdmin() {
  const user = getCurrentUser();
  return user ? user.role === 'admin' : false;
}
