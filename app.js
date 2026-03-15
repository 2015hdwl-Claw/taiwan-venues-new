// ===== 全局變數 =====
let allVenues = [];
let filteredVenues = [];
let currentPage = 0;
const ITEMS_PER_PAGE = 20;

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', async () => {
    await loadVenues();
    initializeFilters();
    renderVenues();
});

// ===== 載入場地資料 =====
async function loadVenues() {
    try {
        const response = await fetch('venues.json');
        if (!response.ok) throw new Error('無法載入資料');
        
        allVenues = await response.json();
        filteredVenues = [...allVenues];
        
        // 更新統計
        document.getElementById('totalVenues').textContent = allVenues.length;
        document.getElementById('resultCount').textContent = allVenues.length;
        
        console.log(`✅ 成功載入 ${allVenues.length} 個場地`);
    } catch (error) {
        console.error('載入場地失敗:', error);
        showError('無法載入場地資料，請稍後再試');
    } finally {
        // 隱藏載入狀態
        document.getElementById('loadingState').style.display = 'none';
    }
}

// ===== 初始化篩選器 =====
function initializeFilters() {
    // 取得所有城市
    const cities = [...new Set(allVenues.map(v => v.city))].sort();
    const citySelect = document.getElementById('cityFilter');
    cities.forEach(city => {
        if (city) {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        }
    });

    // 取得所有場地類型
    const types = [...new Set(allVenues.map(v => v.venueType))].sort()
    const typeSelect = document.getElementById('typeFilter');
    types.forEach(type => {
        if (type) {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            typeSelect.appendChild(option);
        }
    });
}

// ===== 搜尋功能 =====
function handleSearch(event) {
    if (event.key === 'Enter') {
        performSearch();
    }
}

function performSearch() {
    applyFilters();
}

// ===== 應用篩選 =====
function applyFilters() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    const city = document.getElementById('cityFilter').value;
    const type = document.getElementById('typeFilter').value;
    const capacity = document.getElementById('capacityFilter').value;
    const price = document.getElementById('priceFilter').value

    filteredVenues = allVenues.filter(venue => {
        // 搜尋關鍵字
        if (searchTerm) {
            const searchFields = [
                venue.name,
                venue.address,
                venue.city,
                venue.venueType
            ].filter(Boolean).join(' ').toLowerCase();
            
            if (!searchFields.includes(searchTerm)) {
                return false;
            }
        }

        // 城市篩選
        if (city && venue.city !== city) {
            return false;
        }

        // 類型篩選
        if (type && venue.venueType !== type) {
            return false;
        }

        // 容納人數篩選
        if (capacity) {
            const maxCapacity = venue.maxCapacityTheater || venue.maxCapacityClassroom || 0;
            const cap = parseInt(capacity);
            
            if (cap === 1000) {
                if (maxCapacity < 1000) return false;
            } else {
                if (maxCapacity > cap) return false;
            }
        }

        // 價格篩選
        if (price) {
            const minPrice = venue.priceHalfDay || venue.priceFullDay || 0;
            if (minPrice > parseInt(price)) {
                return false;
            }
        }

        return true;
    });

    // 重置頁碼
    currentPage = 0;
    
    // 重新渲染
    renderVenues();
    
    // 更新結果計數
    document.getElementById('resultCount').textContent = filteredVenues.length;
}

// ===== 清除篩選 =====
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('cityFilter').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('capacityFilter').value = '';
    document.getElementById('priceFilter').value = '';
    
    filteredVenues = [...allVenues];
    currentPage = 0;
    renderVenues();
    document.getElementById('resultCount').textContent = filteredVenues.length;
}

