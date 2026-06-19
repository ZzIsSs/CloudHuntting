const BASE_URL = 'http://127.0.0.1:8000';

/**
 * Hàm băm (hash) một chuỗi thành một số nguyên dương (để dùng làm tour_id)
 * Băm dựa trên thuật toán DJB2 đơn giản
 * @param {string} str 
 * @returns {number} ID số nguyên
 */
export function generateTourId(str) {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i); /* hash * 33 + c */
  }
  return Math.abs(hash);
}

/**
 * Lấy danh sách đánh giá của một địa điểm
 * @param {number} tour_id - ID số nguyên của địa điểm
 * @returns {Promise<Array>} Danh sách reviews
 */
export async function fetchReviews(tour_id) {
  const response = await fetch(`${BASE_URL}/content/reviews/location/${tour_id}`);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Không thể lấy đánh giá');
  }

  return response.json();
}

/**
 * Gửi một đánh giá mới
 * @param {number} tour_id - ID số nguyên của địa điểm
 * @param {number} rating - Số sao (1-5)
 * @param {string} comment - Nội dung đánh giá
 * @param {string} location_name - Tên địa điểm thật
 * @returns {Promise<Object>} Đánh giá vừa tạo
 */
export async function postReview(tour_id, rating, comment, location_name) {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json'
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}/content/reviews`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      location_id: tour_id,
      location_name: location_name,
      rating,
      comment
    })
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Không thể gửi đánh giá');
  }

  return response.json();
}

/**
 * Chỉnh sửa một đánh giá đã có
 * @param {number} review_id - ID của đánh giá
 * @param {number} rating - Số sao mới (1-5)
 * @param {string} comment - Nội dung mới
 * @returns {Promise<Object>} Đánh giá sau khi cập nhật
 */
export async function editReview(review_id, rating, comment) {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json'
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}/content/reviews/${review_id}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify({
      rating,
      comment
    })
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Không thể cập nhật đánh giá');
  }

  return response.json();
}

export async function likeReview(review_id) {
  const response = await fetch(`${BASE_URL}/content/reviews/${review_id}/helpful`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to like review');
  return response.json();
}

export async function unlikeReview(review_id) {
  const response = await fetch(`${BASE_URL}/content/reviews/${review_id}/unhelpful`, { method: 'POST' });
  if (!response.ok) throw new Error('Failed to unlike review');
  return response.json();
}

export async function fetchMyReviews() {
  const token = localStorage.getItem('accessToken');
  if (!token) return [];
  const response = await fetch(`${BASE_URL}/content/reviews/user/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!response.ok) throw new Error('Failed to fetch user reviews');
  return response.json();
}
