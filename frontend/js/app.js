/**
 * CloudHunting App Logic
 * Xu ly render UI, su kien nguoi dung, va hieu ung dong.
 */

// ─── Global State ───────────────────────────────────────────
let lastSearchData = null; // Luu ket qua tim kiem gan nhat (co timeline)
let timelineVisible = false;

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

    // Forecast slider
    const forecastSlider = document.getElementById('forecast-slider');
    const forecastDisplay = document.getElementById('forecast-value');
    if (forecastSlider) {
        forecastSlider.addEventListener('input', () => {
            const val = parseInt(forecastSlider.value);
            if (val === 0) forecastDisplay.textContent = 'Hien tai';
            else forecastDisplay.textContent = `+ ${val} gio`;
        });
    }

    // Search form
    const searchForm = document.getElementById('search-form');
    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const location = document.getElementById('location-input').value.trim();
        const radius = parseFloat(slider.value);
        const forecastHours = forecastSlider ? parseInt(forecastSlider.value) : 0;

        if (!location) {
            showToast('Vui long nhap ten dia diem');
            return;
        }

        const timeLabel = forecastHours === 0 ? 'hien tai' : `sau ${forecastHours} gio`;
        showLoading(`Dang quet cac diem san may (${timeLabel})...`);
        try {
            const result = await apiPredict(location, radius, forecastHours);
            hideLoading();
            renderResults(result, forecastHours);
        } catch (err) {
            hideLoading();
            showToast(err.message);
            renderEmpty();
        }
    });
}

function renderResults(data, forecastHours = 0) {
    // Luu data lai de ve bieu do khi bam nut Thong ke
    lastSearchData = data;
    timelineVisible = false;
    const timelinePanel = document.getElementById('timeline-panel');
    if (timelinePanel) timelinePanel.style.display = 'none';
    const toggleBtn = document.getElementById('btn-toggle-stats');
    if (toggleBtn) toggleBtn.classList.remove('active');

    const container = document.getElementById('results-container');
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';

    // Update header
    const countEl = document.getElementById('results-count');
    const timeText = forecastHours === 0 ? "Hien tai" : `+${forecastHours} gio`;
    countEl.innerHTML = `${data.total_spots_found} dia diem <span style="font-size: 0.85rem; color: #a8b2d1; margin-left: 10px;">(Du bao: ${timeText})</span>`;

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
                    <div class="spot-best-time" style="color: #fde047; font-size: 0.85rem; margin-top: 4px;">&#9200; Khung gio vang: <b>${spot.best_time}</b></div>
                </div>
                <div class="spot-probability">
                    <div class="probability-value ${probClass}">${spot.probability}%</div>
                    <div class="probability-label">MAX</div>
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
                <button class="btn-suggest" onclick="event.stopPropagation(); openNearbyModal('${spot.location_name}', ${spot.lat}, ${spot.lon})">
                    Tien ich
                </button>
            </div>
        </div>
        `;
    }).join('');

    // Render ban do
    renderMap(data);
}

// ─── Map Rendering (Leaflet) ────────────────────────────────

let cloudMap = null;

function renderMap(data) {
    const mapEl = document.getElementById('cloud-map');
    if (!mapEl || typeof L === 'undefined') return;

    // Xoa map cu neu co
    if (cloudMap) {
        cloudMap.remove();
        cloudMap = null;
    }

    // Khoi tao map
    cloudMap = L.map('cloud-map', {
        zoomControl: true,
        attributionControl: false
    });

    // Dark tile layer (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 18
    }).addTo(cloudMap);

    const bounds = [];

    // Marker trung tam (xanh duong, pulsing)
    const centerIcon = L.divIcon({
        className: '',
        html: '<div class="center-marker"></div>',
        iconSize: [18, 18],
        iconAnchor: [9, 9]
    });

    const centerLatLng = [data.center_lat, data.center_lon];
    bounds.push(centerLatLng);

    L.marker(centerLatLng, { icon: centerIcon })
        .addTo(cloudMap)
        .bindPopup(`
            <div class="map-popup-name">📍 ${data.center_location}</div>
            <div style="color: #94a3b8;">Vi tri trung tam khao sat</div>
        `);

    // Vong tron ban kinh
    L.circle(centerLatLng, {
        radius: data.radius_km * 1000,
        color: 'rgba(59, 130, 246, 0.5)',
        fillColor: 'rgba(59, 130, 246, 0.08)',
        fillOpacity: 1,
        weight: 1.5,
        dashArray: '6, 4'
    }).addTo(cloudMap);

    // Markers cho top spots
    data.top_spots.forEach((spot) => {
        const rank = spot.rank;
        const spotLatLng = [spot.lat, spot.lon];
        bounds.push(spotLatLng);

        const markerIcon = L.divIcon({
            className: '',
            html: `<div class="rank-marker rank-marker-${Math.min(rank, 5)}"><span>${rank}</span></div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -34]
        });

        const probClass = spot.probability >= 70 ? 'prob-high' :
                          spot.probability >= 40 ? 'prob-medium' : 'prob-low';

        L.marker(spotLatLng, { icon: markerIcon })
            .addTo(cloudMap)
            .bindPopup(`
                <div class="map-popup-name">#${rank} ${spot.location_name}</div>
                <div class="map-popup-prob ${probClass}">${spot.probability}%</div>
                <div style="color: #94a3b8;">Cach ${spot.distance_km} km · ${spot.best_time}</div>
            `);

        // Duong noi tu trung tam toi spot
        L.polyline([centerLatLng, spotLatLng], {
            color: 'rgba(139, 92, 246, 0.35)',
            weight: 1.5,
            dashArray: '4, 6'
        }).addTo(cloudMap);
    });

    // Auto fit bounds
    if (bounds.length > 1) {
        cloudMap.fitBounds(bounds, { padding: [30, 30] });
    } else {
        cloudMap.setView(centerLatLng, 12);
    }
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

