// ===== 全局變數 =====
let allVenues = [];
let currentVenue = null;

// ===== 版本控制 =====
const DATA_VERSION = '20260412-v31'; // 與 app.js 保持同步

// ===== 智能照片選擇 =====
/**
 * 選擇最合適的場地主照片
 * 優先順序：會議室照片 > 飯店外觀/大廳 > 會議室列表中的照片 > 主照片
 *
 * 不使用：房間照片 (roomtype, guestroom, bedroom)
 */
function selectVenueMainImage(venue) {
    const images = venue.images || {};
    const gallery = images.gallery || [];
    const rooms = venue.rooms || [];

    // 房間照片關鍵字（跳過）
    const roomKeywords = ['roomtype', 'guestroom', 'bedroom', '客室', '寢室', '房間', 'suite'];
    // 會議室照片關鍵字（優先）
    const meetingKeywords = ['banquet', 'meeting', 'conference', '會議', '宴會', '會議室', 'ballroom'];
    // 飯店照片關鍵字（次優先）
    const hotelKeywords = ['lobby', 'exterior', 'facade', 'building', '外觀', '大廳', '飯店', 'hotel'];

    // 輔助函數：檢查 URL 是否包含關鍵字
    const hasKeyword = (url, keywords) => {
        if (!url) return false;
        const urlLower = url.toLowerCase();
        return keywords.some(kw => urlLower.includes(kw));
    };

    const isRoomPhoto = (url) => hasKeyword(url, roomKeywords);
    const isMeetingPhoto = (url) => hasKeyword(url, meetingKeywords);
    const isHotelPhoto = (url) => hasKeyword(url, hotelKeywords);

    // 1. 從 gallery 中尋找會議室照片
    for (const url of gallery) {
        if (isMeetingPhoto(url) && !isRoomPhoto(url)) {
            console.log(`✅ 選擇會議室照片: ${url.split('/').pop()}`);
            return url;
        }
    }

    // 2. 從 gallery 中尋找飯店照片（外觀/大廳）
    for (const url of gallery) {
        if (isHotelPhoto(url) && !isRoomPhoto(url)) {
            console.log(`✅ 選擇飯店照片: ${url.split('/').pop()}`);
            return url;
        }
    }

    // 3. 從活躍會議室中尋找照片
    const activeRooms = rooms.filter(r => r.isActive !== false);
    for (const room of activeRooms) {
        const roomImages = room.images || {};
        if (roomImages.main) {
            console.log(`✅ 選擇會議室照片 (${room.name}): ${roomImages.main.split('/').pop()}`);
            return roomImages.main;
        }
        if (Array.isArray(roomImages.gallery) && roomImages.gallery.length > 0) {
            console.log(`✅ 選擇會議室照片 (${room.name}): ${roomImages.gallery[0].split('/').pop()}`);
            return roomImages.gallery[0];
        }
    }

    // 4. 從 gallery 中尋找第一個非房間照片
    for (const url of gallery) {
        if (!isRoomPhoto(url)) {
            console.log(`✅ 選擇 gallery 非房間照片: ${url.split('/').pop()}`);
            return url;
        }
    }

    // 5. 最後才使用主照片（即使是房間照片）
    if (images.main) {
        console.log(`⚠️ 使用主照片（可能是房間照片）: ${images.main.split('/').pop()}`);
        return images.main;
    }

    return null;
}

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
    hideElement('loadingState');
    showElement('venueContent');
}

