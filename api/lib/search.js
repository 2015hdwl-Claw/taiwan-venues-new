/**
 * Keyword-based fallback search for when embeddings are not available
 *
 * This provides a simple but effective search using:
 * 1. Chinese keyword matching
 * 2. Category filtering
 * 3. Venue-specific search
 */

const fs = require('fs');
const path = require('path');

let venuesData = null;

/**
 * Load all venue data
 */
function loadVenues() {
  if (!venuesData) {
    const venuesDir = path.join(process.cwd(), 'ai_knowledge_base', 'venues');
    if (fs.existsSync(venuesDir)) {
      venuesData = [];
      const files = fs.readdirSync(venuesDir).filter(f => f.endsWith('.json'));
      for (const file of files) {
        const content = fs.readFileSync(path.join(venuesDir, file), 'utf-8');
        venuesData.push(JSON.parse(content));
      }
    }
  }
  return venuesData || [];
}

/**
 * Extract searchable text from a venue
 */
function extractSearchableText(venue) {
  const texts = [];
  const venueName = venue.identity?.name || '';

  // Rules
  const rules = venue.rules || {};
  for (const [category, rulesList] of Object.entries(rules)) {
    if (Array.isArray(rulesList)) {
      for (const rule of rulesList) {
        if (rule.rule) {
          texts.push({
            type: 'rule',
            category,
            text: rule.rule,
            venueId: venue.identity?.id,
            venueName,
            fullText: `【${venueName}】${getCategoryLabel(category)}：${rule.rule}`
          });
        }
      }
    }
  }

  // Rooms
  for (const room of (venue.rooms || [])) {
    const roomName = room.name || '';

    // Limitations
    if (room.limitations && Array.isArray(room.limitations)) {
      for (const lim of room.limitations) {
        texts.push({
          type: 'limitation',
          category: 'room',
          text: lim,
          venueId: venue.identity?.id,
          venueName,
          roomName,
          fullText: `【${venueName} - ${roomName}】限制：${lim}`
        });
      }
    }

    // LoadIn
    const loadin = room.loadIn || {};
    if (loadin.elevatorCapacity || loadin.loadingDock || loadin.loadInTime) {
      const parts = [];
      if (loadin.elevatorCapacity) parts.push(`貨梯：${loadin.elevatorCapacity}`);
      if (loadin.loadingDock) parts.push(`卸貨區：${loadin.loadingDock}`);
      if (loadin.loadInTime) parts.push(`進場時間：${loadin.loadInTime}`);
      if (loadin.loadOutTime) parts.push(`撤場時間：${loadin.loadOutTime}`);
      texts.push({
        type: 'loadIn',
        category: 'room',
        text: parts.join('，'),
        venueId: venue.identity?.id,
        venueName,
        roomName,
        fullText: `【${venueName} - ${roomName}】進撤場：${parts.join('，')}`
      });
    }
  }

  // Risks
  const risks = venue.risks || {};
  if (risks.bookingLeadTime || risks.commonIssues?.length) {
    const parts = [];
    if (risks.bookingLeadTime) parts.push(`預訂提前：${risks.bookingLeadTime}`);
    if (risks.commonIssues) parts.push(`常見問題：${risks.commonIssues.join('、')}`);
    texts.push({
      type: 'risk',
      category: 'venue',
      text: parts.join('。'),
      venueId: venue.identity?.id,
      venueName,
      fullText: `【${venueName}】風險提示：${parts.join('。')}`
    });
  }

  return texts;
}

/**
 * Get Chinese label for category
 */
function getCategoryLabel(category) {
  const labels = {
    catering: '餐飲規定',
    decoration: '佈置規定',
    sound: '音響規定',
    loadIn: '進撤場規定',
    cancellation: '取消政策',
    insurance: '保險規定',
    pricing: '價格規定',
    other: '其他規定'
  };
  return labels[category] || category;
}

/**
 * Calculate simple relevance score based on keyword matching
 */
function calculateScore(text, keywords, venueName = '') {
  let score = 0;
  const lowerText = text.toLowerCase();
  const fullText = text;

  for (const keyword of keywords) {
    // Skip if keyword is a venue name (handled separately)
    if (venueName && venueName.includes(keyword)) continue;

    // Exact match
    if (fullText.includes(keyword)) {
      score += 10;
    }
    // Partial match
    else if (lowerText.includes(keyword.toLowerCase())) {
      score += 5;
    }
  }

  return score;
}

/**
 * Check if query mentions a specific venue (fuzzy match)
 */
function findMentionedVenue(query, venues) {
  // Extract potential venue names from query
  const venueKeywords = [
    ['圓山', '圓山飯店', '台北圓山'],
    ['寒舍', '喜來登', '寒舍喜來登'],
    ['艾美', '寒舍艾美', 'le meridien'],
    ['晶華', 'regent'],
    ['文華東方', 'MOH', 'mandarin oriental'],
    ['萬豪', 'marriott'],
    ['集思', '集思台大', '台大會議'],
    ['南港', '南港展覽館'],
    ['TICC', '國際會議中心'],
    ['世貿', '台北世貿', 'TWTCA']
  ];

  for (const [key, ...aliases] of venueKeywords) {
    if (query.includes(key) || aliases.some(a => query.includes(a))) {
      // Find matching venue
      const matched = venues.find(v => {
        const name = (v.identity?.name || '').toLowerCase();
        return name.includes(key.toLowerCase()) ||
               aliases.some(a => name.includes(a.toLowerCase()));
      });
      if (matched) return matched;
    }
  }
  return null;
}

