// ===== 全局變數 =====
let allVenues = [];
let filteredVenues = [];
let currentPage = 0;
const ITEMS_PER_PAGE = 20;

// ===== 版本控制（每次部署更新此值）=====
const DATA_VERSION = '20260323-v2'; // 格式: YYYYMMDD-序號

// ===== 排序權重定義 =====
// 縣市排序（按場地數量降冪，前3名標記為熱門）
const CITY_ORDER = [
  { name: '台北市', weight: 100, hot: true },
  { name: '台中市', weight: 95, hot: true },
  { name: '高雄市', weight: 90, hot: true },
  { name: '新北市', weight: 85, hot: false },
  { name: '台南市', weight: 80, hot: false },
  { name: '桃園市', weight: 75, hot: false },
  { name: '屏東縣', weight: 70, hot: false },
  { name: '南投縣', weight: 65, hot: false },
  { name: '宜蘭縣', weight: 60, hot: false },
  { name: '新竹市', weight: 55, hot: false },
  { name: '彰化縣', weight: 50, hot: false },
  { name: '花蓮縣', weight: 45, hot: false },
  { name: '台東縣', weight: 40, hot: false },
  { name: '臺東縣', weight: 40, hot: false }, // 繁體字版本
  { name: '苗栗縣', weight: 35, hot: false },
  { name: '雲林縣', weight: 30, hot: false },
  { name: '嘉義市', weight: 25, hot: false },
  { name: '新竹縣', weight: 20, hot: false },
  { name: '澎湖縣', weight: 15, hot: false },
  { name: '連江縣', weight: 10, hot: false },
  { name: '金門縣', weight: 5, hot: false },
  { name: '嘉義縣', weight: 3, hot: false },
  { name: '基隆市', weight: 1, hot: false }
];

// 類型排序（按場地數量降冪，前2名標記為熱門）
const TYPE_ORDER = [
  { name: '飯店場地', weight: 100, hot: true },
  { name: '會議中心', weight: 90, hot: true },
  { name: '展演場地', weight: 70, hot: false },
  { name: '機關場地', weight: 60, hot: false },
  { name: '運動場地', weight: 50, hot: false },
  { name: '婚宴場地', weight: 40, hot: false },
  { name: '咖啡廳', weight: 20, hot: false },
  { name: '宴會廳', weight: 15, hot: false },
  { name: '其他', weight: 10, hot: false }
];

// 建立快速查找的 Map
const CITY_WEIGHT_MAP = new Map(CITY_ORDER.map(c => [c.name, c]));
const TYPE_WEIGHT_MAP = new Map(TYPE_ORDER.map(t => [t.name, t]));

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', async () => {
    await loadVenues();
    initializeFilters();
    renderVenues();
});

