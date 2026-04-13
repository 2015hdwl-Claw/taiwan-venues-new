/**
 * generate-blog.js
 * 生成 Blog 文章頁面
 * 用法：node tools/generate-blog.js
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const VENUES_FILE = path.join(ROOT, 'venues.json');
const AI_KB_DIR = path.join(ROOT, 'ai_knowledge_base', 'venues');
const SITE_URL = 'https://taiwan-venues-new-indol.vercel.app';
const TODAY = '2026-04-10';

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function loadVenues() {
  return JSON.parse(fs.readFileSync(VENUES_FILE, 'utf8')).filter(v => v.active !== false);
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

function venueLink(name, id) {
  return `<a href="/venues/${id}" class="text-primary hover:underline font-medium">${escapeHtml(name)}</a>`;
}

function cityLink(name, slug) {
  return `<a href="/${slug}" class="text-primary hover:underline font-medium">${escapeHtml(name)}</a>`;
}

// ─── Blog Articles ───

const articles = [
  {
    slug: 'taipei-top-10-venues',
    title: '台北 10 大活動場地推薦｜2026 最新評比與挑選指南',
    metaDesc: '2026台北10大活動場地推薦，從10人到2000人，涵蓋會議中心、飯店場地、展演空間。含隱藏限制、價格區間、交通資訊，幫你快速找到最適合的場地。',
    category: '清單型',
    date: '2026-04-10',
    author: '活動大師編輯團隊',
    generateContent: (venues) => {
      const taipei = venues.filter(v => v.city === '台北市');
      const top10 = taipei.sort((a, b) => getVenueMaxCap(b) - getVenueMaxCap(a)).slice(0, 10);

      let html = `<p class="text-on-surface-variant leading-relaxed mb-6">在台北找活動場地，選擇多到讓人眼花撩亂。從 10 人的部門會議到 2000 人的國際研討會，每種活動都有最適合的場地類型。這篇整理了 2026 年台北 10 大活動場地，依照活動規模和類型推薦，幫你快速找到目標。</p>`;

      top10.forEach((v, i) => {
        const kb = loadAiKb(v.id);
        const cap = getVenueMaxCap(v);
        const rooms = (v.rooms || []).length;
        const strengths = kb?.summary?.strengths || [];
        const weaknesses = kb?.summary?.weaknesses || [];
        const suitable = kb?.summary?.suitableEventTypes || [];
        const tips = kb?.pricingTips || [];

        html += `
        <div class="mb-12 pb-12 border-b border-surface-container-high last:border-0">
            <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">${i + 1}. ${venueLink(v.name, v.id)}</h2>
            <div class="flex flex-wrap gap-3 mb-4 text-sm">
                ${cap ? `<span class="bg-primary/10 text-primary px-3 py-1 rounded-full">最多 ${cap} 人</span>` : ''}
                <span class="bg-surface-container text-on-surface-variant px-3 py-1 rounded-full">${rooms} 間會議室</span>
                <span class="bg-surface-container text-on-surface-variant px-3 py-1 rounded-full">${escapeHtml(v.venueType || '場地')}</span>
                ${suitable.slice(0, 3).map(s => `<span class="bg-surface-container text-on-surface-variant px-3 py-1 rounded-full">${escapeHtml(s)}</span>`).join('')}
            </div>
            ${strengths.length ? `
            <div class="mb-3">
                <span class="text-sm font-bold text-primary">優勢：</span>
                <span class="text-sm text-on-surface-variant">${strengths.map(s => escapeHtml(s)).join('、')}</span>
            </div>` : ''}
            ${weaknesses.length ? `
            <div class="mb-3">
                <span class="text-sm font-bold text-error">注意：</span>
                <span class="text-sm text-on-surface-variant">${weaknesses.map(w => escapeHtml(w)).join('、')}</span>
            </div>` : ''}
            ${tips.length ? `
            <div class="mb-3">
                <span class="text-sm font-bold text-tertiary">省錢技巧：</span>
                <span class="text-sm text-on-surface-variant">${escapeHtml(tips[0])}</span>
            </div>` : ''}
        </div>`;
      });

      html += `
      <div class="bg-surface-container-low rounded-xl p-6 border border-surface-container-high mt-8">
          <h3 class="font-bold text-primary mb-3 flex items-center gap-2"><span class="material-symbols-outlined">tips_and_updates</span> AI 重點摘要</h3>
          <p class="text-on-surface-variant leading-relaxed">台北活動場地選擇建議：10-30 人選集思系列會議中心，CP 值最高；50-200 人選飯店中型會議廳，設備齊全；200 人以上選 ${venueLink('圓山大飯店', 1072)} 或 ${venueLink('台北國際會議中心', 1448)}。最重要的不是價格，而是確認場地的隱藏限制（天花板高度、電力負載、進場時間），這些才是活動出問題的主因。</p>
      </div>`;

      return html;
    }
  },
  {
    slug: 'small-vs-large-venue',
    title: '小型 vs 大型場地怎麼選？活動場地選擇完整指南',
    metaDesc: '小型場地和大型場地怎麼選？依照活動人數、預算、設備需求，完整分析小型場地和大場地的優缺點，幫你做出最適合的選擇。',
    category: '比較型',
    date: '2026-04-10',
    author: '活動大師編輯團隊',
    generateContent: () => {
      return `
      <p class="text-on-surface-variant leading-relaxed mb-6">選場地時最常見的錯誤不是選錯場地，而是「選了不適合規模的場地」。30 人的活動放在 200 人的場地，顯得空曠冷清；200 人的活動擠在 30 人的空間，則不舒服。這篇幫你釐清小型和大場地的選擇邏輯。</p>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">什麼是小型場地？（10-50人）</h2>
      <p class="text-on-surface-variant leading-relaxed mb-4">小型場地包括會議室、教室、共享空間。優勢是彈性高、氣氛容易營造、互動性強。適合讀書會、工作坊、部門會議、創業 pitch、小型分享會。</p>
      <div class="bg-surface-container-low rounded-xl p-5 mb-8 border border-surface-container-high">
          <h3 class="font-bold text-primary mb-2">小型場地的優勢</h3>
          <ul class="text-on-surface-variant space-y-1 list-disc list-inside">
              <li>預算友善，通常 NT$500-3,000/小時</li>
              <li>容易營造親密感和互動氛圍</li>
              <li>預訂彈性高，平日通常 1-2 週前即可</li>
              <li>場地恢復簡單，清潔費低</li>
          </ul>
      </div>
      <div class="bg-error-container/20 rounded-xl p-5 mb-8 border border-error-container/40">
          <h3 class="font-bold text-error mb-2">小型場地的陷阱</h3>
          <ul class="text-on-surface-variant space-y-1 list-disc list-inside">
              <li>「最多 30 人」的場地，舒適容量可能只有 20 人</li>
              <li>投影設備不一定含在租金內</li>
              <li>隔音品質差異很大，影響錄音和直播</li>
              <li>有些場地限用場地餐飲，不可外燴</li>
          </ul>
      </div>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">什麼是大型場地？（50人以上）</h2>
      <p class="text-on-surface-variant leading-relaxed mb-4">大型場地包括飯店宴會廳、會議中心、展演空間。優勢是設備齊全、氣派、專業服務。適合研討會、尾牙、婚宴、發表會、股東會。</p>
      <div class="bg-surface-container-low rounded-xl p-5 mb-8 border border-surface-container-high">
          <h3 class="font-bold text-primary mb-2">大型場地的優勢</h3>
          <ul class="text-on-surface-variant space-y-1 list-disc list-inside">
              <li>設備齊全（投影、音響、燈光通常內建）</li>
              <li>專業服務團隊（場控、餐飲、清潔）</li>
              <li>品牌形象加分（五星飯店、知名場館）</li>
              <li>可彈性調整座位排列</li>
          </ul>
      </div>
      <div class="bg-error-container/20 rounded-xl p-5 mb-8 border border-error-container/40">
          <h3 class="font-bold text-error mb-2">大型場地的陷阱</h3>
          <ul class="text-on-surface-variant space-y-1 list-disc list-inside">
              <li>需提前 2-6 個月預訂，旺季更久</li>
              <li>隱藏費用多（清潔費、冷氣超時、設備租借、保險）</li>
              <li>限用飯店餐飲，不可外燴</li>
              <li>取消罰則嚴格，7 天內可能不退款</li>
          </ul>
      </div>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">快速決策表</h2>
      <div class="overflow-x-auto mb-8">
          <table class="w-full text-sm border-collapse">
              <thead>
                  <tr class="bg-surface-container">
                      <th class="text-left p-3 border border-surface-container-high">考量因素</th>
                      <th class="text-left p-3 border border-surface-container-high">選小型</th>
                      <th class="text-left p-3 border border-surface-container-high">選大型</th>
                  </tr>
              </thead>
              <tbody class="text-on-surface-variant">
                  <tr><td class="p-3 border border-surface-container-high">人數</td><td class="p-3 border border-surface-container-high">10-50人</td><td class="p-3 border border-surface-container-high">50人以上</td></tr>
                  <tr><td class="p-3 border border-surface-container-high">預算</td><td class="p-3 border border-surface-container-high">NT$5,000 以內</td><td class="p-3 border border-surface-container-high">NT$10,000 以上</td></tr>
                  <tr><td class="p-3 border border-surface-container-high">活動類型</td><td class="p-3 border border-surface-container-high">會議、工作坊、讀書會</td><td class="p-3 border border-surface-container-high">研討會、宴會、發表會</td></tr>
                  <tr><td class="p-3 border border-surface-container-high">準備時間</td><td class="p-3 border border-surface-container-high">1-2 週</td><td class="p-3 border border-surface-container-high">2-6 個月</td></tr>
                  <tr><td class="p-3 border border-surface-container-high">互動需求</td><td class="p-3 border border-surface-container-high">高（討論、實作）</td><td class="p-3 border border-surface-container-high">低（演講、表演）</td></tr>
              </tbody>
          </table>
      </div>

      <p class="text-on-surface-variant leading-relaxed mb-6">不確定哪種適合？查看 ${cityLink('台北小型場地推薦', 'small-event-venue')} 或 ${cityLink('台北大型場地推薦', 'taipei-event-venue')}，用 AI 助理描述你的活動需求，獲得最適合的推薦。</p>

      <div class="bg-surface-container-low rounded-xl p-6 border border-surface-container-high mt-8">
          <h3 class="font-bold text-primary mb-3 flex items-center gap-2"><span class="material-symbols-outlined">tips_and_updates</span> AI 重點摘要</h3>
          <p class="text-on-surface-variant leading-relaxed">小型場地重互動、預算友善、彈性高。大型場地重氣派、設備齊、服務專業。選擇關鍵不是「多大」，而是「多適合」。30人活動塞進200人場地 = 浪費錢。200人活動擠進30人空間 = 災難。先用確認人數和活動目的，再找對應規模的場地。</p>
      </div>`;
    }
  },
  {
    slug: 'venue-budget-guide',
    title: '活動場地預算怎麼抓？2026 台灣場地租借費用完整指南',
    metaDesc: '活動場地預算怎麼抓？2026台灣場地租借費用指南，從小型會議室到大型宴會廳，完整價格區間、隱藏費用清單、省錢技巧。',
    category: '教學型',
    date: '2026-04-10',
    author: '活動大師編輯團隊',
    generateContent: () => {
      return `
      <p class="text-on-surface-variant leading-relaxed mb-6">活動場地費用是活動預算中最大的變數。同樣 50 人的場地，價格可以從 NT$3,000 到 NT$50,000，差了 15 倍。這篇幫你拆解場地費用的組成，讓你精準抓預算，避免簽約後才發現隱藏費用。</p>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">場地租借費用參考（2026）</h2>
      <div class="overflow-x-auto mb-8">
          <table class="w-full text-sm border-collapse">
              <thead>
                  <tr class="bg-surface-container">
                      <th class="text-left p-3 border border-surface-container-high">場地類型</th>
                      <th class="text-left p-3 border border-surface-container-high">人數</th>
                      <th class="text-left p-3 border border-surface-container-high">計價方式</th>
                      <th class="text-left p-3 border border-surface-container-high">價格區間</th>
                  </tr>
              </thead>
              <tbody class="text-on-surface-variant">
                  <tr><td class="p-3 border border-surface-container-high">共享空間/教室</td><td class="p-3 border border-surface-container-high">10-30人</td><td class="p-3 border border-surface-container-high">每小時</td><td class="p-3 border border-surface-container-high">NT$300-1,500</td></tr>
                  <tr><td class="p-3 border border-surface-container-high">會議中心</td><td class="p-3 border border-surface-container-high">20-200人</td><td class="p-3 border border-surface-container-high">半天/全天</td><td class="p-3 border border-surface-container-high">NT$3,000-30,000</td></tr>
                  <tr><td class="p-3 border border-surface-container-high">飯店會議廳</td><td class="p-3 border border-surface-container-high">30-500人</td><td class="p-3 border border-surface-container-high">半天/全天</td><td class="p-3 border border-surface-container-high">NT$10,000-100,000</td></tr>
                  <tr><td class="p-3 border border-surface-container-high">大型宴會廳</td><td class="p-3 border border-surface-container-high">200-2000人</td><td class="p-3 border border-surface-container-high">全天/專案</td><td class="p-3 border border-surface-container-high">NT$50,000-500,000+</td></tr>
                  <tr><td class="p-3 border border-surface-container-high">展演空間</td><td class="p-3 border border-surface-container-high">依場地</td><td class="p-3 border border-surface-container-high">天/週</td><td class="p-3 border border-surface-container-high">NT$20,000-200,000/天</td></tr>
              </tbody>
          </table>
      </div>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">場地費用 = 租金 + 隱藏費用</h2>
      <p class="text-on-surface-variant leading-relaxed mb-4">很多人只看場地租金，忽略了隱藏費用。實際總支出可能是租金的 1.5-2 倍。</p>
      <div class="bg-error-container/20 rounded-xl p-5 mb-8 border border-error-container/40">
          <h3 class="font-bold text-error mb-3">常見隱藏費用清單</h3>
          <ul class="text-on-surface-variant space-y-2 list-disc list-inside">
              <li><strong>清潔費</strong>：NT$2,000-10,000，有些場地「含」但有些另計</li>
              <li><strong>冷氣超時費</strong>：通常只含 8 小時，每多 1 小時 NT$500-3,000</li>
              <li><strong>設備租借費</strong>：投影機、音響、麥克風可能另計 NT$1,000-5,000/組</li>
              <li><strong>電力超載費</strong>：大型活動使用大量燈光音響時加收</li>
              <li><strong>保險費</strong>：NT$3,000-20,000，大型活動通常必須保</li>
              <li><strong>場地恢復費</strong>：佈置拆除後恢復原狀的費用</li>
              <li><strong>停車位</strong>：有些場地停車位有限，需額外租用</li>
              <li><strong>保證金</strong>：場地租金的 10-30%，活動後無損壞才退還</li>
          </ul>
      </div>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">5 個省錢技巧</h2>
      <ol class="text-on-surface-variant space-y-4 mb-8 list-decimal list-inside leading-relaxed">
          <li><strong>選平日而非週末</strong>：週一到週四的場地價格通常比週五、六低 20-40%</li>
          <li><strong>選離峰時段</strong>：早上 9 點前的場次、下午 2-5 點的時段，議價空間大</li>
          <li><strong>住宿 + 場地套裝</strong>：飯店的「住宿 + 會議室」套裝通常比單租場地划算</li>
          <li><strong>多家場地同時租用</strong>：如果活動需要多個廳，一起租可以議價</li>
          <li><strong>確認「含」什麼</strong>：問清楚租金含不含冷氣、設備、茶點、清潔，不要假設</li>
      </ol>

      <p class="text-on-surface-variant leading-relaxed mb-6">想看更多場地的具體價格？查看 ${cityLink('台北活動場地', 'taipei-event-venue')} 或 ${cityLink('新北活動場地', 'new-taipei-event-venue')}，每個場地都有完整的費用資訊。也歡迎用 AI 助理直接問場地的隱藏費用。</p>

      <div class="bg-surface-container-low rounded-xl p-6 border border-surface-container-high mt-8">
          <h3 class="font-bold text-primary mb-3 flex items-center gap-2"><span class="material-symbols-outlined">tips_and_updates</span> AI 重點摘要</h3>
          <p class="text-on-surface-variant leading-relaxed">活動場地總費用 = 租金 x 1.5 到 2。租金只是基本，隱藏費用（清潔、冷氣、設備、保險、保證金）才是预算失控的主因。省錢最有效的方法：選平日、問清楚「含什麼」、用套裝方案。永遠在簽約前拿到完整費用明細。</p>
      </div>`;
    }
  },
  {
    slug: 'banqiao-hot-spaces',
    title: '板橋熱門活動空間推薦｜會議・婚宴・展演場地整理',
    metaDesc: '板橋活動場地推薦，整理新北市板橋區熱門活動空間，含會議室、婚宴場地、宴會廳。CP值比台北高20-40%，交通方便。',
    category: '清單型',
    date: '2026-04-10',
    author: '活動大師編輯團隊',
    generateContent: (venues) => {
      const newTaipei = venues.filter(v => v.city === '新北市');

      let html = `<p class="text-on-surface-variant leading-relaxed mb-6">板橋是新北市最適合辦活動的區域，高鐵、台鐵、捷運三鐵共構，交通比很多台北場地還方便。更重要的是，價格比台北同級場地便宜 20-40%，同樣預算可以租到更大、更好的空間。</p>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">為什麼選板橋？</h2>
      <ul class="text-on-surface-variant space-y-2 mb-8 list-disc list-inside leading-relaxed">
          <li><strong>交通便利</strong>：板橋車站三鐵共構，北北基桃都方便到達</li>
          <li><strong>價格實惠</strong>：比台北同級場地便宜 20-40%</li>
          <li><strong>停車方便</strong>：多數場地停車位比台北充足</li>
          <li><strong>場地多元</strong>：從婚宴會館到飯店會議室都有</li>
      </ul>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">新北精選場地</h2>`;

      newTaipei.forEach(v => {
        const kb = loadAiKb(v.id);
        const cap = getVenueMaxCap(v);
        const rooms = (v.rooms || []).length;
        const strengths = kb?.summary?.strengths || [];

        html += `
        <div class="mb-8 pb-8 border-b border-surface-container-high">
            <h3 class="text-xl font-bold mb-2">${venueLink(v.name, v.id)}</h3>
            <div class="flex flex-wrap gap-3 mb-3 text-sm">
                ${cap ? `<span class="bg-primary/10 text-primary px-3 py-1 rounded-full">最多 ${cap} 人</span>` : ''}
                <span class="bg-surface-container text-on-surface-variant px-3 py-1 rounded-full">${rooms} 間會議室</span>
                <span class="bg-surface-container text-on-surface-variant px-3 py-1 rounded-full">${escapeHtml(v.venueType || '場地')}</span>
            </div>
            ${strengths.length ? `<p class="text-sm text-on-surface-variant"><span class="font-bold text-primary">亮點：</span>${strengths.slice(0, 2).map(s => escapeHtml(s)).join('、')}</p>` : ''}
        </div>`;
      });

      html += `
      <p class="text-on-surface-variant leading-relaxed mb-6">更多新北場地資訊，查看 ${cityLink('新北活動場地推薦', 'new-taipei-event-venue')}。也歡迎用 AI 助理描述你的活動需求，獲得最適合的場地推薦。</p>

      <div class="bg-surface-container-low rounded-xl p-6 border border-surface-container-high mt-8">
          <h3 class="font-bold text-primary mb-3 flex items-center gap-2"><span class="material-symbols-outlined">tips_and_updates</span> AI 重點摘要</h3>
          <p class="text-on-surface-variant leading-relaxed">板橋是台北活動場地的最佳替代選擇。三鐵共構交通便利，價格比台北低 20-40%，停車位充足。新北市共有 10 個優質場地，涵蓋婚宴會館、飯店會議室和展覽中心。選板橋場地時注意確認捷運站步行距離和周邊餐飲選擇。</p>
      </div>`;

      return html;
    }
  },
  {
    slug: 'seminar-equipment',
    title: '講座場地必備設備清單｜投影、音響、網路一次搞懂',
    metaDesc: '講座場地必備設備完整清單：投影機流明、音響系統、網路頻寬、直播設備。教你確認場地設備是否足夠，避免活動當天出問題。',
    category: '教學型',
    date: '2026-04-10',
    author: '活動大師編輯團隊',
    generateContent: () => {
      return `
      <p class="text-on-surface-variant leading-relaxed mb-6">辦講座最怕的不是沒人來，而是設備出問題。投影機太暗看不清楚、麥克風突然沒聲音、網路卡到直播斷線。這篇整理講座場地的必備設備清單，讓你在簽約前就確認場地能滿足需求。</p>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">1. 投影設備</h2>
      <p class="text-on-surface-variant leading-relaxed mb-4">投影機是講座的核心設備。很多場地說「有投影機」但沒說規格，結果活動當天才發現不夠亮。</p>
      <div class="overflow-x-auto mb-8">
          <table class="w-full text-sm border-collapse">
              <thead>
                  <tr class="bg-surface-container">
                      <th class="text-left p-3 border border-surface-container-high">場地大小</th>
                      <th class="text-left p-3 border border-surface-container-high">建議流明</th>
                      <th class="text-left p-3 border border-surface-container-high">螢幕尺寸</th>
                  </tr>
              </thead>
              <tbody class="text-on-surface-variant">
                  <tr><td class="p-3 border border-surface-container-high">小型（10-30人）</td><td class="p-3 border border-surface-container-high">2,000-3,000 流明</td><td class="p-3 border border-surface-container-high">60-80 吋</td></tr>
                  <tr><td class="p-3 border border-surface-container-high">中型（30-80人）</td><td class="p-3 border border-surface-container-high">3,000-5,000 流明</td><td class="p-3 border border-surface-container-high">100-120 吋</td></tr>
                  <tr><td class="p-3 border border-surface-container-high">大型（80人+）</td><td class="p-3 border border-surface-container-high">5,000+ 流明</td><td class="p-3 border border-surface-container-high">150 吋以上</td></tr>
              </tbody>
          </table>
      </div>
      <div class="bg-surface-container-low rounded-xl p-4 mb-8 border border-surface-container-high text-sm text-on-surface-variant">
          <strong class="text-primary">確認重點：</strong>投影機連接方式（HDMI / VGA / 無線）、是否有投影幕（不是白牆）、燈泡壽命（舊燈泡會變暗）
      </div>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">2. 音響系統</h2>
      <p class="text-on-surface-variant leading-relaxed mb-4">超過 30 人的場地，不靠麥克風後排會聽不到。音響系統的好壞直接影響觀眾體驗。</p>
      <ul class="text-on-surface-variant space-y-2 mb-8 list-disc list-inside leading-relaxed">
          <li><strong>無線麥克風</strong>：至少 2 支（講者 + 主持人），確認是領夾式或手持式</li>
          <li><strong>音源輸入</strong>：確認有 3.5mm / 藍牙輸入，播放影片或音樂用</li>
          <li><strong>監聽喇叭</strong>：大型場地需要舞台監聽，講者才能聽到自己聲音</li>
          <li><strong>混音器</strong>：多個音源（麥克風 + 電腦 + 影片）時需要</li>
      </ul>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">3. 網路與直播</h2>
      <p class="text-on-surface-variant leading-relaxed mb-4">疫情後，很多講座需要直播或錄影。場地的網路品質成了關鍵。</p>
      <ul class="text-on-surface-variant space-y-2 mb-8 list-disc list-inside leading-relaxed">
          <li><strong>有線網路</strong>：直播一定要用有線，WiFi 不穩定</li>
          <li><strong>頻寬</strong>：直播建議上傳頻寬 10Mbps 以上</li>
          <li><strong>WiFi</strong>：確認場地 WiFi 可供多少裝置同時連線（觀眾也可能需要）</li>
          <li><strong>錄影設備</strong>：如果需要錄影，確認場地是否允許架設腳架</li>
      </ul>

      <h2 class="text-2xl font-headline font-bold text-on-surface mb-4">4. 其他設備</h2>
      <ul class="text-on-surface-variant space-y-2 mb-8 list-disc list-inside leading-relaxed">
          <li><strong>白板 / 玻璃牆</strong>：互動型講座必備，確認有白板筆</li>
          <li><strong>電源插座</strong>：確認講台附近有插座，筆電和設備供電用</li>
          <li><strong>空調控制</strong>：確認可以獨立調整冷氣溫度，人多的場地容易悶熱</li>
          <li><strong>指標系統</strong>：場館指標是否清楚，避免參加者迷路</li>
      </ul>

      <p class="text-on-surface-variant leading-relaxed mb-6">想找設備齊全的講座場地？查看 ${cityLink('講座場地推薦', 'seminar-venue')} 或用 AI 助理直接問場地的設備規格。</p>

      <div class="bg-surface-container-low rounded-xl p-6 border border-surface-container-high mt-8">
          <h3 class="font-bold text-primary mb-3 flex items-center gap-2"><span class="material-symbols-outlined">tips_and_updates</span> AI 重點摘要</h3>
          <p class="text-on-surface-variant leading-relaxed">講座場地設備確認三步驟：一看投影（流明夠不夠、連接方式），二聽音響（麥克風數量、有無混音器），三測網路（有線接孔在哪、頻寬多少）。永遠在活動前一天到場測試設備，不要活動當天才第一次開機。</p>
      </div>`;
    }
  }
];

// ─── HTML Generator ───

function generateBlogHtml(article) {
  const venues = loadVenues();
  const content = article.generateContent(venues);

  const jsonLds = [
    { "@context": "https://schema.org", "@type": "Article",
      "headline": article.title,
      "datePublished": article.date,
      "dateModified": article.date,
      "author": { "@type": "Organization", "name": "活動大師" },
      "publisher": { "@type": "Organization", "name": "活動大師 Activity Master", "logo": { "@type": "ImageObject", "url": `${SITE_URL}/favicon.svg` } },
      "description": article.metaDesc,
      "mainEntityOfPage": `${SITE_URL}/blog/${article.slug}`
    },
    { "@context": "https://schema.org", "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "首頁", "item": `${SITE_URL}/` },
        { "@type": "ListItem", "position": 2, "name": "Blog", "item": `${SITE_URL}/blog` },
        { "@type": "ListItem", "position": 3, "name": article.title, "item": `${SITE_URL}/blog/${article.slug}` }
      ]
    }
  ];

  return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="${escapeHtml(article.metaDesc)}">
    <title>${escapeHtml(article.title)} | 活動大師 Blog</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link rel="canonical" href="${SITE_URL}/blog/${article.slug}">
    <meta property="og:type" content="article">
    <meta property="og:title" content="${escapeHtml(article.title)}">
    <meta property="og:description" content="${escapeHtml(article.metaDesc)}">
    <meta property="og:url" content="${SITE_URL}/blog/${article.slug}">
    <meta property="og:image" content="${SITE_URL}/social/images/og-brand.png">
    <meta property="og:locale" content="zh_TW">
    <meta property="og:site_name" content="活動大師">
    <meta name="twitter:card" content="summary_large_image">

    ${jsonLds.map(s => `<script type="application/ld+json">${JSON.stringify(s)}</script>`).join('\n    ')}

    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            darkMode: "class",
            theme: { extend: {
                "colors": {
                    "surface-container-low": "#f2f3f8", "inverse-on-surface": "#eff1f5",
                    "on-primary": "#ffffff", "surface-variant": "#e1e2e6",
                    "on-surface-variant": "#3d4947", "inverse-primary": "#6bd8cb",
                    "inverse-surface": "#2e3134", "surface-bright": "#f8f9fd",
                    "primary-container": "#0d9488", "surface-dim": "#d8dade",
                    "surface": "#f8f9fd", "error": "#ba1a1a", "outline": "#6d7a77",
                    "tertiary": "#924628", "primary": "#0d9488",
                    "on-surface": "#191c1f", "background": "#f8f9fd",
                    "surface-container": "#eceef2", "tertiary-container": "#b05e3d",
                    "surface-container-high": "#e7e8ec", "error-container": "#ffdad6",
                    "on-primary-container": "#f4fffc", "on-error": "#ffffff",
                    "on-secondary": "#ffffff", "on-secondary-container": "#456b66",
                    "on-error-container": "#93000a", "surface-container-lowest": "#ffffff",
                    "secondary-container": "#c2ebe3", "surface-container-highest": "#e1e2e6",
                    "brand-teal": "#0d9488", "brand-teal-hover": "#0f766e"
                },
                "borderRadius": { "DEFAULT": "1rem", "lg": "2rem", "xl": "3rem", "full": "9999px" },
                "fontFamily": { "headline": ["Space Grotesk","sans-serif"], "body": ["Inter","sans-serif"] }
            }}
        }
    </script>
    <style>
        .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; display: inline-block; line-height: 1; }
    </style>
</head>
<body class="bg-surface text-on-surface font-body">

    <!-- Navigation -->
    <nav class="bg-white/80 backdrop-blur-xl sticky top-0 z-50">
        <div class="flex justify-between items-center px-8 py-4 max-w-screen-2xl mx-auto">
            <a href="../index.html" class="text-2xl font-bold text-primary font-headline tracking-tight">活動大師</a>
            <div class="flex items-center gap-6">
                <a href="index.html" class="text-primary font-bold font-headline text-sm uppercase tracking-widest">Blog</a>
                <a href="../index.html" class="text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1 text-sm">
                    <span class="material-symbols-outlined text-base">arrow_back</span> 首頁
                </a>
            </div>
        </div>
    </nav>

    <main class="max-w-3xl mx-auto px-6 md:px-12 py-12">
        <!-- Article Header -->
        <header class="mb-12">
            <div class="flex items-center gap-3 text-sm text-on-surface-variant mb-4">
                <span class="bg-primary/10 text-primary px-3 py-1 rounded-full">${escapeHtml(article.category)}</span>
                <time datetime="${article.date}">${article.date}</time>
                <span>by ${escapeHtml(article.author)}</span>
            </div>
            <h1 class="text-3xl md:text-4xl font-headline font-bold tracking-tight text-on-surface">${escapeHtml(article.title)}</h1>
        </header>

        <!-- Article Content -->
        <article class="mb-16">
${content}
        </article>

        <!-- CTA -->
        <div class="text-center mb-16">
            <a href="../index.html" class="inline-flex items-center gap-2 bg-primary text-on-primary px-8 py-3 rounded-full font-medium hover:bg-brand-teal-hover transition-colors">
                <span class="material-symbols-outlined">smart_toy</span> 用 AI 助理找場地
            </a>
        </div>

        <!-- Related Links -->
        <div class="grid sm:grid-cols-2 gap-4 mb-16">
            <a href="../taipei-event-venue" class="bg-surface-container-low rounded-xl p-6 border border-surface-container-high hover:border-primary/40 transition-colors">
                <span class="material-symbols-outlined text-primary mb-2">location_city</span>
                <div class="font-bold text-on-surface">台北活動場地</div>
                <div class="text-sm text-on-surface-variant">23 個場地推薦</div>
            </a>
            <a href="../new-taipei-event-venue" class="bg-surface-container-low rounded-xl p-6 border border-surface-container-high hover:border-primary/40 transition-colors">
                <span class="material-symbols-outlined text-primary mb-2">apartment</span>
                <div class="font-bold text-on-surface">新北活動場地</div>
                <div class="text-sm text-on-surface-variant">10 個場地推薦</div>
            </a>
        </div>

        <!-- E-E-A-T -->
        <div class="text-center text-xs text-on-surface-variant space-y-1">
            <p>資料最後更新：${article.date}</p>
            <p>資料來源：場地官方網站 | 活動大師 — 活動企劃的場地知識庫</p>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-[#191c1f] flex flex-col md:flex-row justify-between items-center px-12 py-16 w-full mt-16">
        <div class="flex flex-col items-center md:items-start gap-4 mb-8 md:mb-0">
            <span class="text-xl font-bold text-white font-headline">活動大師</span>
            <p class="text-neutral-400 font-headline text-sm uppercase tracking-widest opacity-80">&copy; 2026 活動大師. All rights reserved.</p>
        </div>
        <div class="flex gap-8">
            <a class="text-neutral-400 hover:text-teal-400 transition-colors font-headline text-sm uppercase tracking-widest opacity-80 hover:opacity-100" href="../index.html">首頁</a>
            <a class="text-neutral-400 hover:text-teal-400 transition-colors font-headline text-sm uppercase tracking-widest opacity-80 hover:opacity-100" href="index.html">Blog</a>
        </div>
    </footer>
</body>
</html>`;
}

// ─── Blog Index ───

function generateBlogIndex() {
  const cards = articles.map(a => `
            <a href="${a.slug}" class="bg-surface-container-lowest rounded-xl border border-surface-container-high overflow-hidden hover:border-primary/30 hover:shadow-lg transition-all group">
                <div class="p-6">
                    <div class="flex items-center gap-3 text-xs text-on-surface-variant mb-3">
                        <span class="bg-primary/10 text-primary px-2 py-0.5 rounded-full">${escapeHtml(a.category)}</span>
                        <time>${a.date}</time>
                    </div>
                    <h2 class="font-bold text-on-surface mb-2 group-hover:text-primary transition-colors line-clamp-2">${escapeHtml(a.title)}</h2>
                    <p class="text-sm text-on-surface-variant line-clamp-2">${escapeHtml(a.metaDesc)}</p>
                </div>
            </a>`).join('\n');

  return `<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="活動大師 Blog — 活動場地挑選指南、省錢技巧、設備建議，活動企劃的實用知識庫。">
    <title>Blog — 活動場地知識 | 活動大師</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link rel="canonical" href="${SITE_URL}/blog">
    <meta property="og:type" content="website">
    <meta property="og:title" content="Blog — 活動場地知識 | 活動大師">
    <meta property="og:description" content="活動場地挑選指南、省錢技巧、設備建議，活動企劃的實用知識庫。">
    <meta property="og:url" content="${SITE_URL}/blog">
    <meta property="og:locale" content="zh_TW">
    <meta property="og:site_name" content="活動大師">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
    <script>
        tailwind.config = { theme: { extend: {
            "colors": { "surface": "#f8f9fd", "on-surface": "#191c1f", "on-surface-variant": "#3d4947", "primary": "#0d9488", "surface-container-low": "#f2f3f8", "surface-container-lowest": "#ffffff", "surface-container-high": "#e7e8ec", "brand-teal": "#0d9488", "brand-teal-hover": "#0f766e", "on-primary": "#ffffff" },
            "fontFamily": { "headline": ["Space Grotesk","sans-serif"], "body": ["Inter","sans-serif"] }
        }}}
    </script>
    <style>
        .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; display: inline-block; line-height: 1; }
        .line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    </style>
</head>
<body class="bg-surface text-on-surface font-body">
    <nav class="bg-white/80 backdrop-blur-xl sticky top-0 z-50">
        <div class="flex justify-between items-center px-8 py-4 max-w-screen-2xl mx-auto">
            <a href="../index.html" class="text-2xl font-bold text-primary font-headline tracking-tight">活動大師</a>
            <a href="../index.html" class="text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1 text-sm">
                <span class="material-symbols-outlined text-base">arrow_back</span> 首頁
            </a>
        </div>
    </nav>
    <main class="max-w-4xl mx-auto px-6 md:px-12 py-12">
        <h1 class="text-4xl font-headline font-bold tracking-tight text-on-surface mb-4">Blog</h1>
        <p class="text-lg text-on-surface-variant mb-12">活動場地挑選指南、省錢技巧、設備建議 — 活動企劃的實用知識</p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
${cards}
        </div>
    </main>
    <footer class="bg-[#191c1f] flex flex-col md:flex-row justify-between items-center px-12 py-16 w-full mt-16">
        <div class="flex flex-col items-center md:items-start gap-4 mb-8 md:mb-0">
            <span class="text-xl font-bold text-white font-headline">活動大師</span>
            <p class="text-neutral-400 font-headline text-sm uppercase tracking-widest opacity-80">&copy; 2026 活動大師. All rights reserved.</p>
        </div>
        <div class="flex gap-8">
            <a class="text-neutral-400 hover:text-teal-400 transition-colors font-headline text-sm uppercase tracking-widest opacity-80 hover:opacity-100" href="../index.html">首頁</a>
        </div>
    </footer>
</body>
</html>`;
}

// ─── Main ───

function main() {
  // Generate blog index
  fs.writeFileSync(path.join(ROOT, 'blog', 'index.html'), generateBlogIndex(), 'utf8');
  console.log('Blog index generated');

  // Generate articles
  for (const article of articles) {
    const html = generateBlogHtml(article);
    const outPath = path.join(ROOT, 'blog', `${article.slug}.html`);
    fs.writeFileSync(outPath, html, 'utf8');
    console.log(`Article: blog/${article.slug}.html (${(html.length / 1024).toFixed(0)} KB)`);
  }

  console.log(`\nGenerated ${articles.length + 1} blog pages`);
}

main();
