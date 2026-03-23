/**
 * 將蒐集的會議室尺寸資料轉換為 JSON 格式
 *
 * 輸入範例:
 * {
 *   "venueId": "1103",
 *   "venueName": "台北萬豪酒店",
 *   "rooms": [
 *     {
 *       "name": "春廳",
 *       "nameEn": "Spring Room",
 *       "floor": "B1",
 *       "length": 16.5,
 *       "width": 16,
 *       "height": 3.5,
 *       "area": 80,
 *       "areaUnit": "坪",
 *       "source": "官方"
 *     }
 *   ]
 * }
 */

const fs = require('fs');
const path = require('path');

/**
 * 計算平方公尺
 * @param {number} areaInPing - 坪數
 * @returns {number} 平方公尺
 */
function calculateSqm(areaInPing) {
  return Math.round(areaInPing * 3.305785 * 100) / 100;
}

/**
 * 生成 dimensions 字串
 * @param {number} length - 長度（公尺）
 * @param {number} width - 寬度（公尺）
 * @param {number} height - 高度（公尺）
 * @returns {string} 格式化的尺寸字串
 */
function generateDimensionsString(length, width, height) {
  const l = Math.round(length * 10) / 10;
  const w = Math.round(width * 10) / 10;
  const h = Math.round(height * 10) / 10;
  return `${l}x${w}x${h}m`;
}

/**
 * 判斷空間形狀
 * @param {number} length - 長度
 * @param {number} width - 寬度
 * @param {number} height - 高度
 * @returns {string} 形狀描述
 */
function determineShape(length, width, height) {
  const ratio = length / width;

  if (ratio > 0.9 && ratio < 1.1) {
    return '正方形';
  } else if (ratio >= 1.1 && ratio <= 2.5) {
    return '長方形';
  } else if (ratio > 2.5) {
    return '狹長型';
  } else {
    return '不規則';
  }
}

/**
 * 轉換單一會議室資料
 * @param {object} roomData - 原始會議室資料
 * @returns {object} 轉換後的會議室資料
 */
function convertRoomData(roomData) {
  const { length, width, height, area, areaUnit = '坪', source = '官方' } = roomData;

  // 計算平方公尺
  const sqm = area ? calculateSqm(area) : Math.round(length * width * 100) / 100;

  // 生成 dimensions 字串
  const dimensions = generateDimensionsString(length, width, height);

  // 判斷形狀
  const shape = determineShape(length, width, height);

  // 建立轉換後的物件
  const converted = {
    name: roomData.name,
    ...(roomData.nameEn && { nameEn: roomData.nameEn }),
    ...(roomData.floor && { floor: roomData.floor }),
    ...(area && { area }),
    areaUnit,
    sqm,
    ceiling: height,
    dimensions,
    shape,
  };

  // 如果是推算資料，添加標註
  if (source === '推算') {
    converted.shape = `${shape}（推算）`;
    converted.dataSource = '推算';
  }

  return converted;
}

/**
 * 更新 venues.json 中的特定場地
 * @param {string} venueId - 場地 ID
 * @param {object} venueData - 新的場地資料
 */
function updateVenue(venueId, venueData) {
  const venuesPath = path.join(__dirname, '..', 'venues.json');
  const venues = JSON.parse(fs.readFileSync(venuesPath, 'utf8'));

  // 找到目標場地
  const venueIndex = venues.findIndex(v => v.id === parseInt(venueId));

  if (venueIndex === -1) {
    console.error(`找不到場地 ID: ${venueId}`);
    return false;
  }

  // 更新會議室資料
  const updatedRooms = venueData.rooms.map((newRoom, index) => {
    const existingRoom = venues[venueIndex].rooms[index];

    // 保留原有欄位，只更新尺寸相關欄位
    const convertedRoom = convertRoomData(newRoom);

    return {
      ...existingRoom,
      ...convertedRoom,
      id: existingRoom.id || `${venueId}-${String(index + 1).padStart(2, '0')}`,
    };
  });

  // 更新場地資料
  venues[venueIndex].rooms = updatedRooms;

  // 寫入檔案
  fs.writeFileSync(
    venuesPath,
    JSON.stringify(venues, null, 2),
    'utf8'
  );

  console.log(`✓ 已更新場地: ${venues[venueIndex].name} (ID: ${venueId})`);
  console.log(`  更新 ${updatedRooms.length} 間會議室`);

  return true;
}

