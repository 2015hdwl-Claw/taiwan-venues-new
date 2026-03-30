/**
 * 活動大師 EventMaster - MVP JavaScript
 * 照片為主的會議室搜尋平台
 */

// 全域變數
let allVenues = [];
let filteredVenues = [];

// 格式化價格顯示
function formatPrice(price, priceType) {
    if (!price) return '未提供';
    if (typeof price === 'string') return price;
    if (priceType === 'note' && typeof price === 'string') return price;
    return `$${price.toLocaleString()}`;
}

// 載入場地資料
async function loadVenues() {
    try {
        const response = await fetch('mvp_venues_ready.json');
        if (!response.ok) throw new Error('無法載入場地資料');

        allVenues = await response.json();
        filteredVenues = [...allVenues];

        // 更新統計
        updateVenueCount();

        // 渲染場地列表
        renderVenues();

        console.log(`載入 ${allVenues.length} 個場地`);
    } catch (error) {
        console.error('載入場地資料失敗:', error);
        showError('無法載入場地資料，請重新整理頁面');
    }
}

// 更新場地數量
function updateVenueCount() {
    const countElement = document.getElementById('venue-count');
    if (countElement) {
        countElement.textContent = filteredVenues.length;
    }
}

// 渲染場地列表
function renderVenues() {
    const container = document.getElementById('venues-container');
    const noResults = document.getElementById('no-results');

    if (!container) return;

    // 清空容器
    container.innerHTML = '';

    // 如果沒有結果
    if (filteredVenues.length === 0) {
        if (noResults) noResults.style.display = 'block';
        return;
    }

    if (noResults) noResults.style.display = 'none';

    // 渲染每個場地卡片
    filteredVenues.forEach(venue => {
        const card = createVenueCard(venue);
        container.appendChild(card);
    });
}

// 創建場地卡片
function createVenueCard(venue) {
    const card = document.createElement('div');
    card.className = 'venue-card';
    card.onclick = () => showVenueDetail(venue);

    // 主照片
    const mainPhoto = venue.photos.main || '';

    // 場地類型標籤
    const typeTag = `<span class="tag tag-type">${venue.venueType}</span>`;

    // 行政區標籤
    const districtTag = `<span class="tag tag-district">${venue.tags.district}</span>`;

    // 容量和價格
    const capacity = venue.capacity || '未知';
    const price = formatPrice(venue.price, venue.priceType);
    const floor = venue.floor ? `${venue.floor} · ` : '';

    card.innerHTML = `
        <div class="card-photo">
            <img src="${mainPhoto}" alt="${venue.name}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\"http://www.w3.org/2000/svg\" width=\"400\" height=\"300\"%3E%3Crect fill=\"%23ddd\" width=\"400\" height=\"300\"/%3E%3Ctext fill=\"%23999\" font-family=\"sans-serif\" font-size=\"48\" dy=\".3em\" text-anchor=\"middle\" x=\"50%25\" y=\"50%25\"%3E無照片%3C/text%3E%3C/svg%3E'">
            <div class="card-tags">
                ${typeTag}
                ${districtTag}
            </div>
        </div>
        <div class="card-info">
            <h3 class="card-name">${venue.room_name}</h3>
            <p class="card-address">${venue.original_venue} · ${floor}${venue.address}</p>
            <div class="card-details">
                <span class="card-detail">
                    <span class="icon">👥</span>
                    ${capacity}人
                </span>
                <span class="card-detail">
                    <span class="icon">💰</span>
                    ${price}
                </span>
            </div>
        </div>
    `;

    return card;
}

