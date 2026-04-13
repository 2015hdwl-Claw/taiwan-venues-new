/**
 * generate-landing-pages.js
 * 生成城市頁和分類頁（SEO 入口頁）
 *
 * 用法：node tools/generate-landing-pages.js
 * 輸出：根目錄下的靜態 HTML 頁面
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const VENUES_FILE = path.join(ROOT, 'venues.json');
const AI_KB_DIR = path.join(ROOT, 'ai_knowledge_base', 'venues');
const SITE_URL = 'https://taiwan-venues-new-indol.vercel.app';
const TODAY = new Date().toISOString().split('T')[0];

// ─── Helpers ───

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function loadVenues() {
  return JSON.parse(fs.readFileSync(VENUES_FILE, 'utf8'))
    .filter(v => v.active !== false);
}

function loadAiKb(id) {
  try { return JSON.parse(fs.readFileSync(path.join(AI_KB_DIR, `${id}.json`), 'utf8')); }
  catch { return null; }
}

function getRoomMaxCap(room) {
  if (!room.capacity) return 0;
  return Math.max(
    room.capacity.theater || 0, room.capacity.classroom || 0,
    room.capacity.banquetWestern || 0, room.capacity.banquetEastern || 0,
    room.capacity.reception || 0, room.capacity.hollowSquare || 0,
    room.capacity.uShape || 0
  );
}

function getVenueMaxCap(v) {
  if (v.maxCapacityTheater) return v.maxCapacityTheater;
  const rooms = v.rooms || [];
  return rooms.length ? Math.max(...rooms.map(getRoomMaxCap)) : 0;
}

function venueCardHtml(v) {
  const cap = getVenueMaxCap(v);
  const rooms = (v.rooms || []).length;
  const img = v.images?.main || `${SITE_URL}/social/images/og-brand.png`;
  return `
                <a href="/venues/${v.id}" class="bg-surface-container-lowest rounded-xl border border-surface-container-high overflow-hidden hover:border-primary/30 hover:shadow-lg transition-all group">
                    <div class="h-40 overflow-hidden">
                        <img src="${escapeHtml(img)}" alt="${escapeHtml(v.name)}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy">
                    </div>
                    <div class="p-4">
                        <h3 class="font-bold text-on-surface mb-2 line-clamp-1">${escapeHtml(v.name)}</h3>
                        <div class="flex gap-3 text-xs text-on-surface-variant">
                            ${cap ? `<span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm">groups</span>${cap}人</span>` : ''}
                            <span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm">meeting_room</span>${rooms}間</span>
                        </div>
                    </div>
                </a>`;
}

// ─── Page Configs ───

const cityPages = [
  {
    slug: 'taipei-event-venue',
    h1: '台北活動場地推薦',
    title: '台北活動場地推薦｜小型聚會・講座・會議空間租借指南（2026最新）',
    metaDesc: '台北活動場地怎麼選？整理小型活動、講座、會議空間推薦與價格分析，快速找到適合10-2000人的場地，含場地限制與隱藏規定。',
    city: '台北市',
    intro: `台北是台灣活動場地最密集的城市，從五星飯店的宴會廳到靈活的共享空間，選擇多元。但在台北找活動場地，最常見的問題是「預算、交通與隱藏限制」。

一般來說可以這樣分：

小型活動（10-30人）：適合讀書會、工作坊、小型聚會。推薦選擇交通方便的共享空間或會議中心，價格約 NT$500-1,500/小時。集思台大會議中心、公務人力發展學院是高 CP 值的選擇。

中型活動（30-200人）：適合講座、教育訓練、發表會。需要投影設備與音響的場地，飯店場地和會議中心最合適。寒舍喜來登、晶華酒店都有適合此規模的廳別。

大型活動（200人以上）：適合研討會、尾牙、國際會議。圓山大飯店大會廳可容納 2000 人，台北國際會議中心（TICC）更大達 3100 人，是全台最大容量的會議場地。

台北場地的幾個注意事項：
- 飯店場地多數限用飯店餐飲，不可外燴
- 大型場地需提前 2-6 個月預訂，尾牙季（12-1月）和婚宴旺季（10-12月）最難搶
- 天花板高度是常被忽略的限制，影響舞台設計和燈光架設`,
    faqs: [
      { q: '台北活動場地租金多少？', a: '小型空間約 NT$500-1,500/小時，中型場地 NT$3,000-15,000/半天，大型宴會廳 NT$20,000-100,000+/全天。飯店場地通常以半天或全天計價。' },
      { q: '台北哪裡適合辦講座？', a: '集思台大會議中心、公務人力發展學院、各飯店的中小型會議廳都是熱門選擇，設備齊全且交通便利。' },
      { q: '台北場地需要提前多久預訂？', a: '一般場地建議至少 2-4 週前預訂。旺季（尾牙季、婚宴季）建議 2-6 個月前。大型國際會議中心可能需要半年以上。' },
      { q: '台北活動場地有哪些隱藏費用？', a: '常見加收項目包括：清潔費、冷氣超時費、設備租借費（投影機、音響）、電力超載費、保險費、停車位不足的代價。建議簽約前確認所有費用明細。' },
      { q: '台北 vs 新北場地怎麼選？', a: '台北交通便利但價格較高，新北（特別板橋）CP 值更高且空間較大。如果活動參加者多搭捷運，台北更方便；如果預算有限或有開車需求，新北是好選擇。' }
    ]
  },
  {
    slug: 'new-taipei-event-venue',
    h1: '新北活動場地推薦',
    title: '新北活動場地推薦｜板橋・中和・新店場地租借（2026最新）',
    metaDesc: '新北活動場地推薦，板橋、中和、新店等地區活動空間租借資訊。CP值比台北高20-40%，適合企業會議、婚宴、課程活動。',
    city: '新北市',
    intro: `新北市是台北活動場地的最佳替代選擇，特別是板橋、中和、新店等區域，CP 值比台北市區高 20-40%。

新北場地的優勢：
- 價格比台北低 20-40%，同樣預算可以租到更大的空間
- 停車位通常比台北充足，適合需要開車運器材的活動
- 板橋交通方便，高鐵、台鐵、捷運三鐵共構

新北場地分布：
- 板橋區：Mega50 宴會廳、晶宴會館府中館，適合婚宴和大型聚會
- 中和區：瓏山林台北中和飯店、豪鼎飯店，商務會議和家庭聚會
- 新店區：彭園婚宴會館，大型婚宴和宴會

選擇新北場地時要注意：
- 捷運站步行距離確認（有些場地說「近捷運」實際要走 15 分鐘）
- 周邊餐飲選擇可能不如台北豐富
- 部分場地是純婚宴取向，不適合商務會議`,
    faqs: [
      { q: '新北活動場地租金多少？', a: '比台北便宜約 20-40%。小型空間約 NT$300-1,000/小時，中型場地 NT$2,000-10,000/半天，婚宴場地 NT$8,000-30,000/桌。' },
      { q: '板橋有哪些推薦的活動場地？', a: '板橋有 Mega50 宴會廳、晶宴會館府中館等。板橋車站周邊交通便利，是舉辦中型活動的好選擇。' },
      { q: '新北場地適合企業會議嗎？', a: '適合。中和、新店的飯店場地設備齊全，價格比台北同級場地低很多，適合預算有限的企業內訓或部門會議。' }
    ]
  },
  {
    slug: 'taichung-event-venue',
    h1: '台中活動場地推薦',
    title: '台中活動場地推薦｜會議室・婚宴・展演空間租借（2026最新）',
    metaDesc: '台中活動場地推薦，涵蓋裕元花園酒店、葳格國際會議中心等7個場地。會議、婚宴、展演空間租借資訊與注意事項。',
    city: '台中市',
    intro: `台中是中台灣最大的活動場地市場，場地類型涵蓋飯店、婚宴會館和會議中心，價格通常比台北低 30-50%。

台中場地特色：
- 空間大、價格實惠，同樣預算可以租到比台北大 1.5-2 倍的空間
- 婚宴場地特別豐富，天圓地方、林皇宮花園、潮港城都是知名場地
- 葳格國際會議中心、集思台中新烏日會議中心是專業會議場地

選擇台中場地要注意：
- 交通以自行開車為主，捷運覆蓋範圍有限
- 台中港酒店、裕元花園酒店離市區較遠，需安排接駁
- 婚宴場地週末檔期競爭激烈，平日較容易預訂`,
    faqs: [
      { q: '台中活動場地租金多少？', a: '比台北便宜約 30-50%。小型會議室 NT$500-2,000/小時，婚宴場地 NT$8,000-20,000/桌，會議中心半天約 NT$5,000-20,000。' },
      { q: '台中適合辦研討會的場地有哪些？', a: '葳格國際會議中心、集思台中新烏日會議中心設備齊全，適合中大型研討會。裕元花園酒店也有適合的會議空間。' },
      { q: '台中場地交通方便嗎？', a: '部分場地離捷運站較遠，建議選擇有停車位的場地。新烏日會議中心靠近高鐵站，外縣市參加者交通方便。' }
    ]
  }
];

const categoryPages = [
  {
    slug: 'small-event-venue',
    h1: '小型活動場地推薦',
    title: '小型活動場地推薦｜10-30人會議室・工作坊空間（2026最新）',
    metaDesc: '適合10-30人的小型活動場地推薦。讀書會、工作坊、部門會議，快速找到設備齊全、交通方便的小型空間。',
    filterFn: v => {
      const rooms = v.rooms || [];
      return rooms.some(r => {
        const cap = getRoomMaxCap(r);
        return cap >= 10 && cap <= 30;
      });
    },
    intro: `小型活動場地（10-30人）是需求量最大但最容易被忽略的類別。讀書會、工作坊、部門會議、創業 pitch，這些活動需要的不是大空間，而是「剛好的大小 + 齊全的設備」。

選擇小型場地的重點：
- 投影設備：確認有 HDMI 或無線投影，不要假設「一定有」
- 白板或玻璃牆：工作坊和討論型活動必備
- 網路頻寬：線上直播或遠距參加需要穩定連線
- 隔音：共享空間的隔音品質差異很大，影響錄音和直播

小型場地的常見陷阱：
- 有些場地「最多 30 人」但舒適容量只有 15-20 人
- 按人頭計價的場地，超出人數會大幅加收費用
- 共享空間的冷氣和照明可能無法獨立控制`,
    faqs: [
      { q: '小型活動場地租借費用多少？', a: '共享空間 NT$300-800/小時，飯店小型會議室 NT$1,500-5,000/半天，會議中心 NT$2,000-8,000/半天。' },
      { q: '10人活動適合租什麼場地？', a: '10人活動建議選擇有投影設備的小型會議室，交通方便最重要。集思系列會議中心、飯店的小型會議室都是好選擇。' },
      { q: '小型場地需要提前多久預訂？', a: '平日場地通常 1-2 週前即可，週末和熱門時段建議 2-4 週前預訂。' }
    ]
  },
  {
    slug: 'seminar-venue',
    h1: '講座場地推薦',
    title: '講座場地推薦｜20-80人課程・分享會・教育訓練空間（2026最新）',
    metaDesc: '適合20-80人的講座場地推薦。分享會、課程、教育訓練場地，附投影機、音響設備，交通便利。',
    filterFn: v => {
      const rooms = v.rooms || [];
      return rooms.some(r => {
        const cap = getRoomMaxCap(r);
        return cap >= 20 && cap <= 80;
      });
    },
    intro: `講座型場地（20-80人）是活動企劃最常搜尋的類型。無論是企業內訓、公開課程、分享會還是研討會，這個規模的場地選擇最多，但要注意的細節也最多。

講座場地的必備條件：
- 投影設備：建議確認投影機流明數，大場地需要 3000 流明以上
- 音響系統：超過 30 人的場地需要麥克風，確認有無線麥克風
- 座位排列彈性：劇院式、教室式、U 型，不同排列方式容量差很大
- 讓講者方便進出的動線

講座場地的隱藏費用：
- 投影機和音響可能需要額外租借（即使場地「有設備」）
- 冷氣超時費（很多場地只含基本時段）
- 清潔費和場地恢復費`,
    faqs: [
      { q: '講座場地租借費用多少？', a: '20-50人場地約 NT$3,000-10,000/半天，50-80人場地約 NT$5,000-20,000/半天。設備齊全的會議中心通常比飯店便宜。' },
      { q: '辦講座需要什麼設備？', a: '基本需要投影機、音響、麥克風。超過 50 人建議加直播設備和背板。確認場地網路頻寬足夠線上直播需求。' },
      { q: '台北哪裡適合辦講座？', a: '集思台大會議中心、公務人力發展學院設備齊全且價格合理。飯店場地如寒舍喜來登、晶華酒店也適合商務型講座。' }
    ]
  },
  {
    slug: 'meeting-room-rental',
    h1: '會議室租借推薦',
    title: '會議室租借推薦｜商務會議・企業內訓空間（2026最新）',
    metaDesc: '商務會議室租借推薦。企業會議、內訓、董事會議場地，設備齊全，含投影、音響、視訊設備，快速找到適合的會議空間。',
    filterFn: v => {
      const rooms = v.rooms || [];
      return rooms.some(r => {
        const cap = getRoomMaxCap(r);
        return cap >= 10 && cap <= 60;
      });
    },
    intro: `會議室租借是企業最常見的場地需求。從 10 人的部門會議到 60 人的全公司內訓，選擇合適的會議室可以大幅提升會議效率。

商務會議室的核心需求：
- 視訊設備：遠距會議需要好的攝影機和收音設備
- 白板空間：腦力激盪和策略討論必備
- 隱私性：董事會議和機密討論需要獨立空間
- 餐飲服務：全天會議需要午餐和茶點安排

會議室租借的注意事項：
- 確認報到時間是否含在租借時段內
- 設備清單要逐一確認，不要只看「設備齊全」
- 超時費用通常按小時計算，費率可能比基本時段高 50%`,
    faqs: [
      { q: '會議室租借費用多少？', a: '小型會議室（10人）NT$500-2,000/小時，中型會議室（20-40人）NT$1,500-5,000/小時，大型會議室（50人+）NT$3,000-10,000/小時。' },
      { q: '租會議室需要注意什麼？', a: '重點確認：設備是否含在租金內、冷氣時段限制、超時費用、停車位數量、餐飲是否限用場地服務、取消和改期的退款政策。' },
      { q: '台北商務會議室推薦？', a: '集思系列會議中心專業度高且價格合理。飯店會議室設備齊全但價格較高。公務人力發展學院是高CP值選擇。' }
    ]
  }
];

// ─── HTML Generator ───

function generateLandingHtml(config, venues) {
  const jsonLds = [
    { "@context": "https://schema.org", "@type": "FAQPage",
      "mainEntity": config.faqs.map(f => ({
        "@type": "Question", "name": f.q,
        "acceptedAnswer": { "@type": "Answer", "text": f.a }
      }))
    },
    { "@context": "https://schema.org", "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "首頁", "item": `${SITE_URL}/` },
        { "@type": "ListItem", "position": 2, "name": config.h1, "item": `${SITE_URL}/${config.slug}` }
      ]
    }
  ];

  const venueCards = venues.slice(0, 12).map(venueCardHtml).join('\n');

  return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="${escapeHtml(config.metaDesc)}">
    <title>${escapeHtml(config.title)}</title>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="canonical" href="${SITE_URL}/${config.slug}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="${escapeHtml(config.title)}">
    <meta property="og:description" content="${escapeHtml(config.metaDesc)}">
    <meta property="og:url" content="${SITE_URL}/${config.slug}">
    <meta property="og:image" content="${SITE_URL}/social/images/og-brand.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:locale" content="zh_TW">
    <meta property="og:site_name" content="活動大師">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="${escapeHtml(config.title)}">
    <meta name="twitter:description" content="${escapeHtml(config.metaDesc)}">

    <!-- JSON-LD -->
    ${jsonLds.map(s => `<script type="application/ld+json">${JSON.stringify(s)}</script>`).join('\n    ')}

    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    "colors": {
                        "on-tertiary-fixed": "#370e00", "secondary": "#3f6560",
                        "surface-container-low": "#f2f3f8", "inverse-on-surface": "#eff1f5",
                        "on-primary": "#ffffff", "on-secondary-fixed": "#00201d",
                        "surface-variant": "#e1e2e6", "primary-fixed-dim": "#6bd8cb",
                        "on-surface-variant": "#3d4947", "tertiary-fixed-dim": "#ffb59a",
                        "inverse-primary": "#6bd8cb", "surface-bright": "#f8f9fd",
                        "on-secondary-fixed-variant": "#274d48", "primary-container": "#0d9488",
                        "on-tertiary-container": "#fffbff", "surface-dim": "#d8dade",
                        "outline": "#6d7a77", "on-tertiary-fixed-variant": "#773215",
                        "surface": "#f8f9fd", "secondary-fixed-dim": "#a6cfc8",
                        "error": "#ba1a1a", "outline-variant": "#bcc9c6",
                        "on-primary-fixed-variant": "#005049", "tertiary-fixed": "#ffdbce",
                        "tertiary": "#924628", "primary-fixed": "#89f5e7",
                        "on-primary-fixed": "#00201d", "surface-tint": "#0d9488",
                        "on-surface": "#191c1f", "secondary-fixed": "#c2ebe3",
                        "background": "#f8f9fd", "surface-container": "#eceef2",
                        "on-tertiary": "#ffffff", "tertiary-container": "#b05e3d",
                        "surface-container-high": "#e7e8ec", "error-container": "#ffdad6",
                        "primary": "#0d9488", "on-primary-container": "#f4fffc",
                        "on-background": "#191c1f", "on-error": "#ffffff",
                        "on-secondary": "#ffffff", "inverse-surface": "#2e3134",
                        "on-secondary-container": "#456b66", "on-error-container": "#93000a",
                        "surface-container-lowest": "#ffffff", "secondary-container": "#c2ebe3",
                        "surface-container-highest": "#e1e2e6",
                        "brand-teal": "#0d9488", "brand-teal-surface": "#f0fdfa",
                        "brand-teal-hover": "#0f766e"
                    },
                    "borderRadius": { "DEFAULT": "1rem", "lg": "2rem", "xl": "3rem", "full": "9999px" },
                    "fontFamily": { "headline": ["Space Grotesk","sans-serif"], "body": ["Inter","sans-serif"] }
                }
            }
        }
    </script>
    <style>
        .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; display: inline-block; line-height: 1; }
        .line-clamp-1 { display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
    </style>
</head>
<body class="bg-surface text-on-surface font-body">

    <!-- Navigation -->
    <nav class="bg-white/80 backdrop-blur-xl sticky top-0 z-50">
        <div class="flex justify-between items-center px-8 py-4 max-w-screen-2xl mx-auto">
            <a href="index.html" class="text-2xl font-bold text-primary font-headline tracking-tight">活動大師 Activity Master</a>
            <a href="index.html" class="text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1">
                <span class="material-symbols-outlined">arrow_back</span> 返回首頁
            </a>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto px-6 md:px-12 py-12">
        <!-- Hero -->
        <header class="mb-16">
            <h1 class="text-4xl md:text-5xl font-headline font-bold tracking-tight text-on-surface mb-4">${escapeHtml(config.h1)}</h1>
            <p class="text-lg text-on-surface-variant">活動大師整理 ${venues.length} 個場地資訊，官網沒寫的限制、潛規則、踩坑經驗都在這。</p>
        </header>

        <!-- Intro Text -->
        <section class="mb-16 prose max-w-none">
            ${config.intro.split('\n\n').map(p => `<p class="text-on-surface-variant leading-relaxed mb-4">${p.replace(/\n/g, '<br>')}</p>`).join('')}
        </section>

        <!-- Venue Cards -->
        <section class="mb-16">
            <h2 class="text-2xl md:text-3xl font-headline font-medium text-on-surface mb-8 flex items-center gap-3">
                <span class="material-symbols-outlined text-primary">storefront</span> 推薦場地（${venues.length} 個）
            </h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
${venueCards}
            </div>
        </section>

        <!-- FAQ -->
        <section class="mb-16">
            <h2 class="text-2xl md:text-3xl font-headline font-medium text-on-surface mb-8 flex items-center gap-3">
                <span class="material-symbols-outlined text-primary">help</span> 常見問題
            </h2>
            <div class="space-y-3">
                ${config.faqs.map(f => `
                <details class="group bg-surface-container-low rounded-xl border border-surface-container-high">
                    <summary class="flex items-center justify-between cursor-pointer p-5 font-medium text-on-surface hover:text-primary transition-colors">
                        <span>${escapeHtml(f.q)}</span>
                        <span class="material-symbols-outlined text-on-surface-variant group-open:rotate-180 transition-transform">expand_more</span>
                    </summary>
                    <div class="px-5 pb-5 text-on-surface-variant leading-relaxed">${escapeHtml(f.a)}</div>
                </details>`).join('')}
            </div>
        </section>

        <!-- CTA -->
        <div class="text-center mb-16">
            <a href="index.html" class="inline-flex items-center gap-2 bg-primary text-on-primary px-8 py-3 rounded-full font-medium hover:bg-brand-teal-hover transition-colors">
                <span class="material-symbols-outlined">smart_toy</span> 用 AI 助理找更多場地
            </a>
        </div>

        <!-- E-E-A-T -->
        <div class="text-center text-xs text-on-surface-variant space-y-1">
            <p>資料最後更新：${TODAY}</p>
            <p>資料來源：場地官方網站 | 活動大師 — 活動企劃的場地知識庫</p>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-[#191c1f] flex flex-col md:flex-row justify-between items-center px-12 py-16 w-full mt-16">
        <div class="flex flex-col items-center md:items-start gap-4 mb-8 md:mb-0">
            <span class="text-xl font-bold text-white font-headline">活動大師 Activity Master</span>
            <p class="text-neutral-400 font-headline text-sm uppercase tracking-widest opacity-80">&copy; 2026 活動大師. All rights reserved.</p>
        </div>
        <div class="flex gap-8">
            <a class="text-neutral-400 hover:text-teal-400 transition-colors font-headline text-sm uppercase tracking-widest opacity-80 hover:opacity-100" href="index.html">首頁</a>
            <a class="text-neutral-400 hover:text-teal-400 transition-colors font-headline text-sm uppercase tracking-widest opacity-80 hover:opacity-100" href="index.html#venues-section">場地列表</a>
        </div>
    </footer>
</body>
</html>`;
}

// ─── Main ───

function main() {
  const venues = loadVenues();

  let totalPages = 0;

  // Generate city pages
  for (const config of cityPages) {
    const cityVenues = venues.filter(v => v.city === config.city);
    const html = generateLandingHtml(config, cityVenues);
    fs.writeFileSync(path.join(ROOT, `${config.slug}.html`), html, 'utf8');
    console.log(`City page: ${config.slug}.html (${cityVenues.length} venues)`);
    totalPages++;
  }

  // Generate category pages
  for (const config of categoryPages) {
    const matched = venues.filter(config.filterFn);
    const html = generateLandingHtml(config, matched);
    fs.writeFileSync(path.join(ROOT, `${config.slug}.html`), html, 'utf8');
    console.log(`Category page: ${config.slug}.html (${matched.length} venues)`);
    totalPages++;
  }

  console.log(`\nGenerated ${totalPages} landing pages`);
}

main();
