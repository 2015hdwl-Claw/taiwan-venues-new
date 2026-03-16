// ===== 全局變數 =====
let allVenues = [];
let currentVenue = null;
let currentRoom = null;

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', async () => {
    await loadVenues();
    loadRoomDetail();
});

// ===== 載入場地資料 =====
async function loadVenues() {
    try {
        const response = await fetch('venues.json');
        if (!response.ok) throw new Error('無法載入資料');
        allVenues = await response.json();
        console.log(`✅ 成功載入 ${allVenues.length} 個場地`);
    } catch (error) {
        console.error('載入場地失敗:', error);
        showError('無法載入場地資料');
    }
}

// ===== 載入會議室詳情 =====
function loadRoomDetail() {
    const params = new URLSearchParams(window.location.search);
    const venueId = params.get('venueId');
    const roomId = params.get('roomId');
    
    if (!venueId || !roomId) {
        showError('缺少必要參數');
        return;
    }
    
    // 尋找場地
    currentVenue = allVenues.find(v => v.id === parseInt(venueId));
    
    if (!currentVenue) {
        showError('找不到此場地');
        return;
    }
    
    // 尋找會議室
    if (!currentVenue.rooms || currentVenue.rooms.length === 0) {
        showError('此場地無會議室資料');
        return;
    }
    
    currentRoom = currentVenue.rooms.find(r => r.id === roomId);
    
    if (!currentRoom) {
        showError('找不到此會議室');
        return;
    }
    
    // 渲染會議室資訊
    renderRoomDetail();
    
    // 隱藏載入狀態，顯示內容
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('roomContent').style.display = 'block';
}

// ===== 渲染會議室詳情 =====
function renderRoomDetail() {
    const room = currentRoom;
    const venue = currentVenue;
    
    // 更新頁面標題
    document.title = `${room.name} - ${venue.name} - 活動大師`;
    
    // 麵包屑
    document.getElementById('breadcrumbVenue').href = `venue.html?id=${venue.id}`;
    document.getElementById('breadcrumbVenue').textContent = venue.name;
    document.getElementById('breadcrumbRoom').textContent = room.name;
    
    // 主圖
    const mainImage = room.image || room.images?.main || venue.images?.main || 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800';
    document.getElementById('roomMainImage').src = mainImage;
    document.getElementById('roomMainImage').alt = room.name;
    
    // 基本資訊
    document.getElementById('roomName').textContent = room.name;
    document.getElementById('roomLocation').textContent = `${venue.name}${room.floor ? ' ' + room.floor : ''}`;
    
    // 空間資訊
    document.getElementById('roomArea').textContent = room.area ? `${room.area} 坪` : '未提供';
    document.getElementById('roomCeiling').textContent = room.ceiling ? `${room.ceiling} 米` : '未提供';
    document.getElementById('roomFloor').textContent = room.floor || '未提供';
    document.getElementById('roomWindow').textContent = room.hasWindow ? '有自然採光' : '無窗戶';
    
    // 容納人數
    renderCapacity(room.capacity);
    
    // 價格方案
    renderPricing(room.pricing);
    
    // 設備清單
    renderEquipment(room.equipment);
    
    // 可用時段
    renderTime(room.availableTimeWeekday, room.availableTimeWeekend);
    
    // 特色標籤
    if (room.features && room.features.length > 0) {
        renderFeatures(room.features);
    }
    
    // 注意事項
    if (room.notes) {
        renderNotes(room.notes);
    }
    
    // 聯絡按鈕
    if (venue.contactPhone) {
        const callBtn = document.getElementById('roomCallBtn');
        callBtn.style.display = 'inline-flex';
        callBtn.href = `tel:${venue.contactPhone}`;
    }
}