// ===== 載入場地資料 =====
async function loadVenues() {
    try {
        // 添加版本參數防止快取
        const response = await fetch(`venues.json?v=${DATA_VERSION}`);
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

// ===== 初始化篩選器（智慧排序）=====
function initializeFilters() {
    // 統計縣市數量
    const cityStats = new Map();
    allVenues.forEach(v => {
        if (v.city) {
            cityStats.set(v.city, (cityStats.get(v.city) || 0) + 1);
        }
    });
    
    // 按權重排序縣市
    const cities = [...new Set(allVenues.map(v => v.city))]
        .filter(Boolean)
        .sort((a, b) => {
            const weightA = CITY_WEIGHT_MAP.get(a)?.weight || 0;
            const weightB = CITY_WEIGHT_MAP.get(b)?.weight || 0;
            return weightB - weightA;
        });
    
    const citySelect = document.getElementById('cityFilter');
    cities.forEach(city => {
        const option = document.createElement('option');
        option.value = city;
        const cityInfo = CITY_WEIGHT_MAP.get(city);
        const count = cityStats.get(city);
        option.textContent = cityInfo?.hot ? `${city} 🔥` : city;
        option.setAttribute('data-count', count);
        citySelect.appendChild(option);
    });

    // 統計類型數量
    const typeStats = new Map();
    allVenues.forEach(v => {
        if (v.venueType) {
            typeStats.set(v.venueType, (typeStats.get(v.venueType) || 0) + 1);
        }
    });
    
    // 按權重排序類型
    const types = [...new Set(allVenues.map(v => v.venueType))]
        .filter(Boolean)
        .sort((a, b) => {
            const weightA = TYPE_WEIGHT_MAP.get(a)?.weight || 0;
            const weightB = TYPE_WEIGHT_MAP.get(b)?.weight || 0;
            return weightB - weightA;
        });
    
    const typeSelect = document.getElementById('typeFilter');
    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        const typeInfo = TYPE_WEIGHT_MAP.get(type);
        const count = typeStats.get(type);
        option.textContent = typeInfo?.hot ? `${type} 🔥` : type;
        option.setAttribute('data-count', count);
        typeSelect.appendChild(option);
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
    const price = document.getElementById('priceFilter').value;

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

    // 智慧排序
    sortVenues();
    
    // 重置頁碼
    currentPage = 0;
    
    // 重新渲染
    renderVenues();
    
    // 更新結果計數
    document.getElementById('resultCount').textContent = filteredVenues.length;
}

// ===== 智慧排序 =====
function sortVenues() {
    filteredVenues.sort((a, b) => {
        // 計算權重
        const cityWeightA = CITY_WEIGHT_MAP.get(a.city)?.weight || 0;
        const cityWeightB = CITY_WEIGHT_MAP.get(b.city)?.weight || 0;
        
        const typeWeightA = TYPE_WEIGHT_MAP.get(a.venueType)?.weight || 0;
        const typeWeightB = TYPE_WEIGHT_MAP.get(b.venueType)?.weight || 0;
        
        const totalWeightA = cityWeightA + typeWeightA;
        const totalWeightB = cityWeightB + typeWeightB;
        
        // 降冪排序
        return totalWeightB - totalWeightA;
    });
}

// ===== 清除篩選 =====
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('cityFilter').value = '';
    document.getElementById('typeFilter').value = '';
    document.getElementById('capacityFilter').value = '';
    document.getElementById('priceFilter').value = '';
    
    filteredVenues = [...allVenues];
    sortVenues(); // 重新排序
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
    
    // 移除最大容量顯示（因為容納人數已有）
    // const capacityText = venue.maxCapacityTheater 
    //     ? `最多 ${venue.maxCapacityTheater} 人`
    //     : (venue.maxCapacityClassroom 
    //         ? `最多 ${venue.maxCapacityClassroom} 人`
    //         : '人數未提供');
    const capacityText = '';
    
    // 檢查是否為熱門縣市/類型
    const cityInfo = CITY_WEIGHT_MAP.get(venue.city);
    const typeInfo = TYPE_WEIGHT_MAP.get(venue.venueType);
    const isHot = cityInfo?.hot || typeInfo?.hot;
    
    // 會議室數量
    const roomsCount = venue.rooms ? venue.rooms.length : 0;
    
    // 構建標籤
    const tags = [];
    if (cityInfo?.hot) tags.push('🔥');
    if (typeInfo?.hot && !cityInfo?.hot) tags.push('🔥');
    
    card.innerHTML = `
        <img src="${imageUrl}" alt="${venue.name}" class="venue-image" 
             onerror="this.src='https://images.unsplash.com/photo-1497366216548-37526070297c?w=800'">
        <div class="venue-content">
            <span class="venue-type ${isHot ? 'hot' : ''}">${tags.length > 0 ? tags[0] + ' ' : ''}${venue.venueType || '場地'}</span>
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
                    <span class="address-text">${venue.address || '地址未提供'}</span>
                </div>
            </div>
            <div class="venue-footer">
                <span class="venue-price">${priceText}</span>
                <span class="venue-capacity" style="display: none;">${capacityText}</span>
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
