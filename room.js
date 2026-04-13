// ===== 全局變數 =====
let allVenues = [];
let currentVenue = null;
let currentRoom = null;

// ===== 版本控制 =====
const DATA_VERSION = '20260412-v30'; // 與 app.js、venue.js 保持同步

// ===== Tailwind 顯示/隱藏輔助函數 =====
function showElement(el) {
    if (typeof el === 'string') el = document.getElementById(el);
    if (el) el.classList.remove('hidden');
}
function hideElement(el) {
    if (typeof el === 'string') el = document.getElementById(el);
    if (el) el.classList.add('hidden');
}
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
    hideElement('loadingState');
    showElement('roomContent');
}

// ===== 渲染會議室詳情 =====
function renderRoomDetail() {
    const room = currentRoom;
    const venue = currentVenue;

    // 更新頁面標題與 SEO meta
    const titleSuffix = '場地知識庫 | 活動大師';
    const maxCap = room.capacity ? Math.max(room.capacity.theater || 0, room.capacity.classroom || 0, room.capacity.ushape || 0) : 0;
    const ceiling = room.height || room.ceiling || room.ceilingHeight;
    const area = room.area ? room.area + '坪' : '';
    const pricing = room.price || room.pricing;
    const priceText = pricing ? (pricing.halfDay ? `半日$${pricing.halfDay.toLocaleString()}` : pricing.fullDay ? `全日$${pricing.fullDay.toLocaleString()}` : '') : '';

    document.title = `${venue.name} ${room.name} — ${maxCap ? maxCap + '人' : ''}${area ? ' ' + area : ''} | ${titleSuffix}`;

    // 動態更新 meta 標籤
    const updateMeta = (prop, content) => {
        let el = document.querySelector(`meta[property="${prop}"]`) || document.querySelector(`meta[name="${prop}"]`);
        if (el) el.setAttribute('content', content);
    };

    const metaDesc = `${venue.name} ${room.name}。${area ? area + '，' : ''}${ceiling ? '天花板' + ceiling + '米，' : ''}${maxCap ? '最多' + maxCap + '人，' : ''}${priceText ? priceText + '。' : ''}含場地限制、潛規則、踩坑經驗。${titleSuffix}`;
    const ogTitle = `${venue.name} ${room.name} — ${titleSuffix}`;
    const ogUrl = `https://taiwan-venues-new-indol.vercel.app/room.html?venueId=${venue.id}&roomId=${room.id}`;

    updateMeta('description', metaDesc);
    updateMeta('og:title', ogTitle);
    updateMeta('og:description', metaDesc);
    updateMeta('og:url', ogUrl);
    // 使用會議室圖片，沒有則用場地主圖
    const roomImage = (Array.isArray(room.images) && room.images[0]) || (room.images?.main) || (venue.images?.main);
    if (roomImage) updateMeta('og:image', roomImage);
    updateMeta('twitter:title', ogTitle);
    updateMeta('twitter:description', metaDesc);
    if (roomImage) updateMeta('twitter:image', roomImage);

    // 動態注入 JSON-LD Room 結構化資料
    const jsonLd = {
        "@context": "https://schema.org",
        "@type": "Room",
        "name": `${venue.name} ${room.name}`,
        "description": metaDesc,
        "url": ogUrl,
        ...(area && { "floorSize": { "@type": "QuantitativeValue", "value": room.area, "unitText": "坪" } }),
        ...(maxCap && { "maximumAttendeeCapacity": maxCap }),
        ...(ceiling && { "height": { "@type": "QuantitativeValue", "value": ceiling, "unitText": "米" } }),
        ...(room.floor && { "floorLevel": room.floor }),
        ...(roomImage && { "image": roomImage }),
        "isPartOf": {
            "@type": "EventVenue",
            "name": venue.name,
            ...(venue.address && { "address": { "@type": "PostalAddress", "streetAddress": venue.address } })
        }
    };
    let jsonLdScript = document.getElementById('json-ld-room');
    if (!jsonLdScript) {
        jsonLdScript = document.createElement('script');
        jsonLdScript.type = 'application/ld+json';
        jsonLdScript.id = 'json-ld-room';
        document.head.appendChild(jsonLdScript);
    }
    jsonLdScript.textContent = JSON.stringify(jsonLd);

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
    document.getElementById('roomLocationText').textContent = `${venue.name}${room.floor ? ' ' + room.floor : ''}`;

    // 快速資訊卡片
    renderQuickInfo(room);

    // 容納人數
    renderCapacity(room.capacity);

    // 價格方案
    renderPricing(room.price || room.pricing);

    // 設備清單
    renderEquipment(room.equipment);

    // 特色標籤
    if (room.features && room.features.length > 0) {
        renderFeatures(room.features);
    }

    // 隱藏限制
    renderLimitations(room);

    // 進場資訊
    renderLoadIn(room);
}

