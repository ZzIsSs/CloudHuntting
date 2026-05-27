/**
 * CloudHunting API Module
 * Giao tiep voi Gateway (port 8000) de goi cac microservices.
 */

const API_BASE = window.location.origin; // http://127.0.0.1:8000

// ─── Token Management ───────────────────────────────────────

function getToken() {
    return localStorage.getItem('ch_token');
}

function setToken(token) {
    localStorage.setItem('ch_token', token);
}

function removeToken() {
    localStorage.removeItem('ch_token');
    localStorage.removeItem('ch_username');
}

function setUsername(name) {
    localStorage.setItem('ch_username', name);
}

function getUsername() {
    return localStorage.getItem('ch_username') || 'Guest';
}

function isLoggedIn() {
    return !!getToken();
}

// ─── HTTP Helper ────────────────────────────────────────────

async function apiRequest(method, path, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = { method, headers };
    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${path}`, options);
    const data = await response.json();

    if (!response.ok) {
        const errorMsg = data.detail || data.message || `Loi ${response.status}`;
        throw new Error(errorMsg);
    }

    return data;
}

// ─── S3 Auth API ────────────────────────────────────────────

async function apiLogin(username, password) {
    // S3 su dung OAuth2PasswordRequestForm (form-data, khong phai JSON)
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Dang nhap that bai');
    }

    // Luu token va username
    setToken(data.access_token);
    setUsername(username);
    return data;
}

async function apiRegister(username, email, password) {
    return await apiRequest('POST', '/auth/register', {
        username, email, password
    });
}

// ─── S1 Metrics API ────────────────────────────────────────

async function apiPredict(locationName, radiusKm) {
    return await apiRequest('POST', '/api/s1/predict', {
        location_name: locationName,
        radius_km: radiusKm
    });
}

// ─── S5 Statistics API ──────────────────────────────────────

async function apiGetStatistics(locationName, days = 7) {
    const params = new URLSearchParams({
        location_name: locationName,
        days: days
    });
    return await apiRequest('GET', `/api/s5/statistics?${params}`);
}

// ─── Logout ─────────────────────────────────────────────────

function logout() {
    removeToken();
    window.location.href = '/app/login.html';
}

// ─── Auth Guard ─────────────────────────────────────────────

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = '/app/login.html';
        return false;
    }
    return true;
}
