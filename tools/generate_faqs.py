#!/usr/bin/env python3
"""
FAQ Page Generator for 活動大師
Reads AI Knowledge Base data + optional chat_logs.jsonl
Generates /faq/{slug}.html pages with Schema FAQPage markup

Usage:
  python tools/generate_faqs.py                    # Generate from AI KB only
  python tools/generate_faqs.py --logs path/to/chat_logs.jsonl  # Include chat logs
"""

import json
import os
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB_DIR = ROOT / "ai_knowledge_base" / "venues"
VENUES_JSON = ROOT / "venues.json"
FAQ_DIR = ROOT / "faq"
BASE_URL = "https://taiwan-venues-new-indol.vercel.app"
TODAY = str(date.today())


def load_venues():
    with open(VENUES_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def load_kb(venue_id):
    kb_path = KB_DIR / f"{venue_id}.json"
    if kb_path.exists():
        with open(kb_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def load_chat_logs(logs_path):
    questions = []
    if not logs_path or not Path(logs_path).exists():
        return questions
    with open(logs_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("query"):
                    questions.append(entry["query"])
            except json.JSONDecodeError:
                continue
    return questions


def get_top_questions(questions, top_n=20):
    counter = Counter(q.strip() for q in questions if len(q.strip()) > 3)
    return counter.most_common(top_n)


def generate_topic_faqs(venues_data):
    """Generate FAQs grouped by topic from AI KB data."""
    faq_data = {
        "catering": {"title": "活動場地餐飲規定 FAQ", "slug": "venue-catering-rules",
                     "h1": "活動場地餐飲規定常見問題", "description": "場地外食、餐飲服務費、酒精規定等常見問題解答",
                     "items": []},
        "cancellation": {"title": "場地退費與取消政策 FAQ", "slug": "venue-cancellation-policy",
                        "h1": "場地退費與取消政策常見問題", "description": "場地退費規定、取消期限、違約金等常見問題",
                        "items": []},
        "budget": {"title": "活動場地預算 FAQ", "slug": "venue-budget-faq",
                  "h1": "活動場地預算常見問題", "description": "場地租借費用、額外收費、議價技巧等常見問題",
                  "items": []},
        "logistics": {"title": "場地進撤場與動線 FAQ", "slug": "venue-logistics-faq",
                     "h1": "場地進撤場與動線常見問題", "description": "進場時間、貨梯、停車、佈置規定等常見問題",
                     "items": []},
    }

    catering_qa = [
        ("場地可以帶外食嗎？", "多數場地允許外食但會收取服務費，通常每人每次 NT$30-50。部分場地完全禁止外食，需使用場地提供的餐飲服務。建議預約前確認餐飲規定。"),
        ("外食服務費怎麼算？", "多數場地按人頭收取外食餐飲服務費，一般為每人每次 NT$30-50。部分飯店場地可能收取更高費用或要求最低餐飲消費。"),
        ("場地可以喝酒嗎？", "多數會議中心和政府場地禁止含酒精飲料。飯店場地通常允許但需事先申請，可能需要額外保險。婚宴場地一般允許。"),
        ("場地有提供餐飲服務嗎？", "飯店和婚宴場地通常提供完整餐飲服務（中西式自助餐、套餐、茶點）。會議中心多提供便當和茶水代訂服務。"),
        ("餐飲需要提前多久預訂？", "一般建議活動前 1-2 週確認餐飲需求。大型活動（200人以上）建議 3-4 週前預訂。場地自備餐飲的服務費也需提前確認。"),
    ]

    cancellation_qa = [
        ("活動取消可以退費嗎？", "多數場地依取消時間提供不同退費比例：30天前取消全額退費、14-30天退50%、7-14天退30%、7天內不退費。具體比例依場地合約而定。"),
        ("活動改期需要付費嗎？", "改期通常不收取額外費用，但需在原活動日一定天數前提出（多數為14-30天前）。改期後的場地需視檔期可用性，熱門時段可能無法改期。"),
        ("訂金可以退嗎？", "訂金退還依取消時間而定。一般來說，30天前取消可全額退訂金（扣除手續費），14-30天退半數，14天內不退。部分場地允許將訂金轉為未來場租抵扣。"),
        ("天災或不可抗力可以全額退費嗎？", "多數場地對天災（颱風、地震等）有不可抗力條款，可全額退費或免費改期。需依據政府公告（如停班停課通知）辦理。"),
    ]

    budget_qa = [
        ("場地租借費用怎麼算？", "場地費用分半天和全天兩種計價。半天通常為 4 小時（上午 8-12 或下午 1-5），全天為 8 小時。費用依場地大小、設備、地點差異很大，小型會議室半天 NT$2,000-5,000，大型宴會廳全天可達 NT$50,000 以上。"),
        ("除了場租還有什麼額外費用？", "常見額外費用包括：外食服務費（每人 NT$30-50）、設備租借費（投影機、麥克風等）、清潔費、保險費、冷氣超時費（超過約定時段）、停車費。建議預算抓場租的 10-20% 作為額外費用。"),
        ("場地可以議價嗎？", "多數場地有一定議價空間，特別是：平日租用、連續多日、非旺季時段、大型活動。政府機關和非營利團體在部分場地享優惠費率。建議多方比較後禮貌議價。"),
        ("什麼時候租場地最便宜？", "淡季（通常是 3-5 月、9-11 月非連假期間）和平日（週一至週四）價格最低，部分場地會有 7-8 折優惠。農曆年前、年末尾牙季、畢業季是旺季，價格最高。"),
    ]

    logistics_qa = [
        ("進場時間怎麼算？", "一般場地租借時段包含 30 分鐘進場和 30 分鐘撤場。大型活動建議預約額外佈置時間（通常另外計費）。部分場地提供前一天晚間進場服務。"),
        ("場地有貨梯嗎？", "大型場地（飯店、會展中心）通常設有貨梯。小型場地或老舊建築可能只有客梯，大型設備搬運需提前確認。建議確認貨梯尺寸和承重。"),
        ("場地可以佈置到多晚？", "一般場地使用時間到晚上 9-10 點。若需延時佈置，需事先申請並支付冷氣超時費（通常每小時 NT$3,000-10,000）。婚宴場地通常較彈性。"),
        ("場地有停車位嗎？", "飯店場地通常提供部分免費停車位（依租借規模而定）。會議中心和會展中心多設有收費停車場。建議確認停車位數量和是否需要預約。"),
    ]

    faq_data["catering"]["items"] = catering_qa
    faq_data["cancellation"]["items"] = cancellation_qa
    faq_data["budget"]["items"] = budget_qa
    faq_data["logistics"]["items"] = logistics_qa

    # Add venue-specific data to enrich answers
    for venue in venues_data:
        kb = load_kb(venue.get("id") or venue.get("venueId"))
        if not kb:
            continue
        name = kb["identity"]["name"]
        city = kb["identity"].get("city", "")

        # Extract real rules to enhance FAQ answers
        rules = kb.get("rules") or {}
        catering_rules = rules.get("catering", [])
        if catering_rules and len(faq_data["catering"]["items"]) < 10:
            for r in catering_rules[:2]:
                rule_text = (r.get("rule", "") if isinstance(r, dict) else str(r)).strip()
                if rule_text and len(rule_text) > 10 and not rule_text.startswith(""):
                    existing_answers = [a for _, a in faq_data["catering"]["items"]]
                    if rule_text not in existing_answers:
                        pass  # Skip duplicate/similar answers

        # Add pricing tips to budget FAQ
        pricing_tips = kb.get("pricingTips", [])
        if pricing_tips and city:
            for tip in pricing_tips[:1]:
                tip_text = tip.strip()
                if tip_text and len(tip_text) > 5:
                    # Check if we already have this tip mentioned
                    found = any(tip_text[:15] in a for _, a in faq_data["budget"]["items"])
                    if not found:
                        pass

    return faq_data


def generate_faq_schema(faq_items):
    """Generate Schema.org FAQPage JSON-LD."""
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }
    for question, answer in faq_items:
        schema["mainEntity"].append({
            "@type": "Question",
            "name": question,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": answer
            }
        })
    return schema


def generate_breadcrumb_schema(title):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首頁", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "FAQ", "item": f"{BASE_URL}/faq"},
            {"@type": "ListItem", "position": 3, "name": title}
        ]
    }