// ===== 渲染快速資訊卡片 =====
function renderQuickInfo(room) {
    // 空間面積
    const areaEl = document.getElementById('roomArea');
    if (room.area) {
        areaEl.textContent = `${room.area} 坪`;
    } else if (room.areaSqm) {
        areaEl.textContent = `${room.areaSqm} m²`;
    } else {
        areaEl.textContent = '-';
    }

    // 最大容納
    const capacityEl = document.getElementById('roomCapacityMax');
    if (room.capacity) {
        const maxCap = Math.max(
            room.capacity.theater || 0,
            room.capacity.classroom || 0,
            room.capacity.ushape || 0,
            room.capacity.roundtable || room.capacity.roundtable_max || 0
        );
        capacityEl.textContent = maxCap > 0 ? `${maxCap} 人` : '-';
    } else {
        capacityEl.textContent = '-';
    }

    // 天花板高度
    const ceilingEl = document.getElementById('roomCeiling');
    const ceiling = room.height || room.ceiling || room.ceilingHeight;
    ceilingEl.textContent = ceiling ? `${ceiling}m` : '-';

    // 樓層
    const floorEl = document.getElementById('roomFloor');
    floorEl.textContent = room.floor || '-';
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
        showElement(floorPlanSection);

        // 判斷是否為 PDF
        const isPDF = floorPlanUrl.toLowerCase().endsWith('.pdf') || floorPlanUrl.toLowerCase().includes('.pdf');

        if (isPDF) {
            // PDF 使用 <embed> 顯示（繞過 X-Frame-Options 限制）
            showElement(floorPlanEmbed);
            floorPlanIframe.src = floorPlanUrl;
            // 使用 embed 作為備用
            floorPlanIframe.outerHTML = `<embed id="floorPlanIframe" class="floor-plan-iframe" src="${floorPlanUrl}" type="application/pdf" width="100%" height="500px">`;
            hideElement(floorPlanImage);
        } else {
            // 圖片直接顯示
            hideElement(floorPlanEmbed);
            showElement(floorPlanImage);
            floorPlanImage.src = floorPlanUrl;
            floorPlanImage.alt = `${room.name} 場地圖`;
        }
    } else {
        hideElement(floorPlanSection);
    }

    // 空間面積（第二位）- 重點突出
    if (room.area || room.areaSqm) {
        showElement(highlightCard);

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
        document.getElementById('capTheater').textContent = '-';
        document.getElementById('capClassroom').textContent = '-';
        document.getElementById('capUshape').textContent = '-';
        document.getElementById('capBanquet').textContent = '-';
        return;
    }

    // 劇院式
    document.getElementById('capTheater').textContent = capacity.theater ? `${capacity.theater} 人` : '-';

    // 課桌式
    document.getElementById('capClassroom').textContent = capacity.classroom ? `${capacity.classroom} 人` : '-';

    // U型
    document.getElementById('capUshape').textContent = capacity.ushape ? `${capacity.ushape} 人` : '-';

    // 宴會式（圓桌）
    const banquet = capacity.banquet || capacity.roundtable || capacity.roundtable_max;
    if (capacity.roundtable_min && capacity.roundtable_max) {
        document.getElementById('capBanquet').textContent = `${capacity.roundtable_min}-${capacity.roundtable_max} 人`;
    } else {
        document.getElementById('capBanquet').textContent = banquet ? `${banquet} 人` : '-';
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
    hideElement('loadingState');
    showElement('errorState');
    document.getElementById('errorState').querySelector('h3').textContent = message;
}

// ===== 渲染隱藏限制 =====
function renderLimitations(room) {
    const section = document.getElementById('limitationsSection');
    const list = document.getElementById('limitationsList');
    const limitations = room.limitations;

    if (!limitations || !Array.isArray(limitations) || limitations.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';
    list.innerHTML = limitations.map(item => `<li>${item}</li>`).join('');
}

// ===== 渲染進場資訊 =====
function renderLoadIn(room) {
    const section = document.getElementById('loadInSection');
    const grid = document.getElementById('loadInGrid');
    const loadIn = room.loadIn;

    if (!loadIn || typeof loadIn !== 'object') {
        section.style.display = 'none';
        return;
    }

    const items = [];
    if (loadIn.elevator) {
        items.push({ icon: '🛗', label: '電梯/貨梯', value: loadIn.elevator });
    }
    if (loadIn.vehicleAccess !== undefined) {
        items.push({ icon: '🚗', label: '車輛直達', value: loadIn.vehicleAccess ? '可以' : '不可以' });
    }
    if (loadIn.loadingDock) {
        items.push({ icon: '🚪', label: '卸貨入口', value: loadIn.loadingDock });
    }
    if (loadIn.maxVehicleWeight) {
        items.push({ icon: '⚖️', label: '載重限制', value: loadIn.maxVehicleWeight });
    }
    if (loadIn.setupTime) {
        items.push({ icon: '⏰', label: '進場時間', value: loadIn.setupTime });
    }
    if (loadIn.teardownTime) {
        items.push({ icon: '🏁', label: '撤場時間', value: loadIn.teardownTime });
    }

    if (items.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';
    grid.innerHTML = items.map(item => `
        <div class="loadIn-item">
            <div class="loadIn-item-icon">${item.icon}</div>
            <div class="loadIn-item-content">
                <div class="loadIn-item-label">${item.label}</div>
                <div class="loadIn-item-value">${item.value}</div>
            </div>
        </div>
    `).join('');
}
