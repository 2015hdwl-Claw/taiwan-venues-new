/**
 * 批量檢查並添加 dimensions 欄位到多個場地
 */

const fs = require('fs');

// 第一批飯店 IDs
const venueIds = [1103, 1075, 1076, 1072, 1077];

// 讀取 venues.json
const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));

let totalUpdated = 0;
let totalSkipped = 0;
const venueResults = [];

venueIds.forEach(venueId => {
    const venue = venues.find(v => v.id === venueId);

    if (!venue) {
        console.error(`找不到場地 ID: ${venueId}`);
        return;
    }

    console.log(`\n處理場地: ${venue.name} (ID: ${venueId})`);
    console.log(`總會議室數: ${venue.rooms.length}`);

    let updatedCount = 0;
    let skippedCount = 0;

    venue.rooms.forEach(room => {
        // 檢查是否已有 dimensions
        if (room.dimensions) {
            skippedCount++;
            return;
        }

        // 獲取長、寬、高
        const length = room.length;
        const width = room.width;
        const height = room.height || room.ceiling;

        // 檢查必要欄位是否存在
        if (!length || !width || !height) {
            skippedCount++;
            return;
        }

        // 生成 dimensions 字串
        room.dimensions = `${length}x${width}x${height}m`;
        updatedCount++;
    });

    console.log(`  - 更新: ${updatedCount} 間會議室`);
    console.log(`  - 跳過: ${skippedCount} 間會議室`);

    venueResults.push({
        venueId,
        venueName: venue.name,
        totalRooms: venue.rooms.length,
        updated: updatedCount,
        skipped: skippedCount
    });

    totalUpdated += updatedCount;
    totalSkipped += skippedCount;
});

// 備份原始檔案
const backupFile = `venues.backup.${new Date().toISOString().split('T')[0].replace(/-/g, '')}.json`;
fs.writeFileSync(backupFile, JSON.stringify(venues, null, 2));

// 寫入更新後的資料
fs.writeFileSync('venues.json', JSON.stringify(venues, null, 2));

console.log('\n=================================');
console.log('總計：');
console.log(`  - 總更新: ${totalUpdated} 間會議室`);
console.log(`  - 總跳過: ${totalSkipped} 間會議室`);
console.log(`\n已備份至: ${backupFile}`);
