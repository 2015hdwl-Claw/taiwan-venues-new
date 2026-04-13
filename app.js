// ===== 全局變數 =====
let allVenues = [];
let filteredVenues = [];
let currentPage = 0;
const ITEMS_PER_PAGE = 20;

// ===== 版本控制（每次部署更新此值）=====
const DATA_VERSION = '20260413-v31'; // 格式: YYYYMMDD-序號

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
            return url;
        }
    }

    // 2. 從 gallery 中尋找飯店照片（外觀/大廳）
    for (const url of gallery) {
        if (isHotelPhoto(url) && !isRoomPhoto(url)) {
            return url;
        }
    }

    // 3. 從活躍會議室中尋找照片
    const activeRooms = rooms.filter(r => r.isActive !== false);
    for (const room of activeRooms) {
        const roomImages = room.images || {};
        if (roomImages.main) {
            return roomImages.main;
        }
        if (Array.isArray(roomImages.gallery) && roomImages.gallery.length > 0) {
            return roomImages.gallery[0];
        }
    }

    // 4. 從 gallery 中尋找第一個非房間照片
    for (const url of gallery) {
        if (!isRoomPhoto(url)) {
            return url;
        }
    }

    // 5. 最後才使用主照片
    return images.main || null;
}

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

// ===== Mobile Navigation Toggle =====
function toggleNav() {
    const mobileNav = document.getElementById('mobileNav');
    if (mobileNav) {
        mobileNav.classList.toggle('hidden');
    }
}

// ===== 載入場地資料 =====
async function loadVenues() {
    try {
        // 載入主資料庫
        const response = await fetch(`venues.json?v=${DATA_VERSION}`);
        if (!response.ok) throw new Error('無法載入資料');

        allVenues = await response.json();
        // 過濾：僅啟用的場地（不限城市）
        allVenues = allVenues.filter(venue => venue.active !== false);
        filteredVenues = [...allVenues];
        
        // 更新統計 (B2B 版本使用 class，向後兼容)
        const venueCountEl = document.getElementById('totalVenues');
        if (venueCountEl) {
            venueCountEl.textContent = allVenues.length;
        } else {
            // B2B 版本：更新第一個 stat-number
            const statNumbers = document.querySelectorAll('.stat-number');
            if (statNumbers.length > 0) {
                statNumbers[0].textContent = allVenues.length + '+';
            }
        }

        const resultCountEl = document.getElementById('resultCount');
        if (resultCountEl) {
            resultCountEl.textContent = allVenues.length;
        }

        // Update hero venue count
        const heroVenueCountEl = document.getElementById('heroVenueCount');
        if (heroVenueCountEl) {
            heroVenueCountEl.textContent = allVenues.length + '+';
        }
        
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
    const priceFilter = document.getElementById('priceFilter');
    const price = priceFilter ? priceFilter.value : '';

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
        if (loadMoreSection) loadMoreSection.style.display = 'none';
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
    if (loadMoreSection) {
        if (endIndex < filteredVenues.length) {
            loadMoreSection.style.display = 'block';
        } else {
            loadMoreSection.style.display = 'none';
        }
    }
}

// ===== 創建場地卡片 =====
function createVenueCard(venue) {
    const card = document.createElement('div');
    card.className = 'group cursor-pointer';
    card.onclick = () => {
        window.location.href = `venue.html?id=${venue.id}`;
    }

    // 使用智能照片選擇
    const imageUrl = selectVenueMainImage(venue) || 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800';

    // 區域簡稱
    const district = venue.address ? venue.address.split('區')[0] + '區' : (venue.city || '台北市');

    // 價格顯示 (顯示半天價)
    let priceHtml = '<span class="text-on-surface-variant text-xs block">面議</span>';
    if (venue.priceHalfDay) {
        priceHtml = `<span class="text-primary font-bold text-lg">$${venue.priceHalfDay.toLocaleString()}</span><span class="text-on-surface-variant text-xs block">/ 半天</span>`;
    } else if (venue.priceFullDay) {
        priceHtml = `<span class="text-primary font-bold text-lg">$${venue.priceFullDay.toLocaleString()}</span><span class="text-on-surface-variant text-xs block">/ 全天</span>`;
    }

    // 場地類型標籤
    const typeBadges = {
        '飯店': { text: '高端會議', color: 'bg-primary/90' },
        '會議中心': { text: '精選熱門', color: 'bg-primary/90' },
        '展演': { text: '藝文首選', color: 'bg-primary/90' },
        '婚宴': { text: '熱門推薦', color: 'bg-primary/90' }
    };
    const badge = typeBadges[venue.venueType] || { text: '精選場地', color: 'bg-primary/90' };

    card.innerHTML = `
        <div class="aspect-[4/3] rounded-3xl overflow-hidden mb-6 relative border-2 border-transparent group-hover:border-primary-container transition-all duration-500">
            <img src="${imageUrl}" alt="${venue.name} 會議室"
                 class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                 onerror="this.src='https://images.unsplash.com/photo-1497366216548-37526070297c?w=800'">
            <div class="absolute top-4 left-4">
                <span class="${badge.color} text-white text-xs font-bold px-4 py-2 rounded-full backdrop-blur-sm">${badge.text}</span>
            </div>
        </div>
        <div class="flex justify-between items-start">
            <div>
                <h4 class="text-xl font-bold text-on-surface group-hover:text-primary transition-colors">${venue.name}</h4>
                <p class="text-on-surface-variant flex items-center gap-1 mt-1 text-sm">
                    <span class="material-symbols-outlined text-[16px]">location_on</span> ${district}
                </p>
            </div>
            <div class="text-right">
                ${priceHtml}
            </div>
        </div>
    `;

    return card;
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
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
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
const venueModal = document.getElementById('venueModal');
if (venueModal) {
    venueModal.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            closeModal();
        }
    });
}