// ===== 渲染場地列表 =====
function renderVenues() {
    const grid = document.getElementById('venuesGrid');
    const emptyState = document.getElementById('emptyState');
    const loadMoreSection = document.getElementById('loadMoreSection');
    
    // 清空現有內容
    grid.innerHTML = '';
    
    // 檢查是否有結果
    if (filteredVenues.length === 0) {
        emptyState.style.display = 'block';
        loadMoreSection.style.display = 'none';
        return;
    }
    
    emptyState.style.display = 'none';
    
    // 取得當前頁面的場地
    const startIndex = 0;
    const endIndex = (currentPage + 1) * ITEMS_PER_PAGE;
    const venuesToShow = filteredVenues.slice(startIndex, endIndex);
    
    // 渲染場地卡片
    venuesToShow.forEach(venue => {
        const card = createVenueCard(venue);
        grid.appendChild(card);
    });
    
    // 顯示/隱藏載入更多按鈕
    if (endIndex < filteredVenues.length) {
        loadMoreSection.style.display = 'block';
    } else {
        loadMoreSection.style.display = 'none';
    }
}

// ===== 創建場地卡片 =====
function createVenueCard(venue) {
    const card = document.createElement('div');
    card.className = 'venue-card';
    card.onclick = () => {
        window.location.href = `venue.html?id=${venue.id}`;
    }
    
    const imageUrl = venue.images?.main || 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800';
    const priceText = venue.priceHalfDay 
        ? `半天 $${venue.priceHalfDay.toLocaleString()} 起`
        : (venue.priceFullDay 
            ? `全天 $${venue.priceFullDay.toLocaleString()} 起`
            : '價格面議');
    
    const capacityText = venue.maxCapacityTheater 
        ? `最多 ${venue.maxCapacityTheater} 人`
        : (venue.maxCapacityClassroom 
            ? `最多 ${venue.maxCapacityClassroom} 人`
            : '人數未提供');
    
    // 會議室數量
    const roomsCount = venue.rooms ? venue.rooms.length : 0;
    
    card.innerHTML = `
        <img src="${imageUrl}" alt="${venue.name}" class="venue-image" 
             onerror="this.src='https://images.unsplash.com/photo-1497366216548-37526070297c?w=800'">
        <div class="venue-content">
            <span class="venue-type">${venue.venueType || '場地'}</span>
            <h3 class="venue-name">${venue.name}</h3>
            <div class="venue-info">
                <div class="venue-info-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                        <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    <span>${venue.city || '未知城市'}</span>
                </div>
                <div class="venue-info-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                        <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    <span>${venue.address || '地址未提供'}</span>
                </div>
            </div>
            <div class="venue-footer">
                <span class="venue-price">${priceText}</span>
                <span class="venue-capacity">${capacityText}</span>
                ${roomsCount > 0 ? `<span class="venue-rooms">🚪 ${roomsCount} 間會議室</span>` : ''}
            </div>
        </div>
    `;
    
    return card
}

// ===== 載入更多 =====
function loadMore() {
    currentPage++;
    renderVenues();
    
    // 滾動到新內容
    const grid = document.getElementById('venuesGrid');
    const cards = grid.querySelectorAll('.venue-card');
    if (cards.length > ITEMS_PER_PAGE * currentPage) {
        cards[ITEMS_PER_PAGE * currentPage].scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ===== 顯示場地詳情（Modal - 保留但改為跳轉） =====
function showVenueDetail(venue) {
    // 直接跳轉到 venue.html
    window.location.href = `venue.html?id=${venue.id}`;
}

// ===== 關閉 Modal =====
function closeModal() {
    const modal = document.getElementById('venueModal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// ===== 返回首頁 =====
function goHome() {
    clearFilters();
    window.location.href = 'index.html';
}

// ===== 顯示錯誤 =====
function showError(message) {
    const grid = document.getElementById('venuesGrid');
    grid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
            <div class="empty-icon">⚠️</div>
            <h3>${message}</h3>
            <button class="btn btn-primary" onclick="location.reload()">重新載入</button>
        </div>
    `;
}

// ===== 鍵盤快捷鍵 =====
document.addEventListener('keydown', (e) => {
    // ESC 關閉 Modal
    if (e.key === 'Escape') {
        closeModal();
    }
    
    // Ctrl/Cmd + K 聚焦搜尋框
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
    }
});

// ===== 點擊外部關閉 Modal =====
document.getElementById('venueModal').addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        closeModal();
    }
});
