const BASE_URL = 'http://127.0.0.1:8000';

/**
 * Gọi API S1 để tìm kiếm các điểm săn mây
 * @param {string} location_name - Tên địa điểm trung tâm (vd: "Đà Lạt")
 * @param {number} radius_km - Bán kính tìm kiếm (mặc định 15)
 * @param {number} forecast_hours - Số giờ dự báo (mặc định 0)
 * @returns {Promise<Object>} Trả về danh sách điểm săn mây
 */
export async function predictCloud(location_name, radius_km = 15, forecast_hours = 0) {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json'
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}/api/s1/predict`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      location_name,
      radius_km,
      forecast_hours
    })
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Không thể lấy dữ liệu Săn Mây');
  }

  return response.json();
}