// ─── Timeline Chart (Main Page) ─────────────────────────────

const TIMELINE_COLORS = [
    '#fde047', // Vang gold - Rank 1
    '#a78bfa', // Tim - Rank 2
    '#fb923c', // Cam - Rank 3
    '#22d3ee', // Cyan - Rank 4
    '#f472b6'  // Hong - Rank 5
];

function toggleTimeline() {
    const panel = document.getElementById('timeline-panel');
    const btn = document.getElementById('btn-toggle-stats');
    if (!panel || !lastSearchData) return;

    timelineVisible = !timelineVisible;

    if (timelineVisible) {
        panel.style.display = 'block';
        btn.classList.add('active');
        // Ve bieu do voi data da luu
        requestAnimationFrame(() => drawTimelineChart(lastSearchData.top_spots));
    } else {
        panel.style.display = 'none';
        btn.classList.remove('active');
    }
}

function drawTimelineChart(spots) {
    const canvas = document.getElementById('timeline-chart');
    if (!canvas || !spots || spots.length === 0) return;

    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const wrapper = canvas.parentElement;
    const rect = wrapper.getBoundingClientRect();

    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.scale(dpr, dpr);

    const W = rect.width;
    const H = rect.height;
    const padding = { top: 25, right: 20, bottom: 50, left: 50 };
    const chartW = W - padding.left - padding.right;
    const chartH = H - padding.top - padding.bottom;

    // Clear
    ctx.clearRect(0, 0, W, H);

    // Tim so gio max (lay tu spot co nhieu timeline nhat)
    let maxPoints = 0;
    let timeLabels = [];
    spots.forEach(spot => {
        console.log(`[Timeline] ${spot.location_name}: timeline =`, spot.timeline ? spot.timeline.length + ' points' : 'MISSING');
        if (spot.timeline && spot.timeline.length > maxPoints) {
            maxPoints = spot.timeline.length;
            timeLabels = spot.timeline.map(t => t.time);
        }
    });

    if (maxPoints === 0) {
        ctx.fillStyle = '#64748b';
        ctx.font = '14px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Dang tai du lieu bieu do...', W / 2, H / 2);
        ctx.font = '11px Inter, sans-serif';
        ctx.fillText('(Hay thu tim kiem lai)', W / 2, H / 2 + 22);
        return;
    }

    // Grid ngang (0%, 25%, 50%, 75%, 100%)
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = padding.top + (chartH / 4) * i;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(W - padding.right, y);
        ctx.stroke();

        const val = 100 - 25 * i;
        ctx.fillStyle = '#64748b';
        ctx.font = '11px Inter, sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(`${val}%`, padding.left - 8, y + 4);
    }

    // Ve tung duong cho moi dia diem
    spots.forEach((spot, spotIdx) => {
        if (!spot.timeline || spot.timeline.length === 0) return;

        const color = TIMELINE_COLORS[spotIdx % TIMELINE_COLORS.length];
        const values = spot.timeline.map(t => t.probability);
        const numPoints = values.length;

        const points = values.map((v, i) => ({
            x: padding.left + (chartW / Math.max(numPoints - 1, 1)) * i,
            y: padding.top + chartH - (v / 100) * chartH
        }));

        // Area fill (nhe)
        const gradient = ctx.createLinearGradient(0, padding.top, 0, H - padding.bottom);
        gradient.addColorStop(0, hexToRgba(color, 0.12));
        gradient.addColorStop(1, 'rgba(0,0,0,0)');

        // Ve area fill nhe cho rank 1
        if (spotIdx === 0) {
            ctx.beginPath();
            ctx.moveTo(points[0].x, H - padding.bottom);
            points.forEach(p => ctx.lineTo(p.x, p.y));
            ctx.lineTo(points[points.length - 1].x, H - padding.bottom);
            ctx.closePath();
            ctx.fillStyle = hexToRgba(color, 0.1);
            ctx.fill();
        }

        // Line
        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.lineWidth = spotIdx === 0 ? 3 : 2;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';

        // Ve duong cong smooth (bezier)
        points.forEach((p, i) => {
            if (i === 0) {
                ctx.moveTo(p.x, p.y);
            } else {
                const prev = points[i - 1];
                const cpx = (prev.x + p.x) / 2;
                ctx.quadraticCurveTo(prev.x + (cpx - prev.x) * 0.8, prev.y, cpx, (prev.y + p.y) / 2);
                ctx.quadraticCurveTo(p.x - (p.x - cpx) * 0.8, p.y, p.x, p.y);
            }
        });
        ctx.stroke();

        // Dots
        points.forEach((p, i) => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, spotIdx === 0 ? 4 : 3, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.fill();
            ctx.strokeStyle = '#0a0e1a';
            ctx.lineWidth = 1.5;
            ctx.stroke();
        });
    });

    // X-axis labels (chi hien thi 1 so label de khong bi chat)
    if (timeLabels.length > 0) {
        ctx.fillStyle = '#64748b';
        ctx.font = '10px Inter, sans-serif';
        ctx.textAlign = 'center';
        const step = Math.max(1, Math.floor(timeLabels.length / 8));
        for (let i = 0; i < timeLabels.length; i += step) {
            const x = padding.left + (chartW / Math.max(timeLabels.length - 1, 1)) * i;
            // Xoay label
            ctx.save();
            ctx.translate(x, H - padding.bottom + 14);
            ctx.rotate(-Math.PI / 6);
            ctx.fillText(timeLabels[i], 0, 0);
            ctx.restore();
        }
    }

    // Y-axis title
    ctx.save();
    ctx.fillStyle = '#94a3b8';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.translate(14, padding.top + chartH / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Chi so san may (%)', 0, 0);
    ctx.restore();

    // Render legend
    renderTimelineLegend(spots);
}