// ===== B2B 功能：反饋表單處理 =====
function submitFeedback(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const feedbackData = {
        profession: formData.get('profession'),
        frequency: formData.get('frequency'),
        concerns: formData.get('concerns'),
        email: formData.get('email'),
        timestamp: new Date().toISOString(),
        page: 'index'
    };

    // 儲存到 localStorage（實際應用中應發送到後端）
    const feedbacks = JSON.parse(localStorage.getItem('eventmaster_feedbacks') || '[]');
    feedbacks.push(feedbackData);
    localStorage.setItem('eventmaster_feedbacks', JSON.stringify(feedbacks));

    // 發送到 Google Analytics（如果可用）
    if (typeof gtag !== 'undefined') {
        gtag('event', 'submit_feedback', {
            'event_category': 'engagement',
            'event_label': feedbackData.profession
        });
    }

    // 顯示感謝訊息
    alert('感謝您的反饋！我們會認真考慮您的意見。');
    form.reset();

    // 可選：發送到後端 API
    // sendToBackend('/api/feedback', feedbackData);
}

// ===== B2B 功能：企業表單顯示 =====
function showEnterpriseForm(type) {
    const modal = document.getElementById('enterpriseModal');
    const typeInput = document.getElementById('enterpriseType');
    const title = document.getElementById('enterpriseModalTitle');
    const desc = document.getElementById('enterpriseModalDesc');

    // 設定表單類型
    typeInput.value = type;

    // 根據類型設定標題和描述
    switch(type) {
        case 'pr':
            title.textContent = '公關/活動公司服務洽詢';
            desc.textContent = '專業的場地知識平台，幫助您提升客戶滿意度';
            break;
        case 'corporate':
            title.textContent = '企業行銷團隊服務洽詢';
            desc.textContent = '快速找到符合品牌形象的專業場地';
            break;
        case 'planner':
            title.textContent = '活動策劃師服務洽詢';
            desc.textContent = '獲取專業場地知識庫和風險評估工具';
            break;
    }

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// ===== B2B 功能：關閉企業表單 =====
function closeEnterpriseModal() {
    const modal = document.getElementById('enterpriseModal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// ===== B2B 功能：提交企業表單 =====
function submitEnterpriseForm(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const enterpriseData = {
        type: formData.get('type'),
        companyName: formData.get('companyName'),
        contactPerson: formData.get('contactPerson'),
        email: formData.get('contactEmail'),
        phone: formData.get('contactPhone'),
        requirements: formData.get('requirements'),
        timestamp: new Date().toISOString()
    };

    // 儲存到 localStorage
    const inquiries = JSON.parse(localStorage.getItem('eventmaster_inquiries') || '[]');
    inquiries.push(enterpriseData);
    localStorage.setItem('eventmaster_inquiries', JSON.stringify(inquiries));

    // 發送到 Google Analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', 'submit_inquiry', {
            'event_category': 'lead_generation',
            'event_label': enterpriseData.type
        });
    }

    // 顯示感謝訊息
    alert('感謝您的洽詢！我們會盡快與您聯繫。');
    closeEnterpriseModal();
    form.reset();

    // 可選：發送到後端 API 或 Email
    // sendInquiryEmail(enterpriseData);
}

