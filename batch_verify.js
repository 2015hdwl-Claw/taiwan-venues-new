/**
 * 批次驗證腳本 - 快速檢查多間飯店
 *
 * 用法: node batch_verify.js
 * 輸出: verification_reports/batch2_quick_summary.md
 */

const fs = require('fs');
const https = require('https');

// 批次2的5間示範飯店
const HOTELS = [
    { id: 1043, name: '台北六福萬怡酒店', url: 'https://www.courtyardtaipei.com.tw/wedding/list' },
    { id: 1069, name: '台北國賓大飯店', url: 'https://www.ambassador-hotels.com/tc/taipei' },
    { id: 1090, name: '茹曦酒店 ILLUME TAIPEI', url: 'https://www.theillumehotel.com/zh/' },
    { id: 1122, name: '維多麗亞酒店', url: 'https://www.grandvictoria.com.tw/' },
    { id: 1124, name: '花園大酒店', url: 'https://www.taipeigarden.com.tw' }
];

// 載入 venues.json
const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));

/**
 * 快速檢查單一飯店
 */
function quickCheckHotel(hotelId) {
    const venue = venues.find(v => v.id === hotelId);
    if (!venue) return { error: '找不到飯店' };

    const rooms = venue.rooms || [];

    return {
        id: venue.id,
        name: venue.name,
        url: venue.url,
        官網有資料: '⏳ 待檢查',
        venues_json會議室數: rooms.length,
        會議室名稱: rooms.map(r => r.name).join(', '),
        照片數量: rooms.reduce((sum, r) => sum + (r.images?.length || 0), 0),
        維度完整: rooms.every(r => r.length && r.width && r.sqm) ? '✅' : '❌',
        容量完整: rooms.every(r => r.capacity?.theater) ? '✅' : '❌',
        價格完整: rooms.every(r => r.price || r.pricing) ? '✅' : '❌',
        備註: ''
    };
}

/**
 * 生成批次摘要報告
 */
function generateBatchReport() {
    const results = HOTELS.map(h => quickCheckHotel(h.id));

    const report = `# 批次2飯店快速檢查報告

**生成時間**: ${new Date().toLocaleString('zh-TW')}
**檢查數量**: ${HOTELS.length} 間飯店

## 📊 快速摘要

| 飯店ID | 飯店名稱 | 會議室數 | 照片數 | 維度 | 容量 | 價格 | 狀態 |
|-------|---------|---------|--------|------|------|------|------|
${results.map(r =>
    `| ${r.id} | ${r.name} | ${r.venues_json會議室數}間 | ${r.照片數量}張 | ${r.維度完整} | ${r.容量完整} | ${r.價格完整} | ${r.備註 || '待檢查'} |`
).join('\n')}

## 📋 詳細清單

${results.map(r => `
### ${r.name} (ID: ${r.id})
- **官網**: ${r.url}
- **會議室**: ${r.venues_json會議室數}間 - ${r.會議室名稱}
- **照片總數**: ${r.照片數量}張
- **維度資料**: ${r.維度完整}
- **容量資料**: ${r.容量完整}
- **價格資料**: ${r.價格完整}
`).join('\n')}

## 🔍 下一步行動

1. [ ] 訪問各飯店官網擷取完整資料
2. [ ] 比對官網與 venues.json 差異
3. [ ] 生成詳細驗證報告（僅對有問題的飯店）

---

**說明**: 本報告由 batch_verify.js 自動生成
`.trim();

    // 確保目錄存在
    if (!fs.existsSync('verification_reports')) {
        fs.mkdirSync('verification_reports');
    }

    fs.writeFileSync('verification_reports/batch2_quick_summary.md', report, 'utf8');
    console.log('✅ 報告已生成: verification_reports/batch2_quick_summary.md');
}

// 執行
generateBatchReport();
