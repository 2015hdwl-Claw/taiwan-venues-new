// ===== 全局變數 =====
let allVenues = [];
let currentVenue = null;

// ===== 版本控制 =====
const DATA_VERSION = '20260407-v1'; // 與 app.js 保持同步

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', async () => {
    await loadVenues();
    loadVenueDetail();
});

// ===== 載入場地資料 =====
async function loadVenues() {
    try {
        const response = await fetch(`venues.json?v=${DATA_VERSION}`);
        if (!response.ok) throw new Error('無法載入資料');
        allVenues = await response.json();
        // 不過濾 active=false，讓 venue detail 可以顯示友善下架訊息
        console.log(`✅ 成功載入 ${allVenues.length} 個場地`);
    } catch (error) {
        console.error('載入場地失敗:', error);
        showError('無法載入場地資料');
    }
}

// ===== 載入場地詳情 =====
function loadVenueDetail() {
    const params = new URLSearchParams(window.location.search);
    const venueId = params.get('id');
    
    if (!venueId) {
        showError('缺少場地 ID');
        return;
    }
    
    // 尋找場地（包含 inactive，用於顯示友善訊息）
    currentVenue = allVenues.find(v => v.id === parseInt(venueId));

    // 暴露給 Chat Widget 使用
    window.currentVenueId = parseInt(venueId);
    window.currentVenueName = currentVenue?.name || null;

    if (!currentVenue) {
        showError('找不到此場地，請確認 ID 是否正確');
        return;
    }

    // 檢查場地是否已下架（顯示友善訊息而非隱藏）
    if (currentVenue.active === false) {
        showError('此場地目前暫停更新，如需資料請聯繫我們');
        return;
    }
    
    // 渲染場地資訊
    renderVenueDetail();
    
    // 隱藏載入狀態，顯示內容
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('venueContent').style.display = 'block';
}

// ===== 渲染場地詳情 =====
function renderVenueDetail() {
    const venue = currentVenue;
    
    // 更新頁面標題
    document.title = `${venue.name} - 活動大師`;
    
    // 主圖（使用官網圖片，如果沒有則隱藏）
    if (venue.images?.main) {
        const mainImage = venue.images.main;
        const imgElement = document.getElementById('venueMainImage');
        imgElement.src = mainImage;
        imgElement.alt = venue.name;
        imgElement.style.display = 'block';
    } else {
        document.getElementById('venueMainImage').style.display = 'none';
    }
    
    // 基本資訊
    document.getElementById('venueType').textContent = venue.venueType || '場地';
    document.getElementById('venueName').textContent = venue.name;
    document.getElementById('venueAddress').querySelector('span').textContent = venue.address || '地址未提供';
    
    // 容納人數
    let capacityText = '-';
    if (venue.maxCapacityTheater && venue.maxCapacityClassroom) {
        capacityText = `劇院式 ${venue.maxCapacityTheater} 人 / 教室式 ${venue.maxCapacityClassroom} 人`;
    } else if (venue.maxCapacityTheater) {
        capacityText = `劇院式 ${venue.maxCapacityTheater} 人`;
    } else if (venue.maxCapacityClassroom) {
        capacityText = `教室式 ${venue.maxCapacityClassroom} 人`;
    }
    document.getElementById('venueCapacity').textContent = capacityText;
    
    // 價格
    let priceText = '價格面議';
    if (venue.priceHalfDay && venue.priceFullDay) {
        priceText = `$${venue.priceHalfDay.toLocaleString()} - $${venue.priceFullDay.toLocaleString()}`;
    } else if (venue.priceHalfDay) {
        priceText = `$${venue.priceHalfDay.toLocaleString()} 起`;
    } else if (venue.priceFullDay) {
        priceText = `$${venue.priceFullDay.toLocaleString()} 起`;
    }
    document.getElementById('venuePrice').textContent = priceText;
    
    // 可用時段
    let timeText = '-';
    if (venue.availableTimeWeekday && venue.availableTimeWeekend) {
        timeText = `平日 ${venue.availableTimeWeekday} / 假日 ${venue.availableTimeWeekend}`;
    } else if (venue.availableTimeWeekday) {
        timeText = venue.availableTimeWeekday;
    }
    document.getElementById('venueTime').textContent = timeText;
    
    // 設備
    document.getElementById('venueEquipment').textContent = venue.equipment || '未提供';

    // 風險評估
    renderRisks(venue);

    // 專業知識
    renderPricingTips(venue);

    // 租借規定
    renderRules(venue);

    // 相簿照片
    renderGallery(venue);

    // 聯絡資訊
    renderContactInfo(venue);
    
    // 會議室列表
    renderRooms(venue);
}