// ===== B2B 功能：Analytics 追蹤 =====
function trackEnterpriseEngagement() {
    // 追蹤專業功能查看
    const knowledgeLinks = document.querySelectorAll('[onclick*="viewAllKnowledge"]');
    knowledgeLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'view_knowledge', {
                    'event_category': 'enterprise_feature',
                    'event_label': 'professional_knowledge'
                });
            }
        });
    });

    // 追蹤場地比較功能
    const compareButtons = document.querySelectorAll('[onclick*="compareVenue"]');
    compareButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'compare_venues', {
                    'event_category': 'enterprise_feature',
                    'event_label': 'comparison_tool'
                });
            }
        });
    });
}

// ===== B2B 功能：資料收集分析 =====
function analyzeUserBehavior() {
    // 收集用戶行為數據
    const behaviorData = {
        visitTime: new Date().toISOString(),
        pagesViewed: [],
        searchesPerformed: 0,
        filtersUsed: [],
        venuesViewed: [],
        timeOnPage: 0
    };

    // 追蹤頁面停留時間
    let startTime = Date.now();
    window.addEventListener('beforeunload', () => {
        behaviorData.timeOnPage = Math.floor((Date.now() - startTime) / 1000);
        localStorage.setItem('eventmaster_behavior', JSON.stringify(behaviorData));
    });

    // 追蹤搜尋行為
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('change', () => {
            behaviorData.searchesPerformed++;
        });
    }
}

// ===== 初始化 B2B 功能 =====
document.addEventListener('DOMContentLoaded', () => {
    // 啟用分析功能
    analyzeUserBehavior();

    // 延遲啟用功能追蹤（確保 DOM 完全載入）
    setTimeout(() => {
        trackEnterpriseEngagement();
    }, 1000);
});

// ===== B2B 功能：風險等級計算 =====
function calculateRiskLevel(venue) {
    let riskScore = 0;
    let riskFactors = [];

    // 檢查各種風險因素
    if (venue.priceHalfDay > 50000) {
        riskScore += 2;
        riskFactors.push('高價格場地');
    }

    if (venue.maxCapacityTheater > 500) {
        riskScore += 1;
        riskFactors.push('大型場地需要更多準備');
    }

    // 檢查是否有隱藏知識
    if (!venue.hiddenKnowledge || Object.keys(venue.hiddenKnowledge).length === 0) {
        riskScore += 2;
        riskFactors.push('缺乏專業知識');
    }

    // 計算風險等級
    let riskLevel = 'low';
    if (riskScore >= 4) {
        riskLevel = 'high';
    } else if (riskScore >= 2) {
        riskLevel = 'medium';
    }

    return { level: riskLevel, score: riskScore, factors: riskFactors };
}
