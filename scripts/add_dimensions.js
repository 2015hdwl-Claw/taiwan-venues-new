/**
 * 批量添加 dimensions 欄位到指定場地的會議室
 * 格式: "LxWxHm" (長x寬x高)
 */

const fs = require('fs');

// 讀取 venues.json
const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));

// 處理指定場地
const venueId = 1103; // 台北萬豪酒店
const venue = venues.find(v => v.id === venueId);

if (!venue) {
    console.error('找不到場地 ID:', venueId);
    process.exit(1);
}

console.log(`處理場地: ${venue.name} (ID: ${venueId})`);
console.log(`總會議室數: ${venue.rooms.length}`);

let updatedCount = 0;
let skippedCount = 0;

venue.rooms.forEach(room => {
    // 檢查是否已有 dimensions
    if (room.dimensions) {
        console.log(`  ✓ ${room.name} (${room.id}) - 已有 dimensions: ${room.dimensions}`);
        skippedCount++;
        return;
    }

    // 獲取長、寬、高
    const length = room.length;
    const width = room.width;
    const height = room.height || room.ceiling;

    // 檢查必要欄位是否存在
    if (!length || !width || !height) {
        console.log(`  ✗ ${room.name} (${room.id}) - 缺少尺寸資料 (length:${length}, width:${width}, height:${height})`);
        skippedCount++;
        return;
    }

    // 生成 dimensions 字串
    room.dimensions = `${length}x${width}x${height}m`;

    console.log(`  + ${room.name} (${room.id}) - 添加 dimensions: ${room.dimensions}`);
    updatedCount++;
});

// 備份原始檔案
const backupFile = `venues.backup.${new Date().toISOString().split('T')[0].replace(/-/g, '')}.json`;
fs.writeFileSync(backupFile, JSON.stringify(venues, null, 2));
console.log(`\n已備份至: ${backupFile}`);

// 寫入更新後的資料
fs.writeFileSync('venues.json', JSON.stringify(venues, null, 2));

console.log(`\n完成！`);
console.log(`  - 更新: ${updatedCount} 間會議室`);
console.log(`  - 跳過: ${skippedCount} 間會議室`);
