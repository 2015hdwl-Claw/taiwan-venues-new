"""Update venues 1509, 1514, 1515 (晶宴會館) enrichment data."""
import json, os

VENUES_FILE = os.path.join(os.path.dirname(__file__), '..', 'venues.json')

def main():
    with open(VENUES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    venues = {v['id']: v for v in data}

    # === 1509 晶宴(峇里斯莊園) ===
    v = venues[1509]
    v['description'] = '峇里斯莊園佔地2,000坪，是新北市婚宴地標之一，宴會廳以世界級劇院為設計概念，結合人文美學與建築工藝，挑高10米的豪華接待門廳、宮廷古典列柱廊道、頂級水晶吊燈，勾勒極致奢華的時尚氛圍，是不能錯過的新北婚宴場地。'
    v['nameEn'] = 'Amazing Hall Bali Manor'
    v['highlights'] = [
        '佔地2,000坪，新北市婚宴地標',
        '世界級劇院式設計概念',
        '挑高10米豪華接待門廳',
        '宮廷古典列柱廊道',
        '頂級水晶吊燈',
        '御嵿國際集團旗下品牌',
        '首創劇場式宴會廳與婚宴秘書服務'
    ]
    v['image'] = 'https://i0.wp.com/www.amazinghall.com.tw/wp-content/uploads/2024/12/1F-%E6%88%B6%E5%A4%96%E8%AD%89%E5%A9%9A%E5%8D%80-1024x683.jpg'
    v['images'] = {
        'main': v['image'],
        'gallery': [
            'https://i0.wp.com/www.amazinghall.com.tw/wp-content/uploads/2023/05/%E5%B3%87%E9%87%8C%E6%96%AF%E5%A9%9A%E7%A6%AE-1.jpeg'
        ],
        'verified': True,
        'verifiedAt': '2026-04-11'
    }
    v['rules'] = {
        'catering': [{'rule': '晶宴提供專屬婚宴秘書服務與晶緻美饌宴席料理，菜色依專案而異，需洽詢各館', 'source': '官網首頁', 'confidence': 'medium'}],
        'decoration': [{'rule': '需洽詢場地', 'source': '官網未提供', 'confidence': 'low'}],
        'sound': [{'rule': '配備頂級聲光設備，結合舞台設計', 'source': '官網首頁品牌介紹', 'confidence': 'medium'}],
        'loadIn': [{'rule': '需洽詢場地', 'source': '官網未提供', 'confidence': 'low'}],
        'cancellation': [{'rule': '需洽詢場地', 'source': '官網未提供', 'confidence': 'low'}],
        'insurance': [{'rule': '需洽詢場地', 'source': '官網未提供', 'confidence': 'low'}]
    }
    v['risks'] = {
        'bookingLeadTime': '建議提前3-6個月預訂',
        'peakSeasons': ['農曆年前尾牙季', '婚宴旺季(9-12月)'],
        'commonIssues': ['佔地廣大(2,000坪)，不同宴會廳之間可能互相干擾', '非捷運站旁，賓客交通需安排']
    }
    v['pricingTips'] = ['晶宴為連鎖婚宴品牌，價格屬中高檔定位', '建議詢問平日/假日價差及專案優惠', '官網有工商優惠方案，企業活動可洽詢']
    v['contact'] = {'phone': '(02)2992-0033', 'email': ''}
    v['accessInfo'] = '新北市新莊區思源路40號，近台65線快速道路及中山高速公路'
    v['transportation'] = {'mrt': '台北捷運新莊線（頭前庄站）', 'parking': '需洽詢場地'}
    v['loadIn'] = '佔地2,000坪大型場館，進場動線需洽詢'
    v['limitations'] = '晶宴提供自有宴席料理，原則上不開放外燴'
    v['verified'] = True
    v['lastUpdated'] = '2026-04-11'
    v['lastVerified'] = '2026-04-11'
    print('1509 done')

    # === 1514 晶宴(台茂館) — 可能已停業 ===
    v2 = venues[1514]
    v2['description'] = '台茂館目前已不在晶宴會館官方網站的館別列表中。官網目前列出7家分館為：民權館、日光香頌、峇里斯莊園、中和館、府中館、桃園館、御豐館。台茂館可能已結束營業或更名，需向晶宴會館確認。'
    v2['nameEn'] = 'Amazing Hall Tai Mall (Status Uncertain)'
    v2['highlights'] = ['原位於桃園市蘆竹區台茂購物中心內', '目前已不在官網館別列表中', '需向晶宴會館確認是否仍在營運']
    v2['rules'] = {
        'catering': [{'rule': '需洽詢場地確認營運狀態', 'source': '官網未提供', 'confidence': 'low'}],
        'decoration': [{'rule': '需洽詢場地確認營運狀態', 'source': '官網未提供', 'confidence': 'low'}],
        'sound': [{'rule': '需洽詢場地確認營運狀態', 'source': '官網未提供', 'confidence': 'low'}],
        'loadIn': [{'rule': '需洽詢場地確認營運狀態', 'source': '官網未提供', 'confidence': 'low'}],
        'cancellation': [{'rule': '需洽詢場地確認營運狀態', 'source': '官網未提供', 'confidence': 'low'}],
        'insurance': [{'rule': '需洽詢場地確認營運狀態', 'source': '官網未提供', 'confidence': 'low'}]
    }
    v2['risks'] = {
        'bookingLeadTime': '無法確認',
        'peakSeasons': ['無法確認'],
        'commonIssues': ['台茂館已不在官方網站的館別列表中，可能已結束營業或更名', '需向晶宴會館總公司(02)2992-0033確認']
    }
    v2['pricingTips'] = ['無法確認目前定價，建議聯繫晶宴會館總公司確認']
    v2['contact'] = {'phone': '(02)2992-0033', 'email': ''}
    v2['accessInfo'] = '原址：桃園市蘆竹區台茂購物中心內，需確認現況'
    v2['transportation'] = {'mrt': '最近機場捷運站需確認', 'parking': '台茂購物中心附設大型停車場'}
    v2['loadIn'] = '購物中心內場館，需洽詢確認營運狀態'
    v2['limitations'] = '此分館已不在官網館別列表中，狀態不明'
    v2['verified'] = False
    v2['lastUpdated'] = '2026-04-11'
    v2['statusNote'] = '台茂館已不在官網館別列表，可能已停業'
    print('1514 done (uncertain)')

    # === 1515 晶宴(桃園館) ===
    v3 = venues[1515]
    v3['description'] = '晶宴桃園館座落於桃園藝文特區旁，是晶宴最大的旗艦館且是唯一獨棟式婚宴會館，全館外觀以歐式建築元素與風格為設計理念，整體空間集結了簡約與典雅精緻於一體，氣勢磅礡，獨樹一格，開創桃園地區宴會、聚餐之高級場地首選。桃園館全新改裝更榮獲多項國際設計獎項肯定。'
    v3['nameEn'] = 'Amazing Hall Taoyuan'
    v3['highlights'] = [
        '晶宴最大旗艦館，唯一獨棟式婚宴會館',
        '歐式建築外觀設計',
        '桃園藝文特區旁，地段佳',
        '全新改裝榮獲多項國際設計獎項',
        '御嵿國際集團旗下品牌',
        '首創劇場式宴會廳與婚宴秘書服務'
    ]
    v3['image'] = 'https://i0.wp.com/www.amazinghall.com.tw/wp-content/uploads/2023/05/3F-%E6%81%86%E5%8A%87%E5%A0%B4%E5%A9%9A%E5%AE%B4-1-1024x683.jpg'
    v3['images'] = {
        'main': v3['image'],
        'gallery': [
            'https://i0.wp.com/www.amazinghall.com.tw/wp-content/uploads/2023/05/f1%E6%A1%83%E5%9C%92%E9%A4%A8.jpeg'
        ],
        'verified': True,
        'verifiedAt': '2026-04-11'
    }
    v3['rules'] = {
        'catering': [{'rule': '晶宴提供專屬婚宴秘書服務與晶緻美饌宴席料理，菜色依專案而異，需洽詢各館', 'source': '官網首頁', 'confidence': 'medium'}],
        'decoration': [{'rule': '需洽詢場地', 'source': '官網未提供', 'confidence': 'low'}],
        'sound': [{'rule': '配備頂級聲光設備，結合舞台設計', 'source': '官網首頁品牌介紹', 'confidence': 'medium'}],
        'loadIn': [{'rule': '需洽詢場地', 'source': '官網未提供', 'confidence': 'low'}],
        'cancellation': [{'rule': '需洽詢場地', 'source': '官網未提供', 'confidence': 'low'}],
        'insurance': [{'rule': '需洽詢場地', 'source': '官網未提供', 'confidence': 'low'}]
    }
    v3['risks'] = {
        'bookingLeadTime': '建議提前3-6個月預訂',
        'peakSeasons': ['農曆年前尾牙季', '婚宴旺季(9-12月)'],
        'commonIssues': ['旗艦館價格可能較高', '獨棟建築周邊停車需確認']
    }
    v3['pricingTips'] = ['旗艦館定位，價格可能為晶宴各館中最高', '建議詢問平日/假日價差及專案優惠', '官網有工商優惠方案，企業活動可洽詢']
    v3['contact'] = {'phone': '(03)355-3555', 'email': ''}
    v3['accessInfo'] = '桃園市桃園區南平路166號，桃園藝文特區旁'
    v3['transportation'] = {'mrt': '桃園捷運綠線（興建中），近期可搭台鐵桃園站轉乘', 'parking': '需洽詢場地'}
    v3['loadIn'] = '獨棟式建築，進場動線需洽詢'
    v3['limitations'] = '晶宴提供自有宴席料理，原則上不開放外燴'
    v3['verified'] = True
    v3['lastUpdated'] = '2026-04-11'
    v3['lastVerified'] = '2026-04-11'
    print('1515 done')

    with open(VENUES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print('All 3 晶宴 venues saved.')

if __name__ == '__main__':
    main()
