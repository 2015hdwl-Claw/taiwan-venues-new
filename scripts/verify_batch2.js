const fs = require('fs');

const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));

// 第二批飯店 IDs (所有 24 個)
const venueIds = [1086, 1043, 1069, 1090, 1122, 1051, 1068, 1085, 1095, 1097, 1124, 1048, 1053, 1059, 1073, 1080, 1082, 1083, 1084, 1092, 1099, 1100, 1121, 1126];

console.log('第二批飯店 dimensions 補充完成狀況');
console.log('='.repeat(80));

let totalRooms = 0;
let totalCompleted = 0;
const completed = [];
const partial = [];
const notStarted = [];

venueIds.forEach(venueId => {
    const venue = venues.find(v => v.id === venueId);
    if (!venue) return;

    const done = venue.rooms.filter(r => r.dimensions).length;
    const total = venue.rooms.length;
    const percentage = Math.round((done / total) * 100);

    totalRooms += total;
    totalCompleted += done;

    if (percentage === 100) {
        completed.push({ name: venue.name, done, total });
    } else if (percentage > 0) {
        partial.push({ name: venue.name, done, total, percentage });
    } else {
        notStarted.push({ name: venue.name, done, total });
    }
});

console.log(`\n✅ 100% 完成 (${completed.length} 個):`);
completed.forEach(v => {
    console.log(`   ${v.name} - ${v.done}/${v.total} 間`);
});

if (partial.length > 0) {
    console.log(`\n🟡 部分完成 (${partial.length} 個):`);
    partial.forEach(v => {
        console.log(`   ${v.name} - ${v.done}/${v.total} 間 (${v.percentage}%)`);
    });
}

if (notStarted.length > 0) {
    console.log(`\n🔴 未開始 (${notStarted.length} 個):`);
    notStarted.forEach(v => {
        console.log(`   ${v.name} - ${v.done}/${v.total} 間`);
    });
}

console.log('\n' + '='.repeat(80));
console.log(`第二批總計: ${totalCompleted}/${totalRooms} 間會議室 (${Math.round((totalCompleted/totalRooms)*100)}%)`);
