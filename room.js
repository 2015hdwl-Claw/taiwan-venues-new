// ===== 全局變數 =====
let allVenues = [];
let currentVenue = null;
let currentRoom = null;

// ===== 版本控制 =====
const DATA_VERSION = '20260323-v4'; // 與 app.js、venue.js 保持同步

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', async () => {
    await loadVenues();
    loadRoomDetail();
});

// ===== 載入場地資料 =====
async function loadVenues() {
    try {
        // 添加版本參數防止快取
        const response = await fetch(`venues.json?v=${DATA_VERSION}`);
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
    
    if (!venueId) {
        showError('缺少 venueId 參數');
        return;
    }
    
    // roomId 可選，如果沒有指定，默認顯示第一個會議室
    
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
    
    // 如果沒有指定 roomId，默認顯示第一個會議室（通常是最大型場地）
    if (!roomId) {
        currentRoom = currentVenue.rooms[0];
    } else {
        currentRoom = currentVenue.rooms.find(r => r.id === roomId);
        
        if (!currentRoom) {
            showError('找不到此會議室');
            return;
        }
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
    
    // 主圖（優先使用 images 陣列第一張，其次是 images.main，再來是 photo）
    let mainImage;
    if (Array.isArray(room.images) && room.images.length > 0) {
        mainImage = room.images[0];
    } else if (room.images && typeof room.images === 'object' && room.images.main) {
        mainImage = room.images.main;
    } else if (room.photo) {
        mainImage = room.photo;
    } else if (venue.images && venue.images.main) {
        mainImage = venue.images.main;
    } else {
        mainImage = 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800';
    }
    document.getElementById('roomMainImage').src = mainImage;
    document.getElementById('roomMainImage').alt = room.name;
    
    // 基本資訊
    document.getElementById('roomName').textContent = room.name;
    document.getElementById('roomLocation').textContent = `${venue.name}${room.floor ? ' ' + room.floor : ''}`;
    
    // 空間資訊（新版）
    renderSpaceInfo(room);
    
    // 容納人數
    renderCapacity(room.capacity);
    
    // 價格方案
    renderPricing(room.price || room.pricing);
    
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

// ===== 渲染空間資訊（新版） =====
function renderSpaceInfo(room) {
    const highlightCard = document.getElementById('areaHighlightCard');
    const mainValue = document.getElementById('roomAreaMain');
    const secondaryValue = document.getElementById('roomAreaSecondary');
    const grid = document.getElementById('spaceInfoGrid');
    const descSection = document.getElementById('spaceDescription');
    const descText = document.getElementById('roomDescription');

    // 收集所有可用的空間資訊（按照指定順序）
    const infoItems = [];

    // 場地平面圖（第一位）- 使用場地（venue）的 floorPlan
    const floorPlanSection = document.getElementById('floorPlanSection');
    const floorPlanEmbed = document.getElementById('floorPlanEmbed');
    const floorPlanIframe = document.getElementById('floorPlanIframe');
    const floorPlanImage = document.getElementById('floorPlanImage');

    // 優先使用場地的 floorPlan PDF
    const floorPlanUrl = currentVenue?.floorPlan || room.floorPlan || room.layoutImage;

    if (floorPlanUrl) {
        floorPlanSection.style.display = 'block';

        // 判斷是否為 PDF
        const isPDF = floorPlanUrl.toLowerCase().endsWith('.pdf') || floorPlanUrl.toLowerCase().includes('.pdf');

        if (isPDF) {
            // PDF 使用 <embed> 顯示（繞過 X-Frame-Options 限制）
            floorPlanEmbed.style.display = 'block';
            floorPlanIframe.src = floorPlanUrl;
            // 使用 embed 作為備用
            floorPlanIframe.outerHTML = `<embed id="floorPlanIframe" class="floor-plan-iframe" src="${floorPlanUrl}" type="application/pdf" width="100%" height="500px">`;
            floorPlanImage.style.display = 'none';
        } else {
            // 圖片直接顯示
            floorPlanEmbed.style.display = 'none';
            floorPlanImage.style.display = 'block';
            floorPlanImage.src = floorPlanUrl;
            floorPlanImage.alt = `${room.name} 場地圖`;
        }
    } else {
        floorPlanSection.style.display = 'none';
    }

    // 空間面積（第二位）- 重點突出
    if (room.area || room.areaSqm) {
        highlightCard.style.display = 'flex';

        // 主要顯示坪數
        if (room.area) {
            mainValue.textContent = `${room.area} 坪`;
        } else if (room.areaSqm) {
            mainValue.textContent = `${room.areaSqm} m²`;
        }

        // 次要顯示（轉換）
        if (room.area && room.areaSqm) {
            secondaryValue.textContent = `約 ${room.areaSqm} 平方公尺`;
        } else if (room.area && !room.areaSqm) {
            // 自動計算平方公尺（1 坪 ≈ 3.3058 m²）
            const sqm = Math.round(room.area * 3.3058);
            secondaryValue.textContent = `約 ${sqm} 平方公尺`;
        } else if (room.areaSqm && !room.area) {
            // 自動計算坪數
            const ping = Math.round(room.areaSqm / 3.3058 * 10) / 10;
            secondaryValue.textContent = `約 ${ping} 坪`;
        }
    } else {
        highlightCard.style.display = 'none';
    }

    // 空間尺寸（第三位）- 長X寬X高
    const hasLength = room.length;
    const hasWidth = room.width;
    const hasHeight = room.height || room.ceiling;
    const heightValue = room.height || room.ceiling;

    if (hasLength && hasWidth && hasHeight) {
        infoItems.push({
            icon: '📐',
            label: '空間尺寸',
            value: `${room.length} × ${room.width} × ${heightValue} 公尺（長×寬×高）`
        });
    } else if (hasLength && hasWidth) {
        infoItems.push({
            icon: '📐',
            label: '空間尺寸',
            value: `${room.length} × ${room.width} 公尺（長×寬）`
        });
    } else if (hasHeight) {
        infoItems.push({
            icon: '📏',
            label: '挑高',
            value: `${heightValue} 公尺`
        });
    }

    // 空間形狀（第四位）
    if (room.shape) {
        infoItems.push({
            icon: '🔲',
            label: '空間形狀',
            value: room.shape
        });
    }

    // 柱子（第五位）
    if (room.pillar !== undefined) {
        infoItems.push({
            icon: '🏛️',
            label: '柱子',
            value: room.pillar ? (room.pillarCount ? `有 ${room.pillarCount} 根柱子` : '有柱子') : '無柱'
        });
    } else if (room.pillars !== undefined) {
        infoItems.push({
            icon: '🏛️',
            label: '柱子',
            value: room.pillars ? `有 ${room.pillars} 根柱子` : '無柱'
        });
    }

    // 樓層（第六位）
    if (room.floor) {
        infoItems.push({
            icon: '🏢',
            label: '樓層',
            value: room.floor
        });
    }

    // 會議室特色說明（第七位）
    if (room.description) {
        descSection.style.display = 'block';
        descText.textContent = room.description;
    } else {
        descSection.style.display = 'none';
    }

    // 其他資訊（採光、分割等）
    if (room.hasWindow !== undefined) {
        infoItems.push({
            icon: '🪟',
            label: '採光',
            value: room.hasWindow ? '有自然採光' : '無窗戶'
        });
    }

    if (room.dividable) {
        infoItems.push({
            icon: '🔲',
            label: '空間分割',
            value: room.dividable
        });
    }

    // 渲染資訊卡片
    if (infoItems.length > 0) {
        grid.innerHTML = infoItems.map(item => `
            <div class="space-info-item">
                <div class="space-info-item-icon">${item.icon}</div>
                <div class="space-info-item-content">
                    <div class="space-info-item-label">${item.label}</div>
                    <div class="space-info-item-value">${item.value}</div>
                </div>
            </div>
        `).join('');
    } else {
        grid.innerHTML = '';
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
    if (capacity.roundtable_min && capacity.roundtable_max) {
        document.querySelector('#capRoundtable .capacity-value').textContent = `${capacity.roundtable_min}-${capacity.roundtable_max} 人`;
    } else if (capacity.roundtable) {
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

    // 支援新版價格結構（morning, afternoon, evening）
    const halfDay = pricing.morning || pricing.afternoon || pricing.halfDay;
    const fullDay = pricing.fullDay || pricing.evening;
    const overtime = pricing.additionalHour || pricing.overtime;

    document.getElementById('priceHalfDay').textContent = halfDay
        ? `$${halfDay.toLocaleString()}`
        : '另議';

    document.getElementById('priceFullDay').textContent = fullDay
        ? `$${fullDay.toLocaleString()}`
        : '另議';

    document.getElementById('priceOvertime').textContent = overtime
        ? `$${overtime.toLocaleString()}`
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
