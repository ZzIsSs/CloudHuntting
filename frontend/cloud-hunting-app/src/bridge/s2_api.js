const BASE_URL = 'http://127.0.0.1:8000';

export async function fetchCategories() {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json'
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}/api/v1/places/categories`, {
    method: 'GET',
    headers
  });

  if (!response.ok) {
    throw new Error('Không thể tải danh sách loại địa điểm');
  }

  return response.json();
}

export async function fetchNearbyUtilities(lat, lon, category = null, amenities = [], radiusKm = 15, perPage = 50) {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json'
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let url = `${BASE_URL}/api/v1/places/nearby?lat=${lat}&lon=${lon}&radius_km=${radiusKm}&per_page=${perPage}`;

  if (category && category !== 'all') {
    url += `&category=${encodeURIComponent(category)}`;
  }

  if (amenities && amenities.length > 0) {
    amenities.forEach(am => {
      url += `&amenities=${encodeURIComponent(am)}`;
    });
  }

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