// ===== 渲染聯絡資訊 =====
function renderContactInfo(venue) {
    // 聯絡人
    if (venue.contactPerson) {
        document.getElementById('contactPerson').style.display = 'flex';
        document.getElementById('contactPerson').querySelector('.contact-value').textContent = venue.contactPerson;
    }
    
    // 電話
    if (venue.contactPhone) {
        document.getElementById('contactPhone').style.display = 'flex';
        const phoneLink = document.getElementById('contactPhone').querySelector('.contact-link');
        phoneLink.href = `tel:${venue.contactPhone}`;
        phoneLink.textContent = venue.contactPhone;
        
        // 撥打按鈕
        document.getElementById('callBtn').style.display = 'inline-flex';
        document.getElementById('callBtn').href = `tel:${venue.contactPhone}`;
    }
    
    // Email
    if (venue.contactEmail) {
        document.getElementById('contactEmail').style.display = 'flex';
        const emailLink = document.getElementById('contactEmail').querySelector('.contact-link');
        emailLink.href = `mailto:${venue.contactEmail}`;
        emailLink.textContent = venue.contactEmail;
    }
    
    // 官網
    if (venue.url) {
        document.getElementById('venueUrl').style.display = 'flex';
        const urlLink = document.getElementById('venueUrl').querySelector('.contact-link');
        urlLink.href = venue.url;
        
        // 官網按鈕
        document.getElementById('websiteBtn').style.display = 'inline-flex';
        document.getElementById('websiteBtn').href = venue.url;
    }
}

// ===== 渲染會議室列表 =====
function renderRooms(venue) {
    const roomsGrid = document.getElementById('roomsGrid');
    const noRoomsState = document.getElementById('noRoomsState');
    const roomsCount = document.getElementById('roomsCount');
    
    const rooms = venue.rooms || [];
    
    if (rooms.length === 0) {
        noRoomsState.style.display = 'block';
        roomsCount.textContent = '(尚無資料)';
        return;
    }
    
    roomsCount.textContent = `(${rooms.length} 間)`;
    
    rooms.forEach(room => {
        const card = createRoomCard(room, venue.id);
        roomsGrid.appendChild(card);
    });
}