function renderTimelineLegend(spots) {
    const legend = document.getElementById('timeline-legend');
    if (!legend) return;

    legend.innerHTML = spots.map((spot, i) => {
        const color = TIMELINE_COLORS[i % TIMELINE_COLORS.length];
        return `
            <div class="legend-item">
                <span class="legend-color" style="background: ${color}"></span>
                <span class="legend-name">#${spot.rank} ${spot.location_name}</span>
                <span class="legend-value" style="color: ${color}">${spot.probability}%</span>
            </div>
        `;
    }).join('');
}

function hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
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
    loadReviews(locationName);
    initReviewsForm(locationName);
}

// ─── Community Reviews & Moderation Logic ─────────────────────

const SPOT_IDS = {
    "Đồi chè Cầu Đất": 1,
    "Đồi Đa Phú": 2,
    "Đồi Du Sinh": 3,
    "Đồi Thiên Phúc Đức": 4,
    "Trại Mát": 5,
    "Đỉnh Hòn Bồ": 6,
    "Đỉnh Pinhatt": 7,
    "Đỉnh Langbiang": 8,
    "Đồi Robin": 9,
    "Đỉnh Rada": 10
};

async function loadReviews(locationName) {
    const locationId = SPOT_IDS[locationName] || 1;
    const reviewsList = document.getElementById('reviews-list');
    if (!reviewsList) return;

    const role = getUserRole();
    const currentUserId = getUserId();
    const isAdminOrMod = (role === 'admin' || role === 'moderator');

    try {
        let reviews = [];
        if (isAdminOrMod) {
            reviews = await apiGetReviewsAll(locationId);
        } else {
            reviews = await apiGetReviews(locationId);
        }

        if (reviews.length === 0) {
            reviewsList.innerHTML = `<div style="color: var(--text-muted); text-align: center; padding: var(--space-lg);">Chưa có bình luận nào cho địa điểm này. Hãy là người đầu tiên chia sẻ trải nghiệm!</div>`;
            return;
        }

        reviewsList.innerHTML = reviews.map(rev => {
            const starsHTML = '★'.repeat(rev.rating) + '☆'.repeat(5 - rev.rating);
            const dateStr = new Date(rev.created_at).toLocaleDateString('vi-VN', {
                year: 'numeric', month: 'long', day: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
            
            const isPending = !rev.is_approved;
            const badgeHTML = isPending ? `<span class="review-badge-pending">Chờ duyệt</span>` : '';
            
            const showApprove = isAdminOrMod && isPending;
            const showDelete = isAdminOrMod || (currentUserId && rev.user_id === currentUserId);

            const approveBtn = showApprove ? `<button class="btn-approve" onclick="handleApproveReview(${rev.id}, '${locationName}')">Duyệt</button>` : '';
            const deleteBtn = showDelete ? `<button class="btn-delete" onclick="handleDeleteReview(${rev.id}, '${locationName}')">Xóa</button>` : '';
            
            const actionsHTML = (approveBtn || deleteBtn) ? `
                <div class="review-actions">
                    ${approveBtn}
                    ${deleteBtn}
                </div>
            ` : '';

            return `
                <div class="review-card" data-id="${rev.id}">
                    <div class="review-header">
                        <div class="reviewer-info">
                            <span class="reviewer-name">👤 ${rev.username}</span>
                            ${badgeHTML}
                        </div>
                        <span class="review-stars">${starsHTML}</span>
                    </div>
                    <div class="review-body">${rev.comment || ''}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                        <span class="review-date">${dateStr}</span>
                        ${actionsHTML}
                    </div>
                </div>
            `;
        }).join('');

    } catch (err) {
        console.error('Error loading reviews:', err);
        reviewsList.innerHTML = `<div style="color: var(--accent-red); text-align: center; padding: var(--space-lg);">Lỗi tải bình luận: ${err.message}</div>`;
    }
}

async function handleApproveReview(reviewId, locationName) {
    showLoading('Đang duyệt bình luận...');
    try {
        await apiApproveReview(reviewId);
        hideLoading();
        showToast('Duyệt bình luận thành công!', 'success');
        loadReviews(locationName);
    } catch (err) {
        hideLoading();
        showToast(err.message);
    }
}

async function handleDeleteReview(reviewId, locationName) {
    if (!confirm('Bạn có chắc chắn muốn xóa bình luận này không?')) return;
    showLoading('Đang xóa bình luận...');
    try {
        await apiDeleteReview(reviewId);
        hideLoading();
        showToast('Xóa bình luận thành công!', 'success');
        loadReviews(locationName);
    } catch (err) {
        hideLoading();
        showToast(err.message);
    }
}

// Bind to window for inline onclick actions
window.handleApproveReview = handleApproveReview;
window.handleDeleteReview = handleDeleteReview;

function initReviewsForm(locationName) {
    const locationId = SPOT_IDS[locationName] || 1;
    const form = document.getElementById('review-submit-form');
    if (!form) return;

    const starsContainer = document.getElementById('review-star-rating');
    const ratingInput = document.getElementById('review-rating-value');
    
    if (starsContainer && ratingInput) {
        const starBtns = starsContainer.querySelectorAll('.star-btn');
        starBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const val = parseInt(btn.getAttribute('data-value'));
                ratingInput.value = val;
                
                starBtns.forEach(sb => {
                    const sbVal = parseInt(sb.getAttribute('data-value'));
                    if (sbVal <= val) {
                        sb.style.color = 'var(--accent-gold)';
                    } else {
                        sb.style.color = '#4b5563';
                    }
                });
            });
        });
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const rating = parseInt(ratingInput.value);
        const comment = document.getElementById('review-comment-text').value.trim();

        if (!comment) {
            showToast('Vui lòng nhập nội dung bình luận');
            return;
        }

        showLoading('Đang gửi đánh giá...');
        try {
            await apiCreateReview(locationId, rating, comment);
            hideLoading();
            document.getElementById('review-comment-text').value = '';
            
            const role = getUserRole();
            const isAdminOrMod = (role === 'admin' || role === 'moderator');

            if (isAdminOrMod) {
                showToast('Gửi bình luận thành công!', 'success');
            } else {
                showToast('Gửi bình luận thành công! Chờ duyệt.', 'success');
                const note = document.getElementById('review-form-note');
                if (note) {
                    note.style.display = 'block';
                    setTimeout(() => { note.style.display = 'none'; }, 5000);
                }
            }
            
            loadReviews(locationName);
        } catch (err) {
            hideLoading();
            showToast(err.message);
        }
    });
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