// ===== 渲染場地詳情 =====
function renderVenueDetail() {
    const venue = currentVenue;
    
    // 更新頁面標題與 SEO meta
    const rooms = venue.rooms || [];
    const roomCount = rooms.length;
    const maxCap = Math.max(venue.maxCapacityTheater || 0, venue.maxCapacityClassroom || 0);
    const titleSuffix = '場地知識庫 | 活動大師';

    document.title = `${venue.name} — ${titleSuffix}`;

    // 動態更新 meta 標籤
    const updateMeta = (prop, content) => {
        let el = document.querySelector(`meta[property="${prop}"]`) || document.querySelector(`meta[name="${prop}"]`);
        if (el) el.setAttribute('content', content);
    };

    const metaDesc = `${venue.name}${venue.venueType ? '，' + venue.venueType : ''}。${roomCount ? roomCount + '間會議室，' : ''}${maxCap ? '最多' + maxCap + '人，' : ''}含天花板高度、電力負載、進場動線等官網不寫的資訊。${titleSuffix}`;
    const ogTitle = `${venue.name} — ${titleSuffix}`;
    const ogUrl = `https://taiwan-venues-new-indol.vercel.app/venue.html?id=${venue.id}`;

    updateMeta('description', metaDesc);
    updateMeta('og:title', ogTitle);
    updateMeta('og:description', metaDesc);
    updateMeta('og:url', ogUrl);
    updateMeta('twitter:title', ogTitle);
    updateMeta('twitter:description', metaDesc);

    // 智能選擇主照片
    const selectedImage = selectVenueMainImage(venue);
    if (selectedImage) {
        updateMeta('og:image', selectedImage);
    }

    // 動態注入 JSON-LD EventVenue 結構化資料
    const jsonLd = {
        "@context": "https://schema.org",
        "@type": "EventVenue",
        "name": venue.name,
        "description": metaDesc,
        "url": ogUrl,
        ...(venue.address && { "address": { "@type": "PostalAddress", "addressLocality": "台灣", "streetAddress": venue.address } }),
        ...(venue.contactPhone && { "telephone": venue.contactPhone }),
        ...(selectedImage && { "image": selectedImage }),
        ...(venue.url && { "sameAs": venue.url })
    };
    let jsonLdScript = document.getElementById('json-ld-venue');
    if (!jsonLdScript) {
        jsonLdScript = document.createElement('script');
        jsonLdScript.type = 'application/ld+json';
        jsonLdScript.id = 'json-ld-venue';
        document.head.appendChild(jsonLdScript);
    }
    jsonLdScript.textContent = JSON.stringify(jsonLd);

    // 主圖（使用智能選擇的照片）
    if (selectedImage) {
        const imgElement = document.getElementById('venueMainImage');
        imgElement.src = selectedImage;
        imgElement.alt = `${venue.name} 會議室`;
        showElement(imgElement);
    } else {
        hideElement('venueMainImage');
    }
    
    // 基本資訊
    document.getElementById('venueType').textContent = venue.venueType || '場地';
    document.getElementById('venueName').textContent = venue.name;
    document.getElementById('venueAddress').querySelector('span').textContent = venue.address || '地址未提供';
    
    // 容納人數
    let capacityText = '最大容納 -';
    if (venue.maxCapacityTheater && venue.maxCapacityClassroom) {
        capacityText = `最大容納 ${Math.max(venue.maxCapacityTheater, venue.maxCapacityClassroom)} 人`;
    } else if (venue.maxCapacityTheater) {
        capacityText = `最大容納 ${venue.maxCapacityTheater} 人`;
    } else if (venue.maxCapacityClassroom) {
        capacityText = `最大容納 ${venue.maxCapacityClassroom} 人`;
    }
    document.getElementById('venueCapacity').textContent = capacityText;

    // 會議室數量
    const roomsCount = venue.rooms ? venue.rooms.length : 0;
    const roomCountEl = document.getElementById('venueRoomCountText');
    if (roomCountEl) {
        roomCountEl.textContent = roomsCount > 0 ? `${roomsCount} 間多功能會議室` : '會議室資訊待確認';
    }
    
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
        showElement('contactPerson');
        document.getElementById('contactPerson').querySelector('.contact-value').textContent = venue.contactPerson;
    }

    // 電話
    if (venue.contactPhone) {
        showElement('contactPhone');
        const phoneLink = document.getElementById('contactPhone').querySelector('.contact-link');
        phoneLink.href = `tel:${venue.contactPhone}`;
        phoneLink.textContent = venue.contactPhone;

        // 撥打按鈕
        showElement('callBtn');
        document.getElementById('callBtn').href = `tel:${venue.contactPhone}`;
    }

    // Email
    if (venue.contactEmail) {
        showElement('contactEmail');
        const emailLink = document.getElementById('contactEmail').querySelector('.contact-link');
        emailLink.href = `mailto:${venue.contactEmail}`;
        emailLink.textContent = venue.contactEmail;
    }

    // 官網
    if (venue.url) {
        showElement('venueUrl');
        const urlLink = document.getElementById('venueUrl').querySelector('.contact-link');
        urlLink.href = venue.url;

        // 官網按鈕
        showElement('websiteBtn');
        document.getElementById('websiteBtn').href = venue.url;
    }
}