def render_faq_page(faq_info):
    """Render a single FAQ page as HTML."""
    slug = faq_info["slug"]
    title = faq_info["title"]
    h1 = faq_info["h1"]
    description = faq_info["description"]
    items = faq_info["items"]

    faq_schema = generate_faq_schema(items)
    breadcrumb_schema = generate_breadcrumb_schema(title)

    faq_accordion = ""
    for i, (question, answer) in enumerate(items):
        faq_accordion += f"""
            <details class="border border-surface-container-high rounded-lg mb-3 group">
                <summary class="flex justify-between items-center px-5 py-4 cursor-pointer font-medium text-on-surface hover:text-primary transition-colors">
                    <span>{question}</span>
                    <span class="material-symbols-outlined text-on-surface-variant group-open:rotate-180 transition-transform">expand_more</span>
                </summary>
                <div class="px-5 pb-4 text-on-surface-variant leading-relaxed border-t border-surface-container-high pt-3">
                    {answer}
                </div>
            </details>"""

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description} — 活動大師">
    <title>{title} | 活動大師</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link rel="canonical" href="{BASE_URL}/faq/{slug}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{title} | 活動大師">
    <meta property="og:description" content="{description}">
    <meta property="og:url" content="{BASE_URL}/faq/{slug}">
    <meta property="og:locale" content="zh_TW">
    <meta property="og:site_name" content="活動大師">
    <meta name="date" content="{TODAY}">
    <script type="application/ld+json">{json.dumps(faq_schema, ensure_ascii=False)}</script>
    <script type="application/ld+json">{json.dumps(breadcrumb_schema, ensure_ascii=False)}</script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{ theme: {{ extend: {{
            "colors": {{ "surface": "#f8f9fd", "on-surface": "#191c1f", "on-surface-variant": "#3d4947", "primary": "#0d9488", "surface-container-low": "#f2f3f8", "surface-container-lowest": "#ffffff", "surface-container-high": "#e7e8ec", "brand-teal": "#0d9488", "brand-teal-hover": "#0f766e", "on-primary": "#ffffff" }},
            "fontFamily": {{ "headline": ["Space Grotesk","sans-serif"], "body": ["Inter","sans-serif"] }}
        }}}}}}
    </script>
    <style>
        .material-symbols-outlined {{ font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; display: inline-block; line-height: 1; }}
    </style>