// ===== 創建會議室卡片 =====
function createRoomCard(room, venueId) {
    const card = document.createElement('div');
    card.className = 'room-card';
    card.onclick = () => goToRoom(venueId, room.id);

    // 圖片處理
    let imageUrl = null;
    if (room.images && typeof room.images === 'object' && room.images.main) {
        imageUrl = room.images.main;
    } else if (Array.isArray(room.images) && room.images.length > 0) {
        imageUrl = room.images[0];
    } else if (room.photo) {
        imageUrl = room.photo;
    }

    // 容納人數視覺化
    let capacityBars = '';
    if (room.capacity) {
        const caps = [];
        if (room.capacity.theater) caps.push(`<span class="cap-item"><span class="cap-icon">🎭</span><span class="cap-num">${room.capacity.theater}</span></span>`);
        if (room.capacity.classroom) caps.push(`<span class="cap-item"><span class="cap-icon">📚</span><span class="cap-num">${room.capacity.classroom}</span></span>`);
        if (room.capacity.ushape) caps.push(`<span class="cap-item"><span class="cap-icon">🔀</span><span class="cap-num">${room.capacity.ushape}</span></span>`);
        if (room.capacity.banquet) caps.push(`<span class="cap-item"><span class="cap-icon">🍽️</span><span class="cap-num">${room.capacity.banquet}</span></span>`);
        capacityBars = caps.join('');
    }

    // 價格
    let priceText = '價格面議';
    let priceClass = '';
    if (room.pricing) {
        if (room.pricing.halfDay && room.pricing.fullDay) {
            priceText = `$${(room.pricing.halfDay/1000).toFixed(0)}k - $${(room.pricing.fullDay/1000).toFixed(0)}k`;
            priceClass = 'has-price';
        } else if (room.pricing.fullDay) {
            priceText = `$${(room.pricing.fullDay/1000).toFixed(0)}k/天`;
            priceClass = 'has-price';
        } else if (room.pricing.halfDay) {
            priceText = `$${(room.pricing.halfDay/1000).toFixed(0)}k/半天`;
            priceClass = 'has-price';
        } else if (room.pricing.note) {
            priceText = room.pricing.note;
            priceClass = 'price-note';
        }
    }

    // 限制警示
    let limitationHtml = '';
    if (room.limitations && room.limitations.length > 0) {
        const firstLimitation = room.limitations[0];
        limitationHtml = `
            <div class="room-limitation-warning">
                <span class="warning-icon">⚠️</span>
                <span class="warning-text">${firstLimitation.length > 50 ? firstLimitation.substring(0, 50) + '...' : firstLimitation}</span>
                ${room.limitations.length > 1 ? `<span class="warning-more">+${room.limitations.length - 1}</span>` : ''}
            </div>
        `;
    }

    // 天花板高度
    const ceilingInfo = room.ceilingHeight ? `<span class="ceiling-info">挑高 ${room.ceilingHeight}m</span>` : '';

    // 進場資訊
    let loadInInfo = '';
    if (room.loadIn) {
        const items = [];
        if (room.loadIn.elevator) items.push('有貨梯');
        if (room.loadIn.vehicleAccess) items.push('車輛可達');
        if (items.length > 0) loadInInfo = `<span class="loadin-info">${items.join(' · ')}</span>`;
    }

    // 圖片區域
    const imageHtml = imageUrl
        ? `<div class="room-image"><img src="${imageUrl}" alt="${room.name}" onerror="this.style.display='none'"></div>`
        : '<div class="room-image room-image-placeholder">🚪</div>';

    card.innerHTML = `
        ${imageHtml}
        <div class="room-card-content">
            <div class="room-card-header">
                <h3 class="room-card-name">${room.name}</h3>
                ${room.floor ? `<span class="room-floor">${room.floor}</span>` : ''}
            </div>

            <div class="room-card-meta">
                <span class="meta-item">
                    <span class="meta-icon">📐</span>
                    ${room.area ? room.area + ' 坪' : '坪數未提供'}
                </span>
                ${ceilingInfo}
                ${loadInInfo}
            </div>

            ${capacityBars ? `<div class="room-capacity-bar">${capacityBars}</div>` : ''}

            ${limitationHtml}

            <div class="room-card-footer">
                <span class="room-price ${priceClass}">${priceText}</span>
                <button class="room-detail-btn">查看詳情 →</button>
            </div>
        </div>
    `;

    return card;
}

// ===== 導航函數 =====
function goToRoom(venueId, roomId) {
    window.location.href = `room.html?venueId=${venueId}&roomId=${roomId}`;
}

function goBack() {
    // 返回首頁
    window.location.href = 'index.html';
}

function goHome() {
    window.location.href = 'index.html';
}

// ===== 顯示錯誤 =====
function showError(message) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('errorState').style.display = 'block';
    document.getElementById('errorState').querySelector('h3').textContent = message;
}

