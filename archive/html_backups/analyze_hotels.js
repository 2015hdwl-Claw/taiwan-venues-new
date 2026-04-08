const fs = require('fs');

const venues = JSON.parse(fs.readFileSync('venues.json', 'utf8'));

// 分析飯店場地
const hotelVenues = venues.filter(v =>
  v.name.includes('飯店') ||
  v.name.includes('Hotel') ||
  v.name.includes('酒店') ||
  v.name.includes('君悅') ||
  v.name.includes('萬豪') ||
  v.name.includes('香格里拉') ||
  v.name.includes('麗緻') ||
  v.name.includes('晶華') ||
  v.name.includes('文華東方') ||
  v.name.includes('寒舍') ||
  v.name.includes('喜來登') ||
  v.name.includes('艾美') ||
  v.name.includes('老爺') ||
  v.name.includes('國賓') ||
  v.name.includes('圓山') ||
  v.name.includes('神旺') ||
  v.name.includes('亞都') ||
  v.name.includes('六福') ||
  v.name.includes('兄弟') ||
  v.name.includes('花園') ||
  v.name.includes('豪景') ||
  v.name.includes('康華') ||
  v.name.includes('美福') ||
  v.name.includes('茹曦')
);

console.log(`\n=== 總共找到 ${hotelVenues.length} 個飯店場地 ===\n`);

// 分類分析
const categories = {
  '大型連鎖飯店': [],
  '已有尺寸資料': [],
  '有 area 但缺 dimensions': [],
  '完全無尺寸資料': [],
  '會議室數量>=5': []
};

hotelVenues.forEach(venue => {
  const hasDimensions = venue.rooms && venue.rooms.some(r => r.dimensions);
  const hasArea = venue.rooms && venue.rooms.some(r => r.area);
  const roomCount = venue.rooms ? venue.rooms.length : 0;

  // 大型連鎖飯店
  if (venue.name.includes('萬豪') || venue.name.includes('君悅') ||
      venue.name.includes('晶華') || venue.name.includes('文華東方') ||
      venue.name.includes('寒舍') || venue.name.includes('喜來登') ||
      venue.name.includes('艾美') || venue.name.includes('香格里拉')) {
    categories['大型連鎖飯店'].push({ id: venue.id, name: venue.name, rooms: roomCount, hasDimensions, hasArea });
  }

  // 已有尺寸資料
  if (hasDimensions) {
    categories['已有尺寸資料'].push({ id: venue.id, name: venue.name, rooms: roomCount });
  }

  // 有 area 但缺 dimensions
  if (hasArea && !hasDimensions) {
    categories['有 area 但缺 dimensions'].push({ id: venue.id, name: venue.name, rooms: roomCount });
  }

  // 完全無尺寸資料
  if (!hasArea && !hasDimensions) {
    categories['完全無尺寸資料'].push({ id: venue.id, name: venue.name, rooms: roomCount });
  }

  // 會議室數量>=5
  if (roomCount >= 5) {
    categories['會議室數量>=5'].push({ id: venue.id, name: venue.name, rooms: roomCount, hasDimensions, hasArea });
  }
});

// 輸出分類結果
console.log('【優先級1：大型連鎖飯店】');
categories['大型連鎖飯店'].forEach(v => {
  console.log(`  ID:${v.id} | ${v.name} | ${v.rooms}間會議室 | dimensions:${v.hasDimensions ? '✓' : '✗'} | area:${v.hasArea ? '✓' : '✗'}`);
});

console.log('\n【優先級2：會議室數量>=5的場地】');
categories['會議室數量>=5'].sort((a, b) => b.rooms - a.rooms).forEach(v => {
  console.log(`  ID:${v.id} | ${v.name} | ${v.rooms}間會議室 | dimensions:${v.hasDimensions ? '✓' : '✗'} | area:${v.hasArea ? '✓' : '✗'}`);
});

console.log('\n【優先級3：有 area 但缺 dimensions 的場地】');
categories['有 area 但缺 dimensions'].forEach(v => {
  console.log(`  ID:${v.id} | ${v.name} | ${v.rooms}間會議室`);
});

console.log('\n【已有尺寸資料的場地】');
categories['已有尺寸資料'].forEach(v => {
  console.log(`  ID:${v.id} | ${v.name} | ${v.rooms}間會議室`);
});

// 第一批推薦清單
console.log('\n\n=== 第一批飯店推薦清單（優先級排序）===\n');

const recommendations = [
  // 優先級1：大型連鎖飯店且會議室多
  ...categories['大型連鎖飯店']
    .filter(v => v.rooms >= 5)
    .sort((a, b) => b.rooms - a.rooms)
    .slice(0, 5),

  // 優先級2：有 area 資料的飯店（容易推算）
  ...categories['有 area 但缺 dimensions']
    .filter(v => v.rooms >= 5)
    .sort((a, b) => b.rooms - a.rooms)
    .slice(0, 3),
];

recommendations.forEach((v, i) => {
  const url = venues.find(venue => venue.id === v.id)?.url || 'N/A';
  console.log(`${i + 1}. ${v.name} (ID: ${v.id})`);
  console.log(`   會議室數量: ${v.rooms}間`);
  console.log(`   官網: ${url}`);
  console.log(`   資料狀態: dimensions=${v.hasDimensions ? '✓' : '✗'}, area=${v.hasArea ? '✓' : '✗'}`);
  console.log('');
});

// 輸出第一批清單到檔案
fs.writeFileSync('first_batch_hotels.json', JSON.stringify(recommendations.map(v => ({
  id: v.id,
  name: venues.find(venue => venue.id === v.id)?.name,
  url: venues.find(venue => venue.id === v.id)?.url,
  roomCount: v.rooms,
  hasDimensions: v.hasDimensions,
  hasArea: v.hasArea
})), null, 2));

console.log('第一批推薦清單已匯出至: first_batch_hotels.json');
