/**
 * 批次處理第二批飯店 dimensions 補充
 */

const fs = require('fs');

const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));

// 第二批飯店 IDs
const venueIds = [1086, 1043, 1069, 1090, 1122, 1051, 1068, 1085];

function calculateDimensions(areaInPing, height, aspectRatio = 1.3) {
    const sqm = areaInPing * 3.305785;
    const length = Math.sqrt(sqm * aspectRatio);
    const width = sqm / length;
    return {
        length: Math.round(length * 10) / 10,
        width: Math.round(width * 10) / 10,
        sqm: Math.round(sqm)
    };
}

let totalProcessed = 0;
let totalSkipped = 0;
const results = [];

venueIds.forEach(venueId => {
    const venue = venues.find(v => v.id === venueId);
    if (!venue) {
        console.log(`⚠️  找不到場地 ID: ${venueId}`);
        return;
    }

    console.log(`\n${venue.name} (ID: ${venueId})`);
    console.log('-'.repeat(70));

    let processedCount = 0;
    let skippedCount = 0;
    const roomResults = [];

    venue.rooms.forEach(room => {
        if (room.dimensions) {
            skippedCount++;
            return;
        }

        const area = typeof room.area === 'number' ? room.area : parseFloat(room.area);
        const height = room.height || room.ceiling || 3;

        if (!area || isNaN(area)) {
            roomResults.push({
                room: room.name,
                status: 'skip',
                reason: '無面積資料'
            });
            skippedCount++;
            return;
        }

        // 根據面積大小決定長寬比
        let aspectRatio;
        if (area >= 400) aspectRatio = 1.5;
        else if (area >= 150) aspectRatio = 1.4;
        else if (area >= 50) aspectRatio = 1.3;
        else aspectRatio = 1.2;

        const { length, width, sqm } = calculateDimensions(area, height, aspectRatio);

        room.length = length;
        room.width = width;
        room.sqm = sqm;
        room.dimensions = `${length}x${width}x${height}m`;
        room.shape = room.shape || '長方形（推算）';

        roomResults.push({
            room: room.name,
            status: 'done',
            dimensions: room.dimensions
        });

        console.log(`  ✓ ${room.name} - ${room.dimensions}`);
        processedCount++;
    });

    console.log(`  處理: ${processedCount} 間, 跳過: ${skippedCount} 間`);

    totalProcessed += processedCount;
    totalSkipped += skippedCount;

    results.push({
        venueId,
        venueName: venue.name,
        totalRooms: venue.rooms.length,
        processed: processedCount,
        skipped: skippedCount,
        rooms: roomResults
    });
});

// 備份
const backupFile = `venues.backup.${new Date().toISOString().split('T')[0].replace(/-/g, '')}.json`;
fs.writeFileSync(backupFile, JSON.stringify(venues, null, 2));

// 寫入更新
fs.writeFileSync('venues.json', JSON.stringify(venues, null, 2));

// 輸出報告
console.log('\n' + '='.repeat(70));
console.log('第二批飯店處理完成報告');
console.log('='.repeat(70));

results.forEach(r => {
    console.log(`\n${r.venueName}`);
    console.log(`  已完成: ${r.processed}/${r.totalRooms}`);
    if (r.skipped > 0) {
        console.log(`  跳過: ${r.skipped}`);
    }
});

console.log('\n' + '='.repeat(70));
console.log(`總計: ${totalProcessed} 間會議室已完成, ${totalSkipped} 間跳過`);
console.log(`備份: ${backupFile}`);
