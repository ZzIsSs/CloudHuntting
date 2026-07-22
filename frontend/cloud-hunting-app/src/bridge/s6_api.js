const BASE_URL = '';

/**
 * Gọi API S6 để lên lịch trình săn mây
 * @param {Object} preferences - Thông tin sở thích người dùng
 * {
 *   user_id: 1,
 *   time_available: "04:00 - 08:00",
 *   vehicle: "Xe máy",
 *   style: "Chill",
 *   current_location_lat: null,
 *   current_location_lon: null
 * }
 */
export async function recommendItinerary(preferences) {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json'
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}/api/s6/recommend`, {
    method: 'POST',
    headers,
    body: JSON.stringify(preferences)
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    let errMsg = 'Không thể lấy lịch trình gợi ý';
    if (errorData.detail) {
      errMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
    }
    throw new Error(errMsg);
  }

  return response.json();
}
