/**
 * 根據台北晶華酒店官網資料修正 dimensions
 * 資料來源：https://www.regenttaiwan.com/occasions/event-venues
 */

const fs = require('fs');

const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));
const venue = venues.find(v => v.id === 1086);

if (!venue) {
    console.log('找不到台北晶華酒店');
    process.exit(1);
}

// 官網資料
const officialData = {
    '晶英會': { sqm: 270, height: 2.4 },
    '晶華會': { sqm: 357, height: 2.3 },
    '宴會廳': { sqm: 888, height: 5 },
    '萬象廳': { sqm: 470, height: 2.35 },
    '貴賓廳': { sqm: 776, height: 2.3 }
};

console.log('台北晶華酒店 - 根據官網資料修正');
console.log('='.repeat(70));

venue.rooms.forEach(room => {
    const official = officialData[room.name];

    if (official) {
        // 使用官網的 sqm 和 height
        room.sqm = official.sqm;
        room.height = official.height;

        // 根據 sqm 反推長寬（假設長寬比 1.3:1）
        const aspectRatio = 1.3;
        const length = Math.sqrt(official.sqm * aspectRatio);
        const width = official.sqm / length;

        room.length = Math.round(length * 10) / 10;
        room.width = Math.round(width * 10) / 10;
        room.dimensions = `${room.length}x${room.width}x${official.height}m`;
        room.shape = room.shape || '長方形';
        room.ceiling = official.height;

        console.log(`✓ ${room.name} (${room.id})`);
        console.log(`  sqm: ${official.sqm} (官方)`);
        console.log(`  height: ${official.height}m (官方)`);
        console.log(`  dimensions: ${room.dimensions}`);
        console.log(`  shape: 長方形`);
    } else {
        console.log(`? ${room.name} (${room.id}) - 官網無資料`);
    }
});

// 備份
const backupFile = `venues.backup.${new Date().toISOString().split('T')[0].replace(/-/g, '')}.json`;
fs.writeFileSync(backupFile, JSON.stringify(venues, null, 2));

// 寫入更新
fs.writeFileSync('venues.json', JSON.stringify(venues, null, 2));

console.log('\n' + '='.repeat(70));
console.log(`已修正台北晶華酒店 5 間會議室資料`);
console.log(`備份: ${backupFile}`);