// ===== 渲染會議室列表 =====
function renderRooms(venue) {
    const roomsGrid = document.getElementById('roomsGrid');
    const noRoomsState = document.getElementById('noRoomsState');
    const roomsCount = document.getElementById('roomsCount');

    const rooms = venue.rooms || [];

    // 過濾下架的會議室
    const activeRooms = rooms.filter(room => room.isActive !== false);

    // 計算隱藏的會議室數量
    const hiddenRoomsCount = rooms.length - activeRooms.length;

    if (activeRooms.length === 0) {
        showElement(noRoomsState);
        roomsCount.textContent = `(${rooms.length} 間)`;
        return;
    }

    // 顯示總數（包含隱藏的）
    roomsCount.textContent = `(${activeRooms.length}${hiddenRoomsCount > 0 ? ` +${hiddenRoomsCount} 隱藏` : ''} 間)`;

    activeRooms.forEach(room => {
        const card = createRoomCard(room, venue.id);
        roomsGrid.appendChild(card);
    });
}

// ===== 創建會議室卡片 =====
function createRoomCard(room, venueId) {
    const card = document.createElement('div');
    card.className = 'bg-surface-container-lowest rounded-xl overflow-hidden group border border-surface-container-high hover:border-primary transition-all cursor-pointer';
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

    // 容納人數
    let capacityText = '-';
    if (room.capacity) {
        const min = Math.min(room.capacity.theater || Infinity, room.capacity.classroom || Infinity, room.capacity.ushape || Infinity);
        const max = Math.max(room.capacity.theater || 0, room.capacity.classroom || 0, room.capacity.ushape || 0);
        if (min !== Infinity && max > 0) {
            capacityText = min === max ? `${min} 人` : `${min}-${max} 人`;
        }
    }

    // 價格
    let priceHtml = '<span class="text-sm text-outline">起價</span><p class="text-2xl font-bold text-primary">價格面議</p>';
    if (room.pricing) {
        if (room.pricing.halfDay && room.pricing.fullDay) {
            priceHtml = `<span class="text-sm text-outline">起價</span><p class="text-2xl font-bold text-primary">NT$ ${room.pricing.halfDay.toLocaleString()} <span class="text-xs font-normal text-on-surface-variant">- NT$ ${room.pricing.fullDay.toLocaleString()}</span></p>`;
        } else if (room.pricing.fullDay) {
            priceHtml = `<span class="text-sm text-outline">起價</span><p class="text-2xl font-bold text-primary">NT$ ${room.pricing.fullDay.toLocaleString()} <span class="text-xs font-normal text-on-surface-variant">/天</span></p>`;
        } else if (room.pricing.halfDay) {
            priceHtml = `<span class="text-sm text-outline">起價</span><p class="text-2xl font-bold text-primary">NT$ ${room.pricing.halfDay.toLocaleString()} <span class="text-xs font-normal text-on-surface-variant">/半天</span></p>`;
        } else if (room.pricing.note) {
            priceHtml = `<span class="text-sm text-outline">起價</span><p class="text-2xl font-bold text-primary">${room.pricing.note}</p>`;
        }
    }

    // 描述
    const description = room.description || room.name || '';

    // 圖片區域
    const imageHtml = imageUrl
        ? `<div class="h-64 overflow-hidden relative"><img src="${imageUrl}" alt="${room.name}" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" onerror="this.parentElement.innerHTML='<div class=\\'w-full h-full bg-surface-container flex items-center justify-center text-4xl\\'>🚪</div>'">${room.floor ? `<div class="absolute top-4 right-4 bg-primary text-on-primary px-3 py-1 rounded-full text-xs font-bold">${room.floor}</div>` : ''}</div>`
        : `<div class="h-64 bg-surface-container flex items-center justify-center text-4xl relative">${room.floor ? `<div class="absolute top-4 right-4 bg-primary text-on-primary px-3 py-1 rounded-full text-xs font-bold">${room.floor}</div>` : ''}🚪</div>`;

    card.innerHTML = `
        ${imageHtml}
        <div class="p-8 space-y-6">
            <div>
                <h3 class="text-2xl font-bold mb-2">${room.name}</h3>
                ${description ? `<p class="text-on-surface-variant text-sm line-clamp-2">${description}</p>` : ''}
            </div>
            <div class="flex justify-between items-center py-4 border-y border-surface-container-high">
                <div class="text-center">
                    <p class="text-xs text-outline font-bold uppercase mb-1">面積</p>
                    <p class="font-bold">${room.area ? room.area + ' 坪' : '-'}</p>
                </div>
                <div class="text-center">
                    <p class="text-xs text-outline font-bold uppercase mb-1">容納</p>
                    <p class="font-bold">${capacityText}</p>
                </div>
                <div class="text-center">
                    <p class="text-xs text-outline font-bold uppercase mb-1">挑高</p>
                    <p class="font-bold">${room.ceilingHeight ? room.ceilingHeight + ' 米' : '-'}</p>
                </div>
            </div>
            <div class="flex justify-between items-center">
                <div>
                    ${priceHtml}
                </div>
                <button class="bg-surface-container-highest p-4 rounded-full text-primary hover:bg-primary hover:text-on-primary transition-all">
                    <span class="material-symbols-outlined">chevron_right</span>
                </button>
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
    hideElement('loadingState');
    showElement('errorState');
    document.getElementById('errorState').querySelector('h3').textContent = message;
}

// ===== 渲染相簿照片 =====
function renderGallery(venue) {
    const gallerySection = document.getElementById('gallerySection');
    const galleryContainer = document.getElementById('venueGallery');

    // 檢查是否有 gallery 照片
    const gallery = venue.images?.gallery;

    if (!gallery || !Array.isArray(gallery) || gallery.length === 0) {
        hideElement(gallerySection);
        return;
    }

    // 顯示相簿區域
    showElement(gallerySection);

    // 清空容器
    galleryContainer.innerHTML = '';

    // 添加照片
    gallery.forEach((photoUrl, index) => {
        const photoDiv = document.createElement('div');
        photoDiv.className = 'aspect-[4/3] rounded-xl overflow-hidden bg-surface-container';

        const img = document.createElement('img');
        img.src = photoUrl;
        img.alt = `${venue.name} - 照片 ${index + 1}`;
        img.loading = 'lazy';
        img.className = 'w-full h-full object-cover hover:scale-105 transition-transform duration-300';

        // 錯誤處理：如果圖片載入失敗，隱藏該照片
        img.onerror = function() {
            hideElement(photoDiv);
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
    if (!risks || typeof risks !== 'object') { hideElement(section); return; }

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

    if (items.length === 0) { hideElement(section); return; }

    showElement(section);
    container.innerHTML = items.map(item => `
        <div class="bg-surface-container-lowest rounded-xl p-4 flex items-start gap-4">
            <div class="text-2xl">${item.icon}</div>
            <div>
                <div class="text-sm text-on-surface-variant mb-1">${item.label}</div>
                <div class="font-medium text-on-surface">${item.value}</div>
            </div>
        </div>
    `).join('');
}

// ===== 渲染專業知識 =====
function renderPricingTips(venue) {
    const section = document.getElementById('pricingTipsSection');
    const container = document.getElementById('pricingTipsContent');
    const tips = venue.pricingTips;
    if (!tips || !Array.isArray(tips) || tips.length === 0) { hideElement(section); return; }

    showElement(section);
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
    if (!rules || typeof rules !== 'object') { hideElement(section); return; }

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

    if (items.length === 0) { hideElement(section); return; }

    showElement(section);
    container.innerHTML = items.map(item => `
        <div class="bg-surface-container-lowest rounded-xl p-4 flex items-start gap-4">
            <div class="text-2xl">${item.icon}</div>
            <div>
                <div class="text-sm text-on-surface-variant mb-1">${item.label}</div>
                <div class="font-medium text-on-surface">${item.value}</div>
            </div>
        </div>
    `).join('');
}