// 顯示場地詳情
function showVenueDetail(venue) {
    const modal = document.getElementById('venue-modal');
    const modalBody = document.getElementById('modal-body');

    if (!modal || !modalBody) return;

    // 照片庫
    const mainPhoto = venue.photos.main || '';
    const galleryPhotos = venue.photos.gallery || [];

    let galleryHTML = '';
    if (galleryPhotos.length > 0) {
        galleryHTML = '<div class="detail-gallery">';
        galleryPhotos.forEach(photo => {
            galleryHTML += `
                <img
                    src="${photo}"
                    alt="${venue.name}"
                    onerror="this.style.display='none'"
                >
            `;
        });
        galleryHTML += '</div>';
    }

    // 面積與尺寸資訊
    const areaInfo = venue.area ?
        `<p><strong>面積：</strong>${venue.area} ${venue.areaUnit || '㎡'}</p>` : '';

    const dimensionsInfo = venue.dimensions && venue.dimensions.length && venue.dimensions.width ?
        `<p><strong>尺寸：</strong>長 ${venue.dimensions.length}m × 寬 ${venue.dimensions.width}m × 高 ${venue.dimensions.height}m</p>` : '';

    const floorInfo = venue.floor ?
        `<p><strong>樓層：</strong>${venue.floor}</p>` : '';

    const capacityTypeInfo = venue.capacityType ?
        `<p><strong>容量類型：</strong>${venue.capacityType}</p>` : '';

    modalBody.innerHTML = `
        <div class="detail-header">
            <h2>${venue.room_name}</h2>
            <p style="font-size: 16px; color: #666; margin: 5px 0 10px;">${venue.original_venue}</p>
            <span class="tag tag-type">${venue.venueType}</span>
        </div>

        <div class="detail-content">
            <div class="detail-main-photo">
                <img src="${mainPhoto}" alt="${venue.name}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\"http://www.w3.org/2000/svg\" width=\"800\" height=\"400\"%3E%3Crect fill=\"%23ddd\" width=\"800\" height=\"400\"/%3E%3Ctext fill=\"%23999\" font-family=\"sans-serif\" font-size=\"48\" dy=\".3em\" text-anchor=\"middle\" x=\"50%25\" y=\"50%25\"%3E無照片%3C/text%3E%3C/svg%3E'">
            </div>

            ${galleryHTML}

            <div class="detail-info">
                <h3>基本資訊</h3>
                <p><strong>場地：</strong>${venue.original_venue}</p>
                <p><strong>會議室：</strong>${venue.room_name}</p>
                <p><strong>地址：</strong>${venue.address}</p>
                ${floorInfo}
                <p><strong>容量：</strong>${venue.capacity} 人</p>
                ${capacityTypeInfo}
                ${areaInfo}
                ${dimensionsInfo}
                <p><strong>價格：</strong>${formatPrice(venue.price, venue.priceType)}</p>

                <h3>標籤</h3>
                <p><strong>行政區：</strong>${venue.tags.district}</p>
                <p><strong>容量等級：</strong>${venue.tags.capacity_level}</p>
                <p><strong>價格等級：</strong>${venue.tags.price_level}</p>

                ${venue.contact && venue.contact.phone ? `<p><strong>電話：</strong>${venue.contact.phone}</p>` : ''}
                ${venue.contact && venue.contact.email ? `<p><strong>Email：</strong>${venue.contact.email}</p>` : ''}
                ${venue.url ? `<p><strong>官網：</strong><a href="${venue.url}" target="_blank">${venue.url}</a></p>` : ''}
            </div>
        </div>
    `;

    modal.style.display = 'block';
}

// 關閉 Modal
function closeVenueModal() {
    const modal = document.getElementById('venue-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 篩選場地
function filterVenues() {
    const searchText = document.getElementById('search-input').value.toLowerCase();
    const district = document.getElementById('district-filter').value;
    const capacity = document.getElementById('capacity-filter').value;
    const price = document.getElementById('price-filter').value;

    filteredVenues = allVenues.filter(venue => {
        // 搜尋文字
        if (searchText) {
            const nameMatch = venue.name.toLowerCase().includes(searchText);
            const addressMatch = venue.address.toLowerCase().includes(searchText);
            if (!nameMatch && !addressMatch) return false;
        }

        // 行政區
        if (district && venue.tags.district !== district) {
            return false;
        }

        // 容量
        if (capacity && venue.tags.capacity_level !== capacity) {
            return false;
        }

        // 價格
        if (price && venue.tags.price_level !== price) {
            return false;
        }

        return true;
    });

    updateVenueCount();
    renderVenues();
}

// 重設篩選
function resetFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('district-filter').value = '';
    document.getElementById('capacity-filter').value = '';
    document.getElementById('price-filter').value = '';

    filterVenues();
}

// 顯示錯誤
function showError(message) {
    const container = document.getElementById('venues-container');
    if (container) {
        container.innerHTML = `
            <div class="error-message">
                <p>${message}</p>
            </div>
        `;
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 載入場地資料
    loadVenues();

    // 設置事件監聽器
    document.getElementById('search-input').addEventListener('input', filterVenues);
    document.getElementById('district-filter').addEventListener('change', filterVenues);
    document.getElementById('capacity-filter').addEventListener('change', filterVenues);
    document.getElementById('price-filter').addEventListener('change', filterVenues);
    document.getElementById('reset-filters').addEventListener('click', resetFilters);

    // Modal 關閉按鈕
    const closeBtn = document.querySelector('.modal-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeVenueModal);
    }

    // 點擊 Modal 外部關閉
    const modal = document.getElementById('venue-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeVenueModal();
            }
        });
    }

    // ESC 鍵關閉 Modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeVenueModal();
        }
    });
});