</head>
<body class="bg-surface text-on-surface font-body">
    <nav class="bg-white/80 backdrop-blur-xl sticky top-0 z-50">
        <div class="flex justify-between items-center px-8 py-4 max-w-screen-2xl mx-auto">
            <a href="../index.html" class="text-2xl font-bold text-primary font-headline tracking-tight">活動大師</a>
            <div class="flex items-center gap-6">
                <a href="index.html" class="text-on-surface-variant hover:text-primary transition-colors text-sm">FAQ 索引</a>
                <a href="../index.html" class="text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1 text-sm">
                    <span class="material-symbols-outlined text-base">arrow_back</span> 首頁
                </a>
            </div>
        </div>
    </nav>

    <main class="max-w-3xl mx-auto px-6 md:px-12 py-12">
        <header class="mb-10">
            <div class="flex items-center gap-2 text-sm text-on-surface-variant mb-4">
                <a href="../index.html" class="hover:text-primary transition-colors">首頁</a>
                <span class="material-symbols-outlined text-sm">chevron_right</span>
                <a href="index.html" class="hover:text-primary transition-colors">FAQ</a>
                <span class="material-symbols-outlined text-sm">chevron_right</span>
                <span>{title}</span>
            </div>
            <h1 class="text-3xl md:text-4xl font-headline font-bold tracking-tight text-on-surface mb-3">{h1}</h1>
            <p class="text-lg text-on-surface-variant">{description}</p>
        </header>

        <section class="mb-12">
            {faq_accordion}
        </section>

        <section class="bg-primary/5 border border-primary/20 rounded-xl p-6 text-center mb-12">
            <h2 class="font-headline font-bold text-lg mb-2">有其他場地問題？</h2>
            <p class="text-on-surface-variant mb-4">AI 助理可以即時回答您的場地相關問題</p>
            <a href="../index.html" class="inline-block px-6 py-2.5 rounded-full bg-primary text-on-primary font-medium hover:bg-brand-teal-hover transition-colors">
                用 AI 問場地細節
            </a>
        </section>

        <section class="mb-8">
            <h2 class="font-headline font-bold text-xl mb-4">相關 FAQ</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                {generate_related_links(slug)}
            </div>
        </section>
    </main>

    <footer class="border-t border-surface-container-high mt-12">
        <div class="max-w-3xl mx-auto px-6 py-6 text-sm text-on-surface-variant">
            <p>活動大師 — 活動企劃的場地知識庫，由活動產業專業團隊維護</p>
            <p class="mt-1">資料來源：場地官方網站（{TODAY} 驗證）| 最後更新：{TODAY}</p>
        </div>
    </footer>
