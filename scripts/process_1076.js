const fs = require('fs');

const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));
const venue = venues.find(v => v.id === 1076);

if (!venue) {
    console.log('找不到場地 1076');
    process.exit(1);
}

console.log(`處理: ${venue.name} (ID: 1076)`);

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

venue.rooms.forEach(room => {
    if (room.dimensions) return;

    const area = typeof room.area === 'number' ? room.area : parseFloat(room.area);
    const height = room.height || room.ceiling || 3;

    if (!area || isNaN(area)) {
        console.log(`  ✗ ${room.name} - 無面積資料`);
        return;
    }

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

    console.log(`  + ${room.name} - ${room.dimensions}`);
});

fs.writeFileSync('venues.json', JSON.stringify(venues, null, 2));
console.log('\n✅ 已更新並儲存');
