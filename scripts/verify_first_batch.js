const fs = require('fs');

const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));
const venueIds = [1103, 1075, 1076, 1072, 1077];

console.log('第一批飯店 dimensions 補充狀況');
console.log('='.repeat(70));

let totalRooms = 0;
let totalCompleted = 0;

venueIds.forEach(venueId => {
    const venue = venues.find(v => v.id === venueId);
    if (!venue) return;

    const completed = venue.rooms.filter(r => r.dimensions).length;
    const total = venue.rooms.length;

    totalRooms += total;
    totalCompleted += completed;

    const percentage = Math.round((completed / total) * 100);
    const status = percentage === 100 ? '✅' : (percentage >= 50 ? '🟡' : '🔴');

    console.log(`\n${status} ${venue.name} (ID: ${venueId})`);
    console.log(`   ${completed}/${total} 間會議室已完成 (${percentage}%)`);

    if (completed < total) {
        const missing = venue.rooms.filter(r => !r.dimensions);
        console.log(`   缺少 dimensions 的會議室:`);
        missing.forEach(r => {
            console.log(`     - ${r.name} (${r.id})`);
            console.log(`       area: ${r.area || '無'}, length: ${r.length || '無'}, width: ${r.width || '無'}, height: ${r.height || r.ceiling || '無'}`);
        });
    }
});

console.log('\n' + '='.repeat(70));
console.log(`總計: ${totalCompleted}/${totalRooms} 間會議室已完成 (${Math.round((totalCompleted/totalRooms)*100)}%)`);