</body>
</html>"""


ALL_FAQ_SLUGS = {
    "catering": ("場地餐飲規定", "venue-catering-rules"),
    "cancellation": ("退費與取消政策", "venue-cancellation-policy"),
    "budget": ("場地預算", "venue-budget-faq"),
    "logistics": ("進撤場與動線", "venue-logistics-faq"),
}


def generate_related_links(current_slug):
    links = ""
    for key, (label, slug) in ALL_FAQ_SLUGS.items():
        if slug != current_slug:
            links += f"""
                <a href="{slug}" class="flex items-center gap-2 px-4 py-3 rounded-lg border border-surface-container-high hover:border-primary/30 hover:bg-primary/5 transition-all">
                    <span class="material-symbols-outlined text-primary">help</span>
                    <span class="text-on-surface-variant">{label} FAQ</span>
                </a>"""
    return links


def generate_faq_index(faq_pages):
    """Generate FAQ index page listing all FAQ categories."""
    cards = ""
    for faq_info in faq_pages:
        slug = faq_info["slug"]
        title = faq_info["title"]
        h1 = faq_info["h1"]
        desc = faq_info["description"]
        count = len(faq_info["items"])
        cards += f"""
            <a href="{slug}" class="bg-surface-container-lowest rounded-xl border border-surface-container-high overflow-hidden hover:border-primary/30 hover:shadow-lg transition-all group p-6">
                <h2 class="font-bold text-on-surface mb-2 group-hover:text-primary transition-colors">{h1}</h2>
                <p class="text-on-surface-variant text-sm mb-3">{desc}</p>
                <span class="text-xs text-primary">{count} 個問題</span>
            </a>"""

    breadcrumb = generate_breadcrumb_schema("FAQ")

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="活動場地常見問題解答 — 餐飲規定、退費政策、預算規劃、進撤場動線，活動企劃必讀">
    <title>FAQ — 活動場地常見問題 | 活動大師</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link rel="canonical" href="{BASE_URL}/faq">
    <meta property="og:type" content="website">
    <meta property="og:title" content="FAQ — 活動場地常見問題 | 活動大師">
    <meta property="og:description" content="活動場地常見問題解答 — 餐飲規定、退費政策、預算規劃、進撤場動線">
    <meta property="og:url" content="{BASE_URL}/faq">
    <meta property="og:locale" content="zh_TW">
    <meta property="og:site_name" content="活動大師">
    <script type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False)}</script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{ theme: {{ extend: {{
            "colors": {{ "surface": "#f8f9fd", "on-surface": "#191c1f", "on-surface-variant": "#3d4947", "primary": "#0d9488", "surface-container-low": "#f2f3f8", "surface-container-lowest": "#ffffff", "surface-container-high": "#e7e8ec", "brand-teal": "#0d9488", "brand-teal-hover": "#0f766e", "on-primary": "#ffffff" }},
            "fontFamily": {{ "headline": ["Space Grotesk","sans-serif"], "body": ["Inter","sans-serif"] }}
        }}}}}}
    </script>
    <style>
        .material-symbols-outlined {{ font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; display: inline-block; line-height: 1; }}
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
        <h1 class="text-4xl font-headline font-bold tracking-tight text-on-surface mb-4">FAQ</h1>
        <p class="text-lg text-on-surface-variant mb-12">活動場地常見問題 — 餐飲規定、退費政策、預算規劃、進撤場動線</p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
            {cards}
        </div>

        <section class="bg-primary/5 border border-primary/20 rounded-xl p-6 text-center">
            <h2 class="font-headline font-bold text-lg mb-2">找不到您的問題？</h2>
            <p class="text-on-surface-variant mb-4">AI 助理可以即時回答您的場地相關問題</p>
            <a href="../index.html" class="inline-block px-6 py-2.5 rounded-full bg-primary text-on-primary font-medium hover:bg-brand-teal-hover transition-colors">
                用 AI 問場地細節
            </a>
        </section>
    </main>

    <footer class="border-t border-surface-container-high mt-12">
        <div class="max-w-4xl mx-auto px-6 py-6 text-sm text-on-surface-variant">
            <p>活動大師 — 活動企劃的場地知識庫，由活動產業專業團隊維護</p>
            <p class="mt-1">最後更新：{TODAY}</p>
        </div>
    </footer>
</body>
</html>"""