/**
 * 從 CSV 或 JSON 匯入並更新
 * @param {string} inputFile - 輸入檔案路徑
 */
function importFromFile(inputFile) {
  const ext = path.extname(inputFile).toLowerCase();

  if (ext === '.json') {
    const data = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
    updateVenue(data.venueId, data);
  } else if (ext === '.csv') {
    // CSV 處理邏輯（需要實作）
    console.log('CSV 匯入功能開發中...');
  } else {
    console.error('不支援的檔案格式:', ext);
  }
}

/**
 * 驗證會議室尺寸資料
 * @param {object} room - 會議室資料
 * @returns {object} 驗證結果
 */
function validateRoom(room) {
  const errors = [];
  const warnings = [];

  // 必要欄位檢查
  if (!room.dimensions) errors.push('缺少 dimensions 欄位');
  if (!room.sqm) errors.push('缺少 sqm 欄位');
  if (!room.ceiling) errors.push('缺少 ceiling 欄位');

  // 數值合理性檢查
  if (room.sqm && room.sqm <= 0) errors.push('sqm 必須大於 0');
  if (room.ceiling && room.ceiling < 2.5) warnings.push('層高似乎過低（< 2.5m）');
  if (room.ceiling && room.ceiling > 10) warnings.push('層高似乎過高（> 10m）');

  // 格式檢查
  if (room.dimensions && !/^\d+(\.\d+)?x\d+(\.\d+)?x\d+(\.\d+)?m$/.test(room.dimensions)) {
    errors.push('dimensions 格式錯誤，應為 "LxWxHm"');
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * 批次驗證場地的所有會議室
 * @param {string} venueId - 場地 ID
 */
function validateVenue(venueId) {
  const venuesPath = path.join(__dirname, '..', 'venues.json');
  const venues = JSON.parse(fs.readFileSync(venuesPath, 'utf8'));

  const venue = venues.find(v => v.id === parseInt(venueId));

  if (!venue) {
    console.error(`找不到場地 ID: ${venueId}`);
    return;
  }

  console.log(`\n驗證場地: ${venue.name} (ID: ${venueId})`);
  console.log(`會議室數量: ${venue.rooms.length}`);

  let hasErrors = false;
  let hasWarnings = false;

  venue.rooms.forEach((room, index) => {
    const validation = validateRoom(room);

    if (validation.errors.length > 0) {
      hasErrors = true;
      console.log(`\n❌ 會議室 ${index + 1}: ${room.name}`);
      validation.errors.forEach(err => console.log(`   - ${err}`));
    }

    if (validation.warnings.length > 0) {
      hasWarnings = true;
      console.log(`\n⚠️  會議室 ${index + 1}: ${room.name}`);
      validation.warnings.forEach(warn => console.log(`   - ${warn}`));
    }
  });

  if (!hasErrors && !hasWarnings) {
    console.log('\n✓ 所有會議室驗證通過');
  }
}

// CLI 介面
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'update':
      if (args[1]) {
        importFromFile(args[1]);
      } else {
        console.log('用法: node convert_dimensions_to_json.js update <輸入檔案>');
      }
      break;

    case 'validate':
      if (args[1]) {
        validateVenue(args[1]);
      } else {
        console.log('用法: node convert_dimensions_to_json.js validate <場地ID>');
      }
      break;

    case 'convert':
      // 單純轉換測試
      const testData = {
        name: '測試會議室',
        nameEn: 'Test Room',
        floor: '1F',
        length: 20,
        width: 15,
        height: 3.5,
        area: 90,
        areaUnit: '坪',
        source: '官方',
      };
      console.log('轉換範例:');
      console.log(JSON.stringify(convertRoomData(testData), null, 2));
      break;

    default:
      console.log(`
會議室尺寸資料轉換工具

用法:
  node convert_dimensions_to_json.js update <輸入檔案>  # 從檔案匯入並更新
  node convert_dimensions_to_json.js validate <場地ID>   # 驗證場地資料
  node convert_dimensions_to_json.js convert             # 轉換測試

範例:
  node convert_dimensions_to_json.js update marriott_rooms.json
  node convert_dimensions_to_json.js validate 1103
      `);
  }
}

module.exports = {
  convertRoomData,
  updateVenue,
  validateRoom,
  validateVenue,
  calculateSqm,
  generateDimensionsString,
  determineShape,
};
