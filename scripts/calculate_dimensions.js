/**
 * 根據面積推算會議室的長寬尺寸
 */

const fs = require('fs');

// 推算公式
function calculateDimensions(areaInPing, height, aspectRatio = 1.3) {
    // 坪轉平方公尺
    const sqm = areaInPing * 3.305785;

    // 根據長寬比推算長寬
    const length = Math.sqrt(sqm * aspectRatio);
    const width = sqm / length;

    // 取小數點後一位
    return {
        length: Math.round(length * 10) / 10,
        width: Math.round(width * 10) / 10,
        sqm: Math.round(sqm)
    };
}

// 讀取 venues.json
const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));

// 需要推算的場地
const venueIds = [1075, 1076, 1077];

let totalCalculated = 0;
let totalSkipped = 0;

venueIds.forEach(venueId => {
    const venue = venues.find(v => v.id === venueId);
    if (!venue) return;

    console.log(`\n${venue.name} (ID: ${venueId})`);
    console.log('='.repeat(60));

    let calculatedCount = 0;
    let skippedCount = 0;

    venue.rooms.forEach(room => {
        // 跳過已有 dimensions 的
        if (room.dimensions) {
            skippedCount++;
            return;
        }

        // 檢查是否有面積資料
        const area = typeof room.area === 'number' ? room.area : parseFloat(room.area);
        const height = room.height || room.ceiling;

        if (!area || isNaN(area)) {
            console.log(`  ✗ ${room.name} - 無面積資料`);
            skippedCount++;
            return;
        }

        // 根據面積大小決定長寬比
        let aspectRatio;
        if (area >= 400) {
            aspectRatio = 1.5; // 大型宴會廳，較長
        } else if (area >= 150) {
            aspectRatio = 1.4; // 中型宴會廳
        } else if (area >= 50) {
            aspectRatio = 1.3; // 一般會議室
        } else {
            aspectRatio = 1.2; // 小型會議室
        }

        // 推算尺寸
        const { length, width, sqm } = calculateDimensions(area, height || 3, aspectRatio);

        // 更新會議室資料
        room.length = length;
        room.width = width;
        room.sqm = sqm;
        room.dimensions = `${length}x${width}x${height || 3}m`;
        room.shape = room.shape || '長方形（推算）';

        console.log(`  + ${room.name} (${room.id})`);
        console.log(`     ${area}坪 → ${length}x${width}x${height || 3}m (長寬比 ${aspectRatio}:1)`);

        calculatedCount++;
    });

    console.log(`\n  計算: ${calculatedCount} 間, 跳過: ${skippedCount} 間`);

    totalCalculated += calculatedCount;
    totalSkipped += skippedCount;
});

// 處理台北圓山大飯店缺少 width 的富貴廳
const grandHotel = venues.find(v => v.id === 1072);
if (grandHotel) {
    console.log(`\n台北圓山大飯店 - 修正富貴廳`);
    const富贵廳 = grandHotel.rooms.find(r => r.id === '1072-10');
    if (富贵廳 && 富贵廳.length && !富贵廳.width) {
        const area = 144;
        const height = 2.7;
        // 富貴廳有 length (12m)，推算 width
        const calculatedWidth = Math.round((area * 3.305785 / 12) * 10) / 10;

        富贵廳.width = calculatedWidth;
        富贵廳.sqm = Math.round(area * 3.305785);
        富贵廳.dimensions = `${富贵廳.length}x${calculatedWidth}x${height}m`;

        console.log(`  + 富貴廳 (1072-10)`);
        console.log(`     144坪 → ${富贵廳.length}x${calculatedWidth}x${height}m`);
        totalCalculated++;
    }
}

// 備份原始檔案
const backupFile = `venues.backup.${new Date().toISOString().split('T')[0].replace(/-/g, '')}.json`;
fs.writeFileSync(backupFile, JSON.stringify(venues, null, 2));

// 寫入更新後的資料
fs.writeFileSync('venues.json', JSON.stringify(venues, null, 2));

console.log('\n=================================');
console.log(`總計：推算 ${totalCalculated} 間會議室，跳過 ${totalSkipped} 間`);
console.log(`已備份至: ${backupFile}`);