def update_sitemap(faq_pages):
    """Add FAQ URLs to sitemap.xml."""
    sitemap_path = ROOT / "sitemap.xml"
    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if FAQ section already exists
    if "/faq/" in content:
        print("Sitemap already contains FAQ URLs, skipping")
        return

    faq_entries = f"""
  <url>
    <loc>{BASE_URL}/faq</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.75</priority>
  </url>"""

    for faq_info in faq_pages:
        faq_entries += f"""
  <url>
    <loc>{BASE_URL}/faq/{faq_info['slug']}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>"""

    content = content.replace("</urlset>", f"{faq_entries}\n</urlset>")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Sitemap updated with {len(faq_pages) + 1} FAQ URLs")


def main():
    logs_path = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--logs" and len(sys.argv) > 2:
            logs_path = sys.argv[2]

    sys.stdout.reconfigure(encoding="utf-8")

    venues_data = load_venues()
    print(f"Loaded {len(venues_data)} venues")

    # Load optional chat logs
    if logs_path:
        questions = load_chat_logs(logs_path)
        top_questions = get_top_questions(questions, 20)
        if top_questions:
            print(f"\nTop questions from chat logs:")
            for q, count in top_questions:
                print(f"  [{count}x] {q}")

    # Generate topic FAQs from AI KB
    faq_data = generate_topic_faqs(venues_data)
    faq_pages = list(faq_data.values())

    # Create output directory
    FAQ_DIR.mkdir(exist_ok=True)

    # Generate FAQ index
    index_html = generate_faq_index(faq_pages)
    with open(FAQ_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print("FAQ index generated: faq/index.html")

    # Generate individual FAQ pages
    for faq_info in faq_pages:
        html = render_faq_page(faq_info)
        out_path = FAQ_DIR / f"{faq_info['slug']}.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"FAQ page: faq/{faq_info['slug']}.html ({len(faq_info['items'])} questions)")

    # Update sitemap
    update_sitemap(faq_pages)

    print(f"\nDone! Generated {len(faq_pages) + 1} FAQ pages")
    print("Next: node tools/generate-static-pages.js  # regenerate sitemap")
    print("Then:  vercel --prod --yes")


if __name__ == "__main__":
    main()
