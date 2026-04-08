# Design System — 活動大師 Activity Master

## 1. Visual Theme & Atmosphere

活動大師是活動企劃的場地知識庫 — 一個傳達「找場地，我們幫你把關」的設計系統。視覺語言建立在深黑（`#191c1f`）與純白的對比上，搭配品牌青綠色（`#0d9488`）作為唯一的品牌強調色。這不是冷冰冰的資料庫，而是專業顧問的溫暖協助。

字體系統採用 Aeonik Pro（Display）+ Inter（Body）的組合，在 136px 的超大標題下使用 weight 500 與負向字距（-2.72px），創造強烈的視覺衝擊。這不是低調的品牌；這是一個要讓活動企劃一眼就記住的服務。

品牌色選用**深青綠**（`#0d9488`）— 專業但不冰冷，有科技感但溫暖。青綠色傳達「成功、進行中、順利」的意象，適合活動企劃的使用場景。與競品區隔：不是 Airbnb 紅、不是 Stripe 紫、不是 Vercel 黑白。

**Key Characteristics:**
- Aeonik Pro display at 136px weight 500 — billboard-scale headlines
- Near-black (`#191c1f`) + white binary with teal accent (`#0d9488`)
- Universal pill buttons (9999px radius) with generous padding (14px 32px)
- Inter for body text with positive letter-spacing (0.16px–0.24px)
- Zero shadows — depth through color contrast only
- Tight display line-heights (1.00) with relaxed body (1.50–1.56)

## 2. Color Palette & Roles

### Primary
- **Dark** (`#191c1f`): Primary dark surface, button background, near-black text
- **Pure White** (`#ffffff`): Primary light surface, card backgrounds
- **Light Surface** (`#f4f4f4`): Secondary button background, subtle surface

### Brand / Interactive（品牌青綠）
- **Brand Teal** (`#0d9488`): Primary brand color, CTA buttons, active states, links
- **Brand Teal Hover** (`#0f766e`): Darker variant for hover states
- **Brand Teal Light** (`#5eead4`): Light variant for backgrounds, badges
- **Brand Teal Surface** (`#f0fdfa`): Extremely light background tint
- **Link Blue** (`#376cd5`): Secondary links (less prominent than brand teal)

### Semantic
- **Danger Red** (`#e23b4a`): Error, destructive actions, warnings
- **Warning Orange** (`#f59e0b`): Caution, attention states
- **Success Green** (`#10b981`): Success, confirmation, positive states
- **Info Blue** (`#3b82f6`): Informational messages

### Neutral Scale
- **Near Black** (`#191c1f`): Primary text, headings
- **Dark Gray** (`#374151`): Secondary text, descriptions
- **Mid Gray** (`#6b7280`): Tertiary text, placeholders
- **Light Gray** (`#9ca3af`): Muted text, disabled states
- **Border Gray** (`#e5e7eb`): Borders, dividers
- **Background Gray** (`#f4f4f4`): Subtle backgrounds

### CSS Variables
```css
:root {
  /* Brand */
  --brand-primary: #0d9488;
  --brand-hover: #0f766e;
  --brand-light: #5eead4;
  --brand-surface: #f0fdfa;

  /* Neutral */
  --dark: #191c1f;
  --white: #ffffff;
  --light-surface: #f4f4f4;

  /* Text */
  --text-primary: #191c1f;
  --text-secondary: #374151;
  --text-tertiary: #6b7280;
  --text-muted: #9ca3af;

  /* Semantic */
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #e23b4a;
  --info: #3b82f6;

  /* Borders */
  --border: #e5e7eb;
  --border-dark: #191c1f;
}
```

## 3. Typography Rules

### Font Families
- **Display**: `Aeonik Pro` — geometric grotesque, no detected fallbacks
- **Body / UI**: `Inter` — standard system sans
- **Fallback**: `Arial` for specific button contexts

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|------|--------|-------------|----------------|-------|
| Display Mega | Aeonik Pro | 136px (8.50rem) | 500 | 1.00 (tight) | -2.72px | Stadium-scale hero |
| Display Hero | Aeonik Pro | 80px (5.00rem) | 500 | 1.00 (tight) | -0.8px | Primary hero |
| Section Heading | Aeonik Pro | 48px (3.00rem) | 500 | 1.21 (tight) | -0.48px | Feature sections |
| Sub-heading | Aeonik Pro | 40px (2.50rem) | 500 | 1.20 (tight) | -0.4px | Sub-sections |
| Card Title | Aeonik Pro | 32px (2.00rem) | 500 | 1.19 (tight) | -0.32px | Card headings |
| Feature Title | Aeonik Pro | 24px (1.50rem) | 400 | 1.33 | normal | Light headings |
| Nav / UI | Aeonik Pro | 20px (1.25rem) | 500 | 1.40 | normal | Navigation, buttons |
| Body Large | Inter | 18px (1.13rem) | 400 | 1.56 | -0.09px | Introductions |
| Body | Inter | 16px (1.00rem) | 400 | 1.50 | 0.24px | Standard reading |
| Body Semibold | Inter | 16px (1.00rem) | 600 | 1.50 | 0.16px | Emphasized body |
| Body Bold Link | Inter | 16px (1.00rem) | 700 | 1.50 | 0.24px | Bold links |

