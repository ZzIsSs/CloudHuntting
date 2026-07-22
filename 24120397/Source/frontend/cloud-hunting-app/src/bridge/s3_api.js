const BASE_URL = 'http://127.0.0.1:8000';

/**
 * Đăng nhập người dùng
 * @param {string} username 
 * @param {string} password 
 * @returns {Promise<Object>} { token, token_type }
 */
export async function login(username, password) {
  // FastAPI OAuth2PasswordRequestForm yêu cầu form-data
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString()
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Đăng nhập thất bại');
  }

  const data = await response.json();
  // Lưu token vào localStorage
  if (data.access_token) {
    localStorage.setItem('accessToken', data.access_token);
  }
  return data;
}

/**
 * Đăng ký người dùng mới
 * @param {string} email 
 * @param {string} username 
 * @param {string} displayName 
 * @returns {Promise<Object>} User data
 */
export async function register(email, username, password, displayName) {
  const response = await fetch(`${BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      username,
      password,
      display_name: displayName
    })
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Đăng ký thất bại');
  }

  return response.json();
}

/**
 * Lấy token hiện tại
 */
export function getToken() {
  return localStorage.getItem('accessToken');
}

/**
 * Đăng xuất
 */
export function logout() {
  localStorage.removeItem('accessToken');
}
