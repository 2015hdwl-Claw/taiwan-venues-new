const fs = require('fs');
const data = JSON.parse(fs.readFileSync('venues.json', 'utf8'));
const venue = data.find(v => v.id === 1103);

if (venue) {
    const missing = venue.rooms.filter(r => !r.dimensions);
    console.log('總會議室數:', venue.rooms.length);
    console.log('缺少 dimensions 欄位:', missing.length);

    if (missing.length > 0) {
        console.log('\n缺少 dimensions 的會議室:');
        missing.forEach(r => console.log('  -', r.name, '(' + r.id + ')'));
    }
} else {
    console.log('Venue not found');
}
