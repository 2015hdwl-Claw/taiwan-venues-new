/**
 * generate-static-pages.js
 * 從 venues.json 生成靜態場地頁面，讓 Google 不需 JS 就能索引。
 *
 * 用法：node tools/generate-static-pages.js
 * 輸出：venues/{id}.html（每個啟用場地一頁）
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const VENUES_FILE = path.join(ROOT, 'venues.json');
const AI_KB_DIR = path.join(ROOT, 'ai_knowledge_base', 'venues');
const OUTPUT_DIR = path.join(ROOT, 'venues');
const SITE_URL = 'https://taiwan-venues-new-indol.vercel.app';
const TODAY = new Date().toISOString().split('T')[0];

// ─── helpers ───

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function getRoomMaxCap(room) {
  if (!room.capacity) return 0;
  return Math.max(
    room.capacity.theater || 0,
    room.capacity.classroom || 0,
    room.capacity.banquetWestern || 0,
    room.capacity.banquetEastern || 0,
    room.capacity.reception || 0,
    room.capacity.hollowSquare || 0,
    room.capacity.uShape || 0
  );
}

function getVenueMaxCap(venue) {
  if (venue.maxCapacity) return venue.maxCapacity;
  const rooms = venue.rooms || [];
  if (rooms.length === 0) return 0;
  return Math.max(...rooms.map(getRoomMaxCap));
}

function formatPrice(room) {
  if (!room.pricing) return null;
  const p = room.pricing;
  if (p.halfDay) return `半日 $${Number(p.halfDay).toLocaleString()}`;
  if (p.fullDay) return `全日 $${Number(p.fullDay).toLocaleString()}`;
  if (p.perHour) return `$${Number(p.perHour).toLocaleString()}/hr`;
  return null;
}

function getPriceRange(venue) {
  const rooms = venue.rooms || [];
  let min = Infinity, max = 0;
  for (const r of rooms) {
    if (!r.pricing) continue;
    const p = r.pricing;
    const vals = [p.halfDay, p.fullDay].filter(Boolean).map(Number);
    if (vals.length) {
      min = Math.min(min, ...vals);
      max = Math.max(max, ...vals);
    }
  }
  if (min === Infinity) return '價格面議';
  if (min === max) return `$${min.toLocaleString()}`;
  return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
}

// ─── AI Knowledge Base ───

function loadAiKb(venueId) {
  const kbPath = path.join(AI_KB_DIR, `${venueId}.json`);
  try {
    return JSON.parse(fs.readFileSync(kbPath, 'utf8'));
  } catch {
    return null;
  }
}

function generateFaqs(venue, kb) {
  const faqs = [];
  const name = (venue.name || '').replace(/\(.*\)/, '').trim();

  // From KB summary
  if (kb?.summary?.shortDescription) {
    faqs.push({
      q: `${name}是什麼樣的場地？`,
      a: kb.summary.shortDescription
    });
  }

  // From KB rules
  if (kb?.rules) {
    for (const [category, rules] of Object.entries(kb.rules)) {
      if (!Array.isArray(rules) || rules.length === 0) continue;
      const labels = {
        catering: '餐飲', decoration: '佈置', sound: '音響',
        loadIn: '進場', cancellation: '取消', insurance: '保險', other: '其他'
      };
      const label = labels[category] || category;
      const rule = rules[0];
      const answer = [rule.rule, rule.exception && `例外：${rule.exception}`,
        rule.penalty && `罰則：${rule.penalty}`].filter(Boolean).join('。');
      if (answer) {
        faqs.push({ q: `${name}${label}有什麼規定？`, a: answer });
      }
      if (faqs.length >= 5) break;
    }
  }

  // From KB risks
  if (kb?.risks?.bookingLeadTime) {
    faqs.push({
      q: `${name}需要提前多久預訂？`,
      a: kb.risks.bookingLeadTime
    });
  }

  // From KB logistics
  if (kb?.logistics?.nearestMRT) {
    faqs.push({
      q: `${name}交通怎麼去？`,
      a: `最近捷運站：${kb.logistics.nearestMRT}`
    });
  }

  // Fallback generic FAQs
  if (faqs.length === 0) {
    const rooms = venue.rooms || [];
    const maxCap = getVenueMaxCap(venue);
    faqs.push(
      { q: `${name}有幾間會議室？`, a: `${name}共有 ${rooms.length} 間會議室${maxCap ? `，最大可容納 ${maxCap} 人` : ''}。` },
      { q: `${name}適合什麼類型的活動？`, a: `適合${venue.venueType || '各類'}場地活動，包括會議、研討會、宴會等。` }
    );
  }

  return faqs.slice(0, 5);
}

// ─── JSON-LD ───

function buildVenueJsonLd(venue, faqs) {
  const rooms = venue.rooms || [];
  const maxCap = getVenueMaxCap(venue);
  const phone = venue.contact?.phone || venue.phone || '';
  const email = venue.contact?.email || venue.email || '';

  const schemas = [{
    "@context": "https://schema.org",
    "@type": "EventVenue",
    "name": venue.name,
    "description": `${venue.name}，${venue.venueType || '場地'}。${rooms.length}間會議室，最多${maxCap}人。含天花板高度、電力負載、進場動線等官網不寫的資訊。`,
    "url": `${SITE_URL}/venues/${venue.id}`,
    "address": {
      "@type": "PostalAddress",
      "addressLocality": venue.city || "台灣",
      "streetAddress": venue.address || ""
    },
    ...(phone && { "telephone": phone }),
    ...(email && { "email": email }),
    ...(venue.images?.main && { "image": venue.images.main }),
    ...(venue.url && { "sameAs": venue.url }),
    "maximumAttendeeCapacity": maxCap,
    ...(rooms.length > 0 && {
      "amenityFeature": rooms.slice(0, 5).map(r => ({
        "@type": "LocationFeatureSpecification",
        "name": r.name,
        "value": `${r.area ? r.area + '坪' : ''} ${r.ceilingHeight ? '天花板' + r.ceilingHeight + '米' : ''} 最多${getRoomMaxCap(r)}人`
      }))
    })
  }];

  // FAQPage schema
  if (faqs.length > 0) {
    schemas.push({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": faqs.map(f => ({
        "@type": "Question",
        "name": f.q,
        "acceptedAnswer": { "@type": "Answer", "text": f.a }
      }))
    });
  }

  // BreadcrumbList
  schemas.push({
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "首頁", "item": `${SITE_URL}/` },
      { "@type": "ListItem", "position": 2, "name": venue.name, "item": `${SITE_URL}/venues/${venue.id}` }
    ]
  });

  return schemas;
}

// ─── HTML template ───

function generateVenueHtml(venue) {
  const rooms = venue.rooms || [];
  const maxCap = getVenueMaxCap(venue);
  const titleSuffix = '場地知識庫 | 活動大師';
  const title = `${venue.name} — ${titleSuffix}`;

  // Load AI KB data
  const kb = loadAiKb(venue.id);
  const faqs = generateFaqs(venue, kb);
  const kbSummary = kb?.summary?.shortDescription || '';
  const strengths = kb?.summary?.strengths || [];
  const weaknesses = kb?.summary?.weaknesses || [];
  const suitableTypes = kb?.summary?.suitableEventTypes || [];
  const pricingTips = kb?.pricingTips || [];
  const logistics = kb?.logistics || {};
  const venueLastUpdated = venue.lastUpdated || venue.lastVerified || '';

  const metaDesc = kbSummary
    ? `${kbSummary.slice(0, 140)} | 活動大師`
    : `${venue.name}，${venue.venueType || '場地'}。${rooms.length}間會議室${maxCap ? '，最多' + maxCap + '人' : ''}。含天花板高度、電力負載、進場動線等官網不寫的資訊。`;
  const canonicalUrl = `${SITE_URL}/venues/${venue.id}`;
  const imageUrl = venue.images?.main || `${SITE_URL}/social/images/og-brand.png`;
  const jsonLds = buildVenueJsonLd(venue, faqs);
  const priceRange = getPriceRange(venue);
  const phone = venue.contact?.phone || venue.phone || '';
  const email = venue.contact?.email || venue.email || '';

  // Build room cards HTML
  const roomCardsHtml = rooms.map(r => {
    const rCap = getRoomMaxCap(r);
    const rPrice = formatPrice(r);
    const rArea = r.area ? `${r.area}坪` : (r.areaPing ? `${r.areaPing}坪` : '');
    const rCeil = r.ceilingHeight ? `天花板 ${r.ceilingHeight}m` : '';
    const rFloor = r.floor ? `${r.floor}` : '';
    const rUrl = `${SITE_URL}/room.html?venueId=${venue.id}&roomId=${r.id}`;

    return `
        <article class="bg-surface-container-lowest rounded-xl border border-surface-container-high overflow-hidden hover:border-primary/30 transition-colors">
          <div class="p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h3 class="text-xl font-bold text-on-surface">${escapeHtml(r.name)}</h3>
                ${r.nameEn ? `<p class="text-sm text-on-surface-variant">${escapeHtml(r.nameEn)}</p>` : ''}
              </div>
              ${rFloor ? `<span class="text-xs bg-surface-container text-on-surface-variant px-3 py-1 rounded-full">${escapeHtml(rFloor)}</span>` : ''}
            </div>
            <div class="flex flex-wrap gap-4 text-sm text-on-surface-variant mb-4">
              ${rCap ? `<span class="flex items-center gap-1"><span class="material-symbols-outlined text-base">groups</span> ${rCap}人</span>` : ''}
              ${rArea ? `<span class="flex items-center gap-1"><span class="material-symbols-outlined text-base">square_foot</span> ${rArea}</span>` : ''}
              ${rCeil ? `<span class="flex items-center gap-1"><span class="material-symbols-outlined text-base">height</span> ${rCeil}</span>` : ''}
            </div>
            ${rPrice ? `<p class="text-primary font-bold">${rPrice}</p>` : ''}
            ${r.description ? `<p class="text-sm text-on-surface-variant mt-3 line-clamp-2">${escapeHtml(r.description)}</p>` : ''}
            <a href="${rUrl}" class="inline-block mt-4 text-primary font-medium text-sm hover:underline">查看詳情 →</a>
          </div>
        </article>`;
  }).join('');

  // Build highlights
  const highlightsHtml = (venue.highlights || []).map(h =>
    `          <li class="flex items-start gap-2"><span class="material-symbols-outlined text-primary text-base mt-0.5">check_circle</span><span>${escapeHtml(h)}</span></li>`
  ).join('\n');

  return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-YGTFFCFZHC"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-YGTFFCFZHC');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="${escapeHtml(metaDesc)}">
    <title>${escapeHtml(title)}</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link rel="canonical" href="${canonicalUrl}">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="${escapeHtml(title)}">
    <meta property="og:description" content="${escapeHtml(metaDesc)}">
    <meta property="og:url" content="${canonicalUrl}">
    <meta property="og:image" content="${imageUrl}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:locale" content="zh_TW">
    <meta property="og:site_name" content="活動大師">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="${escapeHtml(title)}">
    <meta name="twitter:description" content="${escapeHtml(metaDesc)}">
    <meta name="twitter:image" content="${imageUrl}">

    <!-- JSON-LD (multiple schemas) -->
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
        .line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    </style>
</head>
<body class="bg-surface text-on-surface font-body selection:bg-primary-fixed selection:text-on-primary-fixed">

    <!-- Navigation -->
    <nav class="bg-white/80 backdrop-blur-xl sticky top-0 z-50 border-b border-outline-variant">
        <div class="flex justify-between items-center px-8 py-4 w-full max-w-screen-2xl mx-auto">
            <div class="flex items-center gap-8">
                <a href="../index.html" class="flex items-center gap-3">
                    <img src="../favicon.svg" alt="活動大師" class="w-10 h-10">
                    <span class="text-xl font-bold text-primary font-headline tracking-tight">活動大師</span>
                </a>
                <div class="hidden md:flex gap-6 items-center">
                    <a href="../index.html" class="text-primary font-bold border-b-2 border-primary font-headline tracking-tight hover:text-primary-container transition-colors duration-300">場地列表</a>
                </div>
            </div>
            <div class="flex items-center gap-4">
                <a href="../index.html" class="text-on-surface-variant hover:text-primary transition-colors">
                    <span class="material-symbols-outlined">arrow_back</span> 返回列表
                </a>
            </div>
        </div>
    </nav>

    <main class="max-w-screen-2xl mx-auto px-6 md:px-12 py-12">
        <!-- Venue Hero -->
        <section class="relative grid grid-cols-1 lg:grid-cols-12 gap-8 mb-16">
            <div class="lg:col-span-8 group relative overflow-hidden rounded-xl h-[400px] md:h-[600px]">
                <img src="${imageUrl}" alt="${escapeHtml(venue.name)}" class="w-full h-full object-cover" loading="eager">
                <div class="absolute bottom-8 left-8">
                    <div class="bg-surface-container-lowest/90 backdrop-blur-md px-6 py-4 rounded-xl inline-flex flex-col border border-primary/10">
                        ${venue.venueType ? `<span class="text-primary font-bold text-sm tracking-widest uppercase mb-1">${escapeHtml(venue.venueType)}</span>` : ''}
                        <h1 class="text-4xl md:text-6xl font-bold tracking-tight text-on-surface">${escapeHtml(venue.name)}</h1>
                    </div>
                </div>
            </div>
            <div class="lg:col-span-4 flex flex-col justify-center space-y-8 bg-surface-container-low p-10 rounded-xl border border-surface-container-high">
                <div class="space-y-4">
                    ${venue.address ? `<div class="flex items-center gap-3 text-on-surface-variant"><span class="material-symbols-outlined">location_on</span><span>${escapeHtml(venue.address)}</span></div>` : ''}
                    <div class="flex items-center gap-3 text-on-surface-variant">
                        <span class="material-symbols-outlined">meeting_room</span>
                        <span>${rooms.length} 間會議室</span>
                    </div>
                    ${maxCap ? `<div class="flex items-center gap-3 text-on-surface-variant"><span class="material-symbols-outlined">groups</span><span>最多 ${maxCap} 人</span></div>` : ''}
                </div>
                <div class="space-y-3 pt-4 border-t border-surface-container-high">
                    <div class="flex justify-between items-center">
                        <span class="text-on-surface-variant text-sm">價格區間</span>
                        <span class="font-bold text-primary">${priceRange}</span>
                    </div>
                </div>
                <div class="flex gap-3">
                    ${phone ? `<a class="flex-1 text-center border border-outline-variant text-on-surface py-3 rounded-full font-medium hover:border-primary hover:text-primary transition-all" href="tel:${escapeHtml(phone)}"><span class="material-symbols-outlined text-sm align-middle">phone</span> 撥打電話</a>` : ''}
                    ${venue.url ? `<a class="flex-1 text-center border border-outline-variant text-on-surface py-3 rounded-full font-medium hover:border-primary hover:text-primary transition-all" href="${escapeHtml(venue.url)}" target="_blank" rel="noopener"><span class="material-symbols-outlined text-sm align-middle">language</span> 官網</a>` : ''}
                </div>
            </div>
        </section>

        ${venue.highlights?.length ? `
        <!-- Highlights -->
        <section class="mb-16">
            <h2 class="text-2xl md:text-3xl font-headline font-medium text-on-surface mb-6 flex items-center gap-3">
                <span class="material-symbols-outlined text-primary">star</span> 場地亮點
            </h2>
            <ul class="grid md:grid-cols-2 gap-3 text-on-surface-variant">
${highlightsHtml}
            </ul>
        </section>` : ''}

        <!-- Room List -->
        <section class="mb-24">
            <div class="flex justify-between items-end mb-12">
                <div>
                    <h2 class="text-4xl md:text-5xl font-bold tracking-tighter mb-4">會議室</h2>
                    <p class="text-on-surface-variant text-lg">${rooms.length} 間會議室空間</p>
                </div>
                <span class="text-sm text-on-surface-variant bg-surface-container px-4 py-2 rounded-full">${rooms.length} 間</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
${roomCardsHtml}
            </div>
        </section>

        ${kbSummary ? `
        <!-- AI Knowledge Summary -->
        <section class="mb-16">
            <h2 class="text-2xl md:text-3xl font-headline font-medium text-on-surface mb-6 flex items-center gap-3">
                <span class="material-symbols-outlined text-primary">info</span> 場地介紹
            </h2>
            <div class="bg-surface-container-low rounded-xl p-8 border border-surface-container-high prose max-w-none">
                <p class="text-on-surface-variant text-lg leading-relaxed">${escapeHtml(kbSummary)}</p>
            </div>
            ${strengths.length > 0 ? `
            <div class="mt-6 grid md:grid-cols-2 gap-6">
                <div>
                    <h3 class="font-bold text-primary mb-3 flex items-center gap-2"><span class="material-symbols-outlined text-base">thumb_up</span> 優勢</h3>
                    <ul class="space-y-2">
                        ${strengths.map(s => `<li class="flex items-start gap-2 text-sm text-on-surface-variant"><span class="text-primary mt-1">+</span>${escapeHtml(s)}</li>`).join('')}
                    </ul>
                </div>
                ${weaknesses.length > 0 ? `
                <div>
                    <h3 class="font-bold text-error mb-3 flex items-center gap-2"><span class="material-symbols-outlined text-base">warning</span> 注意事項</h3>
                    <ul class="space-y-2">
                        ${weaknesses.map(w => `<li class="flex items-start gap-2 text-sm text-on-surface-variant"><span class="text-error mt-1">!</span>${escapeHtml(w)}</li>`).join('')}
                    </ul>
                </div>` : ''}
            </div>` : ''}
            ${suitableTypes.length > 0 ? `
            <div class="mt-6 flex flex-wrap gap-2">
                <span class="text-sm text-on-surface-variant mr-2">適合活動：</span>
                ${suitableTypes.map(t => `<span class="text-xs bg-primary/10 text-primary px-3 py-1 rounded-full">${escapeHtml(t)}</span>`).join('')}
            </div>` : ''}
        </section>` : ''}

        ${pricingTips.length > 0 ? `
        <!-- Pricing Tips -->
        <section class="mb-16">
            <h2 class="text-2xl md:text-3xl font-headline font-medium text-on-surface mb-6 flex items-center gap-3">
                <span class="material-symbols-outlined text-primary">savings</span> 省錢技巧
            </h2>
            <ul class="space-y-3">
                ${pricingTips.map(t => `<li class="flex items-start gap-3 bg-surface-container-low rounded-lg p-4 border border-surface-container-high"><span class="material-symbols-outlined text-primary text-base mt-0.5">lightbulb</span><span class="text-on-surface-variant">${escapeHtml(t)}</span></li>`).join('')}
            </ul>
        </section>` : ''}

        ${logistics.nearestMRT || logistics.parking?.validationFee ? `
        <!-- Logistics -->
        <section class="mb-16">
            <h2 class="text-2xl md:text-3xl font-headline font-medium text-on-surface mb-6 flex items-center gap-3">
                <span class="material-symbols-outlined text-primary">directions</span> 交通資訊
            </h2>
            <div class="grid sm:grid-cols-2 gap-4">
                ${logistics.nearestMRT ? `<div class="bg-surface-container-low rounded-xl p-5 border border-surface-container-high"><div class="text-sm text-on-surface-variant mb-1">捷運</div><div class="font-medium text-on-surface">${escapeHtml(logistics.nearestMRT)}</div></div>` : ''}
                ${logistics.parking?.validationFee ? `<div class="bg-surface-container-low rounded-xl p-5 border border-surface-container-high"><div class="text-sm text-on-surface-variant mb-1">停車</div><div class="font-medium text-on-surface">${escapeHtml(logistics.parking.validationFee)}</div></div>` : ''}
            </div>
        </section>` : ''}

        ${faqs.length > 0 ? `
        <!-- FAQ -->
        <section class="mb-16">
            <h2 class="text-2xl md:text-3xl font-headline font-medium text-on-surface mb-6 flex items-center gap-3">
                <span class="material-symbols-outlined text-primary">help</span> 常見問題
            </h2>
            <div class="space-y-3">
                ${faqs.map((f, i) => `
                <details class="group bg-surface-container-low rounded-xl border border-surface-container-high">
                    <summary class="flex items-center justify-between cursor-pointer p-5 font-medium text-on-surface hover:text-primary transition-colors">
                        <span>${escapeHtml(f.q)}</span>
                        <span class="material-symbols-outlined text-on-surface-variant group-open:rotate-180 transition-transform">expand_more</span>
                    </summary>
                    <div class="px-5 pb-5 text-on-surface-variant leading-relaxed">${escapeHtml(f.a)}</div>
                </details>`).join('')}
            </div>
        </section>` : ''}

        <!-- Contact -->
        <section class="mb-24">
            <h2 class="text-2xl md:text-3xl font-headline font-medium text-on-surface mb-8 flex items-center gap-3">
                <span class="material-symbols-outlined text-primary">contact_phone</span> 聯絡資訊
            </h2>
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                ${phone ? `
                <div class="bg-surface-container-lowest rounded-xl p-6 border border-surface-container-high">
                    <div class="flex items-center gap-3 mb-3">
                        <div class="w-10 h-10 bg-surface-container rounded-full flex items-center justify-center">
                            <span class="material-symbols-outlined text-primary">phone</span>
                        </div>
                        <span class="text-sm text-on-surface-variant">電話</span>
                    </div>
                    <a class="font-medium text-primary hover:underline" href="tel:${escapeHtml(phone)}">${escapeHtml(phone)}</a>
                </div>` : ''}
                ${email ? `
                <div class="bg-surface-container-lowest rounded-xl p-6 border border-surface-container-high">
                    <div class="flex items-center gap-3 mb-3">
                        <div class="w-10 h-10 bg-surface-container rounded-full flex items-center justify-center">
                            <span class="material-symbols-outlined text-primary">mail</span>
                        </div>
                        <span class="text-sm text-on-surface-variant">Email</span>
                    </div>
                    <a class="font-medium text-primary hover:underline" href="mailto:${escapeHtml(email)}">${escapeHtml(email)}</a>
                </div>` : ''}
                ${venue.address ? `
                <div class="bg-surface-container-lowest rounded-xl p-6 border border-surface-container-high">
                    <div class="flex items-center gap-3 mb-3">
                        <div class="w-10 h-10 bg-surface-container rounded-full flex items-center justify-center">
                            <span class="material-symbols-outlined text-primary">location_on</span>
                        </div>
                        <span class="text-sm text-on-surface-variant">地址</span>
                    </div>
                    <div class="font-medium text-on-surface">${escapeHtml(venue.address)}</div>
                </div>` : ''}
            </div>
        </section>

        <!-- Back to dynamic page for interactive features -->
        <div class="text-center mb-16">
            <a href="../venue.html?id=${venue.id}" class="inline-flex items-center gap-2 bg-primary text-on-primary px-8 py-3 rounded-full font-medium hover:bg-brand-teal-hover transition-colors">
                <span class="material-symbols-outlined">smart_toy</span> 問 AI 助理更多問題
            </a>
        </div>

        <!-- E-E-A-T metadata -->
        <div class="text-center text-xs text-on-surface-variant mb-8 space-y-1">
            ${venueLastUpdated ? `<p>資料最後更新：${escapeHtml(venueLastUpdated)}</p>` : ''}
            <p>資料來源：場地官方網站 | 活動大師 — 活動企劃的場地知識庫</p>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-surface-container-lowest border-t border-outline-variant py-12">
        <div class="max-w-screen-2xl mx-auto px-8">
            <div class="flex flex-col md:flex-row justify-between items-center gap-8">
                <!-- Brand -->
                <div class="flex items-center gap-3">
                    <img src="../favicon.svg" alt="活動大師" class="w-8 h-8">
                    <div>
                        <div class="text-lg font-bold text-on-surface font-headline">活動大師 Activity Master</div>
                        <div class="text-sm text-on-surface-variant">台灣活動場地知識庫</div>
                    </div>
                </div>

                <!-- Links -->
                <div class="flex gap-8">
                    <a class="text-sm text-on-surface-variant hover:text-primary transition-colors" href="../index.html">首頁</a>
                    <a class="text-sm text-on-surface-variant hover:text-primary transition-colors" href="../knowledge.html">知識庫</a>
                    <a class="text-sm text-on-surface-variant hover:text-primary transition-colors" href="../taipei-event-venue.html">台北場地</a>
                    <a class="text-sm text-on-surface-variant hover:text-primary transition-colors" href="../new-taipei-event-venue.html">新北場地</a>
                </div>
            </div>

            <!-- Copyright -->
            <div class="mt-8 pt-8 border-t border-outline-variant text-center text-sm text-on-surface-variant">
                &copy; 2026 活動大師 Activity Master. All rights reserved.
            </div>
        </div>
    </footer>
</body>
</html>`;
}

// ─── Main ───

function main() {
  const venues = JSON.parse(fs.readFileSync(VENUES_FILE, 'utf8'));
  const active = venues.filter(v => v.active !== false);

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  let generated = 0;
  for (const venue of active) {
    const html = generateVenueHtml(venue);
    const outPath = path.join(OUTPUT_DIR, `${venue.id}.html`);
    fs.writeFileSync(outPath, html, 'utf8');
    generated++;
  }

  console.log(`Generated ${generated} static venue pages in ${OUTPUT_DIR}`);

  // Regenerate sitemap.xml
  const today = new Date().toISOString().split('T')[0];
  const sitemapUrls = [
    { loc: `${SITE_URL}/`, priority: '1.0', changefreq: 'weekly' },
    { loc: `${SITE_URL}/knowledge.html`, priority: '0.9', changefreq: 'weekly' },
    ...active.map(v => ({
      loc: `${SITE_URL}/venues/${v.id}`,
      priority: '0.8',
      changefreq: 'monthly'
    }))
  ];

  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapUrls.map(u => `  <url>
    <loc>${u.loc}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${u.changefreq}</changefreq>
    <priority>${u.priority}</priority>
  </url>`).join('\n')}
</urlset>`;

  fs.writeFileSync(path.join(ROOT, 'sitemap.xml'), sitemap, 'utf8');
  console.log(`Updated sitemap.xml with ${sitemapUrls.length} URLs`);
}

main();
