// ===== 全局變數 =====
let allVenues = [];
let currentVenue = null;

// ===== 版本控制 =====
const DATA_VERSION = '20260323-v4'; // 與 app.js 保持同步

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
    
    // 尋找場地
    currentVenue = allVenues.find(v => v.id === parseInt(venueId));
    
    if (!currentVenue) {
        showError('找不到此場地');
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
    
    // 優先使用官網照片（支援多種格式）
    // 格式1: {"main": "url", "source": "url"}
    // 格式2: ["url1", "url2"]
    // 格式3: photo: "url"
    let imageUrl = null;
    if (room.images && typeof room.images === 'object' && room.images.main) {
        // 字典格式，优先使用 main
        imageUrl = room.images.main;
    } else if (Array.isArray(room.images) && room.images.length > 0) {
        // 数组格式，使用第一张
        imageUrl = room.images[0];
    } else if (room.photo) {
        // 旧格式 photo 字段
        imageUrl = room.photo;
    }
    
    // 容納人數
    let capacityText = '-';
    if (room.capacity) {
        const caps = [];
        if (room.capacity.theater) caps.push(`劇院${room.capacity.theater}`);
        if (room.capacity.classroom) caps.push(`課桌${room.capacity.classroom}`);
        if (room.capacity.ushape) caps.push(`U型${room.capacity.ushape}`);
        capacityText = caps.join(' / ') || '-';
    }
    
    // 價格
    let priceText = '價格面議';
    if (room.pricing) {
        if (room.pricing.fullDay) {
            priceText = `$${room.pricing.fullDay.toLocaleString()}/天`;
        } else if (room.pricing.halfDay) {
            priceText = `$${room.pricing.halfDay.toLocaleString()}/半天`;
        }
    }
    
    // 設備
    let equipmentText = '基本設備';
    if (room.equipment && room.equipment.length > 0) {
        equipmentText = room.equipment.slice(0, 3).join('、');
        if (room.equipment.length > 3) {
            equipmentText += ` 等${room.equipment.length}項`;
        }
    }
    
    // 空間資訊標籤（新增）
    let spaceTags = [];
    if (room.shape) {
        spaceTags.push(room.shape);
    }
    if (room.height) {
        spaceTags.push(`挑高${room.height}公尺`);
    }
    if (room.pillar !== undefined) {
        spaceTags.push(room.pillar ? '有柱' : '無柱');
    }
    const spaceTagsText = spaceTags.length > 0 ? spaceTags.join(' · ') : '';
    
    // 圖片區域（如果有有效的官網圖片才顯示）
    const imageHtml = imageUrl
        ? `<img src="${imageUrl}" alt="${room.name}" class="room-card-image"
             onerror="this.parentElement.style.display='none'">`
        : '';

    card.innerHTML = `
        ${imageHtml}
        <div class="room-card-content">
            <h3 class="room-card-name">${room.name}</h3>
            <div class="room-card-info">
                <span class="room-card-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    </svg>
                    ${room.area ? room.area + ' 坪' : '坪數未提供'}
                </span>
                <span class="room-card-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                        <circle cx="9" cy="7" r="4"></circle>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                    </svg>
                    ${capacityText}
                </span>
            </div>
            ${spaceTagsText ? `<div class="room-card-space-tags">${spaceTagsText}</div>` : ''}
            <div class="room-card-footer">
                <span class="room-card-price">${priceText}</span>
                <span class="room-card-equipment">${equipmentText}</span>
            </div>
            <button class="room-card-btn">查看詳情 →</button>
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
            this.parentElement.style.display = 'none';
        };

        photoDiv.appendChild(img);
        galleryContainer.appendChild(photoDiv);
    });
}
