const BASE_URL = 'http://127.0.0.1:8000';

export async function fetchNearbyUtilities(lat, lon) {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json'
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${BASE_URL}/api/v1/places/nearby?lat=${lat}&lon=${lon}&radius_km=10`;

  const response = await fetch(url, {
    method: 'GET',
    headers
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Không thể lấy dữ liệu tiện ích');
  }

  return response.json();
}