// ===== 渲染容納人數 =====
function renderCapacity(capacity) {
    if (!capacity) {
        document.querySelectorAll('.capacity-card .capacity-value').forEach(el => {
            el.textContent = '-';
        });
        return;
    }
    
    // 劇院式
    if (capacity.theater) {
        document.querySelector('#capTheater .capacity-value').textContent = capacity.theater + ' 人';
    } else {
        document.getElementById('capTheater').style.opacity = '0.5';
    }
    
    // 課桌式
    if (capacity.classroom) {
        document.querySelector('#capClassroom .capacity-value').textContent = capacity.classroom + ' 人';
    } else {
        document.getElementById('capClassroom').style.opacity = '0.5';
    }
    
    // U型
    if (capacity.ushape) {
        document.querySelector('#capUshape .capacity-value').textContent = capacity.ushape + ' 人';
    } else {
        document.getElementById('capUshape').style.opacity = '0.5';
    }
    
    // 圓桌式
    if (capacity.roundtable) {
        document.querySelector('#capRoundtable .capacity-value').textContent = capacity.roundtable + ' 人';
    } else {
        document.getElementById('capRoundtable').style.opacity = '0.5';
    }
}

// ===== 渲染價格方案 =====
function renderPricing(pricing) {
    if (!pricing) {
        document.getElementById('priceHalfDay').textContent = '價格面議';
        document.getElementById('priceFullDay').textContent = '價格面議';
        document.getElementById('priceOvertime').textContent = '另議';
        return;
    }
    
    document.getElementById('priceHalfDay').textContent = pricing.halfDay 
        ? `$${pricing.halfDay.toLocaleString()}` 
        : '另議';
    
    document.getElementById('priceFullDay').textContent = pricing.fullDay 
        ? `$${pricing.fullDay.toLocaleString()}` 
        : '另議';
    
    document.getElementById('priceOvertime').textContent = pricing.overtime 
        ? `$${pricing.overtime.toLocaleString()}` 
        : '另議';
}

// ===== 渲染設備清單 =====
function renderEquipment(equipment) {
    const grid = document.getElementById('equipmentGrid');
    
    if (!equipment || equipment.length === 0) {
        grid.innerHTML = '<div class="equipment-empty">基本設備</div>';
        return;
    }
    
    const equipmentIcons = {
        '投影設備': '📽️',
        '投影機': '📽️',
        '音響系統': '🔊',
        '音響': '🔊',
        '無線麥克風': '🎤',
        '麥克風': '🎤',
        '白板': '📋',
        '翻頁板': '📋',
        'WiFi': '📶',
        '無線網路': '📶',
        '空調': '❄️',
        '冷氣': '❄️',
        '茶水服務': '☕',
        '茶水': '☕',
        '停車位': '🅿️',
        '停車': '🅿️',
        '舞台': '🎭',
        '燈光控制': '💡',
        '燈光': '💡',
        '直播設備': '📹',
        '錄影設備': '📹',
        '桌椅': '🪑',
        '講台': '🎙️',
        '投票系統': '🗳️',
        '同步翻譯': '🌐'
    };
    
    equipment.forEach(item => {
        const icon = equipmentIcons[item] || '✓';
        const card = document.createElement('div');
        card.className = 'equipment-item';
        card.innerHTML = `
            <span class="equipment-icon">${icon}</span>
            <span class="equipment-name">${item}</span>
        `;
        grid.appendChild(card);
    });
}

// ===== 渲染可用時段 =====
function renderTime(weekday, weekend) {
    document.getElementById('timeWeekday').textContent = weekday || '未提供';
    document.getElementById('timeWeekend').textContent = weekend || '未提供';
}

// ===== 渲染特色標籤 =====
function renderFeatures(features) {
    const section = document.getElementById('featuresSection');
    const container = document.getElementById('featuresTags');
    
    section.style.display = 'block';
    
    features.forEach(feature => {
        const tag = document.createElement('span');
        tag.className = 'feature-tag';
        tag.textContent = feature;
        container.appendChild(tag);
    });
}

// ===== 渲染注意事項 =====
function renderNotes(notes) {
    const section = document.getElementById('notesSection');
    const container = document.getElementById('roomNotes');
    
    section.style.display = 'block';
    
    // 將注意事項分割成列表
    const items = notes.split(/[,，、；;]/).filter(s => s.trim());
    
    if (items.length > 1) {
        const list = document.createElement('ul');
        list.className = 'notes-list';
        items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item.trim();
            list.appendChild(li);
        });
        container.appendChild(list);
    } else {
        container.textContent = notes;
    }
}

// ===== 導航函數 =====
function goBackToVenue() {
    if (currentVenue) {
        window.location.href = `venue.html?id=${currentVenue.id}`;
    } else {
        window.location.href = 'index.html';
    }
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