// ===== 渲染相簿照片 =====
function renderGallery(venue) {
    const gallerySection = document.getElementById('gallerySection');
    const galleryContainer = document.getElementById('venueGallery');

    // 檢查是否有 gallery 照片
    const gallery = venue.images?.gallery;

    if (!gallery || !Array.isArray(gallery) || gallery.length === 0) {
        gallerySection.style.display = 'none';
        return;
    }

    // 顯示相簿區域
    gallerySection.style.display = 'block';

    // 清空容器
    galleryContainer.innerHTML = '';

    // 添加照片
    gallery.forEach((photoUrl, index) => {
        const photoDiv = document.createElement('div');
        photoDiv.className = 'gallery-photo';

        const img = document.createElement('img');
        img.src = photoUrl;
        img.alt = `${venue.name} - 照片 ${index + 1}`;
        img.loading = 'lazy';

        // 錯誤處理：如果圖片載入失敗，隱藏該照片
        img.onerror = function() {
            this.style.display = 'none';
        };

        photoDiv.appendChild(img);
        galleryContainer.appendChild(photoDiv);
    });
}

// ===== 渲染風險評估 =====
function renderRisks(venue) {
    const section = document.getElementById('risksSection');
    const container = document.getElementById('risksContent');
    const risks = venue.risks;
    if (!risks || typeof risks !== 'object') { section.style.display = 'none'; return; }

    const items = [];
    if (risks.bookingLeadTime) {
        items.push({ icon: '📅', label: '預約提前量', value: risks.bookingLeadTime });
    }
    if (risks.peakSeasons && risks.peakSeasons.length > 0) {
        items.push({ icon: '🔥', label: '旺季檔期', value: risks.peakSeasons.join('、') });
    }
    if (risks.commonIssues && risks.commonIssues.length > 0) {
        items.push({ icon: '⚠️', label: '常見問題', value: risks.commonIssues.join('、') });
    }

    if (items.length === 0) { section.style.display = 'none'; return; }

    section.style.display = 'block';
    container.innerHTML = items.map(item => `
        <div class="knowledge-card risk-card">
            <div class="knowledge-icon">${item.icon}</div>
            <div class="knowledge-content">
                <div class="knowledge-label">${item.label}</div>
                <div class="knowledge-value">${item.value}</div>
            </div>
        </div>
    `).join('');
}

// ===== 渲染專業知識 =====
function renderPricingTips(venue) {
    const section = document.getElementById('pricingTipsSection');
    const container = document.getElementById('pricingTipsContent');
    const tips = venue.pricingTips;
    if (!tips || !Array.isArray(tips) || tips.length === 0) { section.style.display = 'none'; return; }

    section.style.display = 'block';
    const list = document.createElement('ul');
    list.className = 'tips-list-items';
    tips.forEach(tip => {
        const li = document.createElement('li');
        li.innerHTML = `<span class="tip-icon">💡</span> ${tip}`;
        list.appendChild(li);
    });
    container.innerHTML = '';
    container.appendChild(list);
}

// ===== 渲染租借規定 =====
function renderRules(venue) {
    const section = document.getElementById('rulesSection');
    const container = document.getElementById('rulesContent');
    const rules = venue.rules;
    if (!rules || typeof rules !== 'object') { section.style.display = 'none'; return; }

    const labels = {
        catering: '餐飲規定',
        decoration: '裝潢規定',
        sound: '音響限制',
        loadIn: '進場/撤場',
        cancellation: '取消政策',
    };
    const icons = {
        catering: '🍽️',
        decoration: '🎨',
        sound: '🔊',
        loadIn: '🚛',
        cancellation: '❌',
    };

    const items = Object.entries(rules)
        .filter(([, v]) => v && typeof v === 'string')
        .map(([key, val]) => ({
            icon: icons[key] || '📋',
            label: labels[key] || key,
            value: val,
        }));

    if (items.length === 0) { section.style.display = 'none'; return; }

    section.style.display = 'block';
    container.innerHTML = items.map(item => `
        <div class="knowledge-card rule-card">
            <div class="knowledge-icon">${item.icon}</div>
            <div class="knowledge-content">
                <div class="knowledge-label">${item.label}</div>
                <div class="knowledge-value">${item.value}</div>
            </div>
        </div>
    `).join('');
}