### Principles
- **Weight 500 as display default**: Aeonik Pro uses medium (500) for ALL headings — no bold. This creates authority through size and tracking, not weight.
- **Billboard tracking**: -2.72px at 136px is extremely compressed — text designed to be read at a glance, like airport signage.
- **Positive tracking on body**: Inter uses +0.16px to +0.24px, creating airy, well-spaced reading text that contrasts with the compressed headings.

## 4. Component Stylings

### Buttons

**Primary Brand Pill（品牌主按鈕）**
- Background: `#0d9488`
- Text: `#ffffff`
- Padding: 14px 32px
- Radius: 9999px (full pill)
- Hover: `#0f766e`
- Focus: `0 0 0 0.125rem` ring

**Primary Dark Pill**
- Background: `#191c1f`
- Text: `#ffffff`
- Padding: 14px 32px
- Radius: 9999px (full pill)
- Hover: opacity 0.85
- Focus: `0 0 0 0.125rem` ring

**Secondary Light Pill**
- Background: `#f4f4f4`
- Text: `#191c1f`
- Padding: 14px 34px
- Radius: 9999px
- Hover: opacity 0.85

**Outlined Pill**
- Background: transparent
- Text: `#191c1f`
- Border: `2px solid #191c1f`
- Padding: 14px 32px
- Radius: 9999px

**Outlined Brand Pill**
- Background: transparent
- Text: `#0d9488`
- Border: `2px solid #0d9488`
- Padding: 14px 32px
- Radius: 9999px
- Hover: background `#f0fdfa`

**Ghost on Dark**
- Background: `rgba(244, 244, 244, 0.1)`
- Text: `#f4f4f4`
- Border: `2px solid #f4f4f4`
- Padding: 14px 32px
- Radius: 9999px

### Cards & Containers
- Radius: 12px (small), 20px (cards)
- No shadows — flat surfaces with color contrast
- Dark and light section alternation

### Navigation
- Aeonik Pro 20px weight 500
- Clean header, hamburger toggle at 12px radius
- Pill CTAs right-aligned

## 5. Layout Principles

### Spacing System
- Base unit: 8px
- Scale: 4px, 6px, 8px, 14px, 16px, 20px, 24px, 32px, 40px, 48px, 80px, 88px, 120px
- Large section spacing: 80px–120px

### Border Radius Scale
- Standard (12px): Navigation, small buttons
- Card (20px): Feature cards
- Pill (9999px): All buttons

## 6. Depth & Elevation

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat (Level 0) | No shadow | Everything — flat design |
| Focus | `0 0 0 0.125rem` ring | Accessibility focus |
| Card Hover | `border-color: #0d9488` | Interactive feedback |

**Shadow Philosophy**: Zero shadows. Depth comes from dark/light section contrast and generous whitespace.

## 7. Do's and Don'ts

