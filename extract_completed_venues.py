import json

with open('venues.json', 'r', encoding='utf-8') as f:
    venues = json.load(f)

# 已爬取成功的場地ID（根據FINAL_PROCESSING_REPORT.md）
completed_ids = [1031, 1032, 1034, 1035, 1036, 1038, 1042, 1043, 1044, 1045,
                1049, 1051, 1053, 1055, 1057, 1068, 1069, 1072, 1075, 1076,
                1077, 1082, 1083, 1085, 1086, 1090, 1095]

print('# ✅ 已完成爬取的場地（27個）\n')
print('| # | 場地名稱 | ID | 官網網址 | 資料完整度 |')
print('|---|---------|-----|---------|-----------|')

for i, vid in enumerate(completed_ids, 1):
    venue = next((v for v in venues if v['id'] == vid), None)
    if venue:
        name = venue.get('name', 'N/A')
        url = venue.get('url', 'N/A')

        # 資料完整度描述
        status = []
        if venue.get('email'):
            status.append('Email')
        if venue.get('contactPhone') or venue.get('metadata', {}).get('phoneSource'):
            status.append('電話')
        if venue.get('images', {}).get('gallery'):
            img_count = len(venue['images']['gallery'])
            status.append(f'{img_count}圖片')
        if venue.get('metadata', {}).get('pdfCount'):
            status.append(f"{venue['metadata'].get('pdfCount')} PDF")

        status_text = ' + '.join(status) if status else '基本資料'

        # 標記已下架的場地
        if venue.get('discontinued'):
            status_text += ' (⚠️ 已下架)'

        print(f'| {i} | {name} | {vid} | {url} | {status_text} |')
