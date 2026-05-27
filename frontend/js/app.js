/**
 * CloudHunting App Logic
 * Xu ly render UI, su kien nguoi dung, va hieu ung dong.
 */

// ─── Toast Notification ─────────────────────────────────────

function showToast(message, type = 'error') {
    // Xoa toast cu neu co
    const old = document.querySelector('.toast');
    if (old) old.remove();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ─── Loading Overlay ────────────────────────────────────────

function showLoading(text = 'Dang xu ly...') {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="spinner"></div>
            <div class="loading-text">${text}</div>
        `;
        document.body.appendChild(overlay);
    }
    overlay.querySelector('.loading-text').textContent = text;
    overlay.classList.add('active');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
}

// ─── Login Page Logic ───────────────────────────────────────

function initLoginPage() {
    const loginTab = document.getElementById('tab-login');
    const registerTab = document.getElementById('tab-register');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    // Tab switching
    loginTab.addEventListener('click', () => {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    });

    registerTab.addEventListener('click', () => {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
    });

    // Login submit
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;

        if (!username || !password) {
            showToast('Vui long nhap day du thong tin');
            return;
        }

        showLoading('Dang dang nhap...');
        try {
            await apiLogin(username, password);
            showToast('Dang nhap thanh cong!', 'success');
            setTimeout(() => {
                window.location.href = '/app/index.html';
            }, 500);
        } catch (err) {
            hideLoading();
            showToast(err.message);
        }
    });

    // Register submit
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value.trim();
        const email = document.getElementById('reg-email').value.trim();
        const password = document.getElementById('reg-password').value;

        if (!username || !email || !password) {
            showToast('Vui long nhap day du thong tin');
            return;
        }

        showLoading('Dang dang ky...');
        try {
            await apiRegister(username, email, password);
            hideLoading();
            showToast('Dang ky thanh cong! Hay dang nhap.', 'success');
            loginTab.click();
        } catch (err) {
            hideLoading();
            showToast(err.message);
        }
    });
}

// ─── Main Page Logic (San May) ──────────────────────────────

function initMainPage() {
    if (!requireAuth()) return;

    // Hien thi username
    const usernameEl = document.getElementById('display-username');
    if (usernameEl) usernameEl.textContent = getUsername();

    // Logout
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) logoutBtn.addEventListener('click', logout);

    // Radius slider
    const slider = document.getElementById('radius-slider');
    const radiusDisplay = document.getElementById('radius-value');
    if (slider) {
        slider.addEventListener('input', () => {
            radiusDisplay.textContent = `${slider.value} km`;
        });
    }

    // Search form
    const searchForm = document.getElementById('search-form');
    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const location = document.getElementById('location-input').value.trim();
        const radius = parseFloat(slider.value);

        if (!location) {
            showToast('Vui long nhap ten dia diem');
            return;
        }

        showLoading('Dang quet cac diem san may...');
        try {
            const result = await apiPredict(location, radius);
            hideLoading();
            renderResults(result);
        } catch (err) {
            hideLoading();
            showToast(err.message);
            renderEmpty();
        }
    });
}

function renderResults(data) {
    const container = document.getElementById('results-container');
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';

    // Update header
    const countEl = document.getElementById('results-count');
    countEl.textContent = `${data.total_spots_found} dia diem`;

    if (data.top_spots.length === 0) {
        renderEmpty();
        return;
    }

    container.innerHTML = data.top_spots.map(spot => {
        const probClass = spot.probability >= 70 ? 'prob-high' :
                          spot.probability >= 40 ? 'prob-medium' : 'prob-low';
        const rankClass = `rank-${Math.min(spot.rank, 5)}`;

        return `
        <div class="spot-card" onclick="viewStats('${spot.location_name}')">
            <div class="spot-card-header">
                <div class="rank-badge ${rankClass}">${spot.rank}</div>
                <div class="spot-info">
                    <div class="spot-name">${spot.location_name}</div>
                    <div class="spot-distance">Cach ${spot.distance_km} km</div>
                </div>
                <div class="spot-probability">
                    <div class="probability-value ${probClass}">${spot.probability}%</div>
                    <div class="probability-label">xac suat</div>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${spot.probability}%"></div>
            </div>
            <div class="spot-suggestion">${spot.suggestion}</div>
            <div class="spot-actions">
                <a href="/app/stats.html?name=${encodeURIComponent(spot.location_name)}" 
                   class="btn-stats" onclick="event.stopPropagation()">
                    Xem thong ke
                </a>
            </div>
        </div>
        `;
    }).join('');
}

function renderEmpty() {
    const container = document.getElementById('results-container');
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';
    container.innerHTML = `
        <div class="empty-state">
            <div class="icon">&#9729;</div>
            <p>Khong tim thay dia diem san may nao trong ban kinh nay.<br>
            Thu tang ban kinh hoac nhap dia diem khac.</p>
        </div>
    `;
}

function viewStats(locationName) {
    window.location.href = `/app/stats.html?name=${encodeURIComponent(locationName)}`;
}

// ─── Stats Page Logic ───────────────────────────────────────

function initStatsPage() {
    if (!requireAuth()) return;

    const usernameEl = document.getElementById('display-username');
    if (usernameEl) usernameEl.textContent = getUsername();

    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) logoutBtn.addEventListener('click', logout);

    // Lay ten dia diem tu URL params
    const params = new URLSearchParams(window.location.search);
    const locationName = params.get('name');

    if (!locationName) {
        showToast('Thieu ten dia diem');
        return;
    }

    document.getElementById('stats-location-name').textContent = locationName;
    loadStatistics(locationName);
}

async function loadStatistics(locationName) {
    showLoading('Dang tai thong ke...');
    try {
        const data = await apiGetStatistics(locationName, 7);
        hideLoading();
        renderStatistics(data, locationName);
    } catch (err) {
        hideLoading();
        // Fallback: hien thi du lieu mac dinh neu S5 chua co data
        renderFallbackStats(locationName);
    }
}

function renderStatistics(data, locationName) {
    // Hien thi cac chi so
    const stats = data.statistics || data;

    const avgEl = document.getElementById('stat-avg');
    const maxEl = document.getElementById('stat-max');
    const minEl = document.getElementById('stat-min');
    const trendEl = document.getElementById('stat-trend');
    const currentEl = document.getElementById('stats-current-value');
    const trendBadge = document.getElementById('stats-trend-badge');

    if (avgEl) avgEl.textContent = `${(stats.avg_probability || 0).toFixed(1)}%`;
    if (maxEl) maxEl.textContent = `${(stats.max_probability || 0).toFixed(1)}%`;
    if (minEl) minEl.textContent = `${(stats.min_probability || 0).toFixed(1)}%`;

    const trend = stats.trend || 'Di ngang';
    if (trendEl) trendEl.textContent = trend;
    if (currentEl) currentEl.textContent = `${(stats.avg_probability || 0).toFixed(0)}%`;

    if (trendBadge) {
        const trendClass = trend === 'Tang' ? 'trend-up' :
                           trend === 'Giam' ? 'trend-down' : 'trend-stable';
        const trendIcon = trend === 'Tang' ? '&#9650;' :
                          trend === 'Giam' ? '&#9660;' : '&#9654;';
        trendBadge.className = `stats-trend ${trendClass}`;
        trendBadge.innerHTML = `${trendIcon} ${trend}`;
    }

    // Ve bieu do
    if (stats.daily_data && stats.daily_data.length > 0) {
        drawChart(stats.daily_data);
    }
}

function renderFallbackStats(locationName) {
    const currentEl = document.getElementById('stats-current-value');
    if (currentEl) currentEl.textContent = '--';

    const trendBadge = document.getElementById('stats-trend-badge');
    if (trendBadge) {
        trendBadge.className = 'stats-trend trend-stable';
        trendBadge.textContent = 'Chua co du lieu';
    }

    showToast('Chua co du lieu thong ke cho dia diem nay. Hay thu lai sau.');
}

// ─── Simple Chart (Canvas) ──────────────────────────────────

function drawChart(dailyData) {
    const canvas = document.getElementById('stats-chart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.parentElement.getBoundingClientRect();

    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.scale(dpr, dpr);

    const W = rect.width;
    const H = rect.height;
    const padding = { top: 20, right: 20, bottom: 40, left: 45 };
    const chartW = W - padding.left - padding.right;
    const chartH = H - padding.top - padding.bottom;

    const values = dailyData.map(d => d.avg_probability || 0);
    const labels = dailyData.map(d => {
        const date = new Date(d.date);
        return `${date.getDate()}/${date.getMonth() + 1}`;
    });

    const maxVal = Math.max(...values, 100);
    const minVal = 0;

    // Background
    ctx.clearRect(0, 0, W, H);

    // Grid lines
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = padding.top + (chartH / 4) * i;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(W - padding.right, y);
        ctx.stroke();

        // Y-axis labels
        const val = Math.round(maxVal - (maxVal / 4) * i);
        ctx.fillStyle = '#64748b';
        ctx.font = '11px Inter, sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(`${val}%`, padding.left - 8, y + 4);
    }

    // Data points
    const points = values.map((v, i) => ({
        x: padding.left + (chartW / (values.length - 1 || 1)) * i,
        y: padding.top + chartH - (v / maxVal) * chartH
    }));

    // Area fill
    const gradient = ctx.createLinearGradient(0, padding.top, 0, H - padding.bottom);
    gradient.addColorStop(0, 'rgba(139, 92, 246, 0.3)');
    gradient.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

    ctx.beginPath();
    ctx.moveTo(points[0].x, H - padding.bottom);
    points.forEach(p => ctx.lineTo(p.x, p.y));
    ctx.lineTo(points[points.length - 1].x, H - padding.bottom);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    // Line
    ctx.beginPath();
    ctx.strokeStyle = '#8b5cf6';
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    points.forEach((p, i) => {
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
    });
    ctx.stroke();

    // Dots
    points.forEach((p, i) => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#8b5cf6';
        ctx.fill();
        ctx.strokeStyle = '#0a0e1a';
        ctx.lineWidth = 2;
        ctx.stroke();
    });

    // X-axis labels
    ctx.fillStyle = '#64748b';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'center';
    labels.forEach((label, i) => {
        ctx.fillText(label, points[i].x, H - padding.bottom + 20);
    });
}