/**
 * Search for relevant information using keywords
 */
function keywordSearch(query, options = {}) {
  const { venueId, topK = 5 } = options;

  // Extract keywords from query
  const keywords = extractKeywords(query);

  // Load venues
  const venues = loadVenues();

  // Check if query mentions a specific venue
  const mentionedVenue = findMentionedVenue(query, venues);

  // Filter venues: prefer mentioned venue, fall back to venueId or all
  let targetVenues;
  if (mentionedVenue) {
    targetVenues = [mentionedVenue];
  } else if (venueId) {
    targetVenues = venues.filter(v => v.identity?.id === venueId);
  } else {
    targetVenues = venues;
  }

  // Extract all searchable text
  const allTexts = [];
  for (const venue of targetVenues) {
    allTexts.push(...extractSearchableText(venue));
  }

  // Score each text
  const scored = allTexts.map(item => ({
    ...item,
    score: calculateScore(item.fullText, keywords, item.venueName)
  }));

  // Boost score if from mentioned venue
  if (mentionedVenue) {
    scored.forEach(item => {
      if (item.venueId === mentionedVenue.identity?.id) {
        item.score *= 2; // Double score for mentioned venue
      }
    });
  }

  // Sort by score and return top K
  return scored
    .filter(item => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);
}

/**
 * Extract keywords from Chinese query
 */
function extractKeywords(query) {
  // keyword patterns with synonyms (Chinese + English)
  // Map English terms to their Chinese equivalents for matching
  const keywordMappings = {
    // Catering
    'catering': ['外食', '外燴', '餐飲', '自助餐', '宴席', '酒水', '飲料', '餐盒', '限用飯店'],
    'food': ['外食', '外燴', '餐飲', '自助餐'],
    'meal': ['餐飲', '宴席'],
    'banquet': ['宴席', '宴會'],
    'buffet': ['自助餐'],
    // Decoration
    'decoration': ['佈置', '裝飾', '花藝', '氣球', '背板'],
    'decor': ['佈置', '裝飾'],
    'stage': ['舞台'],
    'lighting': ['燈光'],
    // Sound/AV
    'sound': ['音響'],
    'audio': ['音響'],
    'projector': ['投影'],
    'microphone': ['麥克風'],
    // Load-in
    'loadin': ['進場', '卸貨'],
    'loadout': ['撤場'],
    'setup': ['佈置時間', '進場'],
    // Cancellation
    'cancel': ['取消', '退費'],
    'refund': ['退費'],
    'deposit': ['訂金'],
    // Insurance
    'insurance': ['保險', '公共意外'],
    // General
    'rule': ['規定', '限制'],
    'policy': ['規定', '政策'],
    'price': ['價格', '費用', '收費'],
    'cost': ['費用', '成本'],
    'limit': ['限制', '不可', '禁止'],
    'allow': ['可以', '允許'],
  };

  // Chinese keyword patterns (direct match)
  const chinesePatterns = [
    '外食', '外燴', '餐飲', '自助餐', '宴席', '酒水', '飲料', '餐盒',
    '自帶', '自己帶', '自備',
    '限用', '不可', '禁止',
    '佈置', '裝飾', '花藝', '氣球', '背板', '舞台', '燈光',
    '音響', '投影', '麥克風', '簡報', 'LED',
    '進場', '撤場', '卸貨', '貨梯', '佈置時間', '前一天',
    '取消', '退費', '訂金', '違約金',
    '保險', '公共意外',
    '限制', '規定', '注意', '費用', '價格', '收費', '可以', '能夠'
  ];

  const found = [];
  const lowerQuery = query.toLowerCase();

  // Check Chinese patterns directly
  for (const pattern of chinesePatterns) {
    if (query.includes(pattern)) {
      found.push(pattern);
    }
  }

  // Check English patterns and add their Chinese equivalents
  for (const [english, chineseEquivalents] of Object.entries(keywordMappings)) {
    if (lowerQuery.includes(english.toLowerCase())) {
      found.push(english); // Keep the English keyword
      found.push(...chineseEquivalents); // Add Chinese equivalents
    }
  }

  // Also extract any venue names mentioned
  const venues = loadVenues();
  for (const venue of venues) {
    const name = venue.identity?.name || '';
    const shortName = name.split('(')[0].trim();
    if (name && query.includes(shortName)) {
      found.push(shortName);
      // Also add keywords from the venue's rules
      const rules = venue.rules || {};
      for (const [cat, rlist] of Object.entries(rules)) {
        if (Array.isArray(rlist)) {
          for (const r of rlist) {
            if (r.rule) {
              // Extract key phrases from rules that might be relevant
              const keyPhrases = r.rule.match(/.{2,4}/g) || [];
              for (const phrase of keyPhrases) {
                if (query.includes(phrase)) {
                  found.push(phrase);
                }
              }
            }
          }
        }
      }
    }
  }

  return [...new Set(found)]; // Dedupe
}

module.exports = {
  keywordSearch,
  loadVenues,
  extractKeywords
};
