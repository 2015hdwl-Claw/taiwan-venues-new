const fs = require('fs');

const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));

// 篩選出飯店類型的場地
const hotelVenues = venues.filter(v => {
    const name = v.name || '';
    return name.includes('酒店') || name.includes('Hotel') || name.includes('飯店') ||
           name.includes('度假村') || name.includes(' Resort') ||
           name.includes(' motel') || name.includes('Motel');
});

// 分析每個飯店的 dimensions 狀況
const analysis = hotelVenues.map(venue => {
    const totalRooms = venue.rooms ? venue.rooms.length : 0;
    const completedRooms = venue.rooms ? venue.rooms.filter(r => r.dimensions).length : 0;
    const percentage = totalRooms > 0 ? Math.round((completedRooms / totalRooms) * 100) : 0;

    return {
        id: venue.id,
        name: venue.name,
        totalRooms,
        completedRooms,
        missingRooms: totalRooms - completedRooms,
        percentage,
        needsWork: completedRooms < totalRooms && totalRooms > 0
    };
})
.filter(v => v.needsWork) // 只列出需要工作的
.sort((a, b) => {
    // 排序優先順序：
    // 1. 完成度低的優先
    // 2. 會議室數量多的優先
    if (a.percentage !== b.percentage) return a.percentage - b.percentage;
    return b.totalRooms - a.totalRooms;
});

console.log('第二批飯店建議清單');
console.log('='.repeat(80));
console.log('\n優先順序根據：1) 完成度低 → 2) 會議室數量多\n');

analysis.forEach((venue, index) => {
    const status = venue.percentage === 0 ? '🔴' : (venue.percentage < 50 ? '🟡' : '🟢');
    console.log(`${status} ${index + 1}. ${venue.name} (ID: ${venue.id})`);
    console.log(`   會議室: ${venue.completedRooms}/${venue.totalRooms} (${venue.percentage}%)`);
    console.log(`   待補充: ${venue.missingRooms} 間\n`);
});

console.log('='.repeat(80));
console.log(`總計: ${analysis.length} 個飯店場地需要補充 dimensions`);

// 建議第二批（前 5-10 個）
console.log('\n建議第二批飯店（前 8 個）：');
const batch2 = analysis.slice(0, 8);
batch2.forEach((venue, index) => {
    console.log(`${index + 1}. ${venue.name} (ID: ${venue.id}) - ${venue.missingRooms} 間待補充`);
});

// 輸出第二批飯店清單到 JSON
const batch2List = batch2.map(v => ({
    id: v.id,
    name: v.name,
    totalRooms: v.totalRooms,
    missingRooms: v.missingRooms
}));

fs.writeFileSync('second_batch_hotels.json', JSON.stringify(batch2List, null, 2));
console.log('\n已輸出至 second_batch_hotels.json');