// ─── Nearby Places Modal Logic ──────────────────────────────

function openNearbyModal(locationName, lat, lon) {
    const modal = document.getElementById('places-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalList = document.getElementById('modal-places-list');
    const loading = document.getElementById('modal-loading');

    modalTitle.textContent = `Tien ich quanh ${locationName}`;
    modalList.innerHTML = '';
    loading.style.display = 'block';
    modal.classList.add('active');

    // Dong modal khi bam nut X hoac bam ra ngoai
    document.getElementById('modal-close').onclick = () => modal.classList.remove('active');
    modal.onclick = (e) => {
        if (e.target === modal) modal.classList.remove('active');
    };

    // Goi API S2
    apiGetNearbyPlaces(lat, lon, 2.0)
        .then(res => {
            loading.style.display = 'none';
            if (res.places.length === 0) {
                modalList.innerHTML = '<div class="empty-state"><p>Chua tim thay tien ich nao quanh day.</p></div>';
                return;
            }

            modalList.innerHTML = res.places.map(p => {
                const img = (p.photos && p.photos.length > 0) ? p.photos[0].url : 'https://via.placeholder.com/100x100?text=No+Image';
                return `
                <div class="place-card">
                    <img src="${img}" class="place-img" alt="${p.name}">
                    <div class="place-info">
                        <div class="place-category">${p.category}</div>
                        <div class="place-name">${p.name}</div>
                        <div class="place-rating">
                            <span>&#9733; ${p.avg_rating}</span> (${p.review_count} danh gia)
                        </div>
                        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">Cach day ${(p.distance_km || 0).toFixed(1)} km</div>
                    </div>
                </div>
                `;
            }).join('');
        })
        .catch(err => {
            loading.style.display = 'none';
            modalList.innerHTML = `<div style="color: #ef4444; padding: 20px; text-align: center;">Loi: ${err.message}</div>`;
        });
}