### Do
- Use Aeonik Pro weight 500 for all display headings
- Apply 9999px radius to all buttons — pill shape is universal
- Use generous button padding (14px 32px)
- Use brand teal (`#0d9488`) for primary CTAs and active states
- Apply positive letter-spacing on Inter body text
- Alternate dark (#191c1f) and light sections for visual rhythm

### Don't
- Don't use shadows — flat is the identity
- Don't use bold (700) for headings — 500 is the weight
- Don't use small buttons — generous padding is intentional
- Don't mix brand teal with other accent colors on the same page
- Don't use brand teal for body text — reserve for interactive elements

## 8. Responsive Behavior

### Breakpoints
| Name | Width | Key Changes |
|------|-------|-------------|
| Mobile Small | <400px | Compact, single column |
| Mobile | 400–720px | Standard mobile |
| Tablet | 720–1024px | 2-column layouts |
| Desktop | 1024–1280px | Standard desktop |
| Large | 1280–1920px | Full layout |

## 9. Agent Prompt Guide

### Quick Color Reference
- Brand: Teal (`#0d9488`)
- Dark: Near-black (`#191c1f`)
- Light: White (`#ffffff`)
- Surface: Light (`#f4f4f4`)
- Success: Green (`#10b981`)
- Warning: Orange (`#f59e0b`)
- Danger: Red (`#e23b4a`)

### Example Component Prompts

**Hero Section:**
```
Create a hero: white background. Headline at 136px Aeonik Pro weight 500,
line-height 1.00, letter-spacing -2.72px, #191c1f text.
Subheadline at 18px Inter, #6b7280.
Brand teal pill CTA (#0d9488, 9999px radius, 14px 32px padding, white text).
Outlined pill secondary (transparent, 2px solid #191c1f, #191c1f text).
```

**Venue Card:**
```
Build a venue card: white background, 20px radius, 1px #e5e7eb border.
Image at 4:3 ratio, 12px radius.
Venue name at 22px Aeonik Pro weight 500, #191c1f.
Meta info at 14px Inter, #6b7280.
Hover: border changes to #0d9488.
```

**Pain Point Section:**
```
Create a pain points section: #f4f4f4 background.
Section title at 48px Aeonik Pro weight 500, #191c1f, centered.
Three cards in a row, white background, 20px radius.
Each card: emoji icon, 24px title (Aeonik Pro 500), 14px description (Inter).
```

**CTA Section:**
```
Build a CTA section: #191c1f background.
Headline at 48px Aeonik Pro weight 500, white text.
Subheadline at 18px Inter, #9ca3af.
Brand teal pill button (#0d9488, white text, 9999px radius).
```

**Pill Button (Brand):**
```
Build a pill button: #0d9488 background, white text, 9999px radius,
14px 32px padding, 20px Aeonik Pro weight 500. Hover: #0f766e.
```

**Pill Button (Dark):**
```
Build a pill button: #191c1f background, white text, 9999px radius,
14px 32px padding, 20px Aeonik Pro weight 500. Hover: opacity 0.85.
```

### Iteration Guide
1. Aeonik Pro 500 for headings — never bold
2. All buttons are pills (9999px) with generous padding
3. Zero shadows — flat is the identity
4. Brand teal for primary actions, dark for secondary
5. Dark/light section alternation for visual rhythm

## 10. Page Templates

### Homepage Structure

```
┌─────────────────────────────────────────────────────────┐
│ [Navigation: Logo | 搜尋 | 場地列表 | 關於 | 登入]       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ HERO (white bg)                                         │
│                                                         │
│         找場地，不再踩坑                                │
│         （136px Aeonik Pro，#191c1f）                   │
│                                                         │
│         活動企劃的場地知識庫                             │
│         官網沒寫的潛規則，我們幫你整理好了               │
│                                                         │
│    [開始搜尋]  [下載場地清單]                           │
│     (teal bg)   (outlined)                              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ PAIN POINTS (light gray bg #f4f4f4)                     │
│                                                         │
│     你是不是也遇過這些問題？                             │
│                                                         │
│     ┌────────┐  ┌────────┐  ┌────────┐                │
│     │ 😤     │  │ 💸     │  │ 📞     │                │
│     │ 場地   │  │ 價格   │  │ 聯繫   │                │
│     │ 限制   │  │ 不透明 │  │ 效率低 │                │
│     └────────┘  └────────┘  └────────┘                │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ FEATURED VENUES (white bg)                              │
│                                                         │
│     台北精選場地                      [查看全部 →]      │
│                                                         │
│     [Card]  [Card]  [Card]  [Card]                     │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ TARGET AUDIENCE (light gray bg #f4f4f4)                 │
│                                                         │
│     我們服務誰？                                         │
│                                                         │
│     🏢 企業公關    🎯 行銷公司    👰 婚宴顧問            │
│     📚 教育機構    🎭 演藝活動    💼 會議主辦            │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ CTA SECTION (dark bg #191c1f)                           │
│                                                         │
│     準備好找場地了嗎？                                   │
│     立即開始，免費使用                                   │
│                                                         │
│     [開始搜尋]                                          │
│     (teal pill)                                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ FOOTER (dark bg #191c1f)                                │
│                                                         │
│     活動大師 | 關於我們 | 聯繫方式 | 隱私政策            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Venue Detail Page Structure

```
┌─────────────────────────────────────────────────────────┐
│ [Navigation]                                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ VENUE HERO                                              │
│                                                         │
│     [場地主圖]        圓山大飯店                        │
│                       ⭐ 4.8 · 25 會議室 · 松山區       │
│                                                         │
│                       [查看會議室] [加入比較]           │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ROOM LIST                                               │
│                                                         │
│     ┌──────────────────────────────────────────────┐   │
│     │ [圖]  國際會議廳  |  253.6坪  |  400人       │   │
│     │                 |  半日 $44,000             │   │
│     └──────────────────────────────────────────────┘   │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ AI ASSISTANT (teal bg #f0fdfa, teal border)             │
│                                                         │
│     🤖 場地 AI 助理                                     │
│                                                         │
│     [輸入你的問題...]                                   │
│                                                         │
│     「這個場地的天花板高度限制是什麼？」                │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ FOOTER                                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

**Last Updated**: 2026-04-08
**Based on**: Revolut Design System (from awesome-design-md)
**Brand Color**: Teal `#0d9488`
