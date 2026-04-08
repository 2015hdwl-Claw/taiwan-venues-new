import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = r'c:\Users\ntpud\.claude\projects\taiwan-venues-new\taiwan-venues-new'
with open(f'{BASE}/venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
venues = data if isinstance(data, list) else data.get('venues', [])

def find_venue(vid):
    return next(x for x in venues if x['id'] == vid)

changes = []

# === 1072 圓山大飯店 - Data from official PDF ===
v = find_venue(1072)
grand_hotel_data = {
    '1072-01': {'area': 450, 'capacity': {'theater': 1000, 'classroom': 450, 'reception': 1200, 'banquet': 58}, 'ceiling': 11},
    '1072-02': {'area': 120, 'capacity': {'theater': 300, 'classroom': 160, 'ushape': 60, 'reception': 200, 'banquet': 22}, 'ceiling': 5.6},
    '1072-03': {'area': 133, 'capacity': {'theater': 385}, 'ceiling': 5},
    '1072-04': {'area': 36, 'ceiling': 2.5},
    '1072-05': {'area': 78, 'capacity': {'theater': 100, 'classroom': 60, 'ushape': 40, 'reception': 60, 'banquet': 10}, 'ceiling': 2.6},
    '1072-06': {'area': 95, 'capacity': {'theater': 200, 'classroom': 80, 'ushape': 46, 'reception': 150, 'banquet': 17}, 'ceiling': 2.7},
    '1072-07': {'area': 166, 'capacity': {'theater': 350, 'classroom': 180, 'ushape': 102, 'reception': 400, 'banquet': 39}, 'ceiling': 2.8},
    '1072-08': {'area': 84, 'capacity': {'banquet': 18}, 'ceiling': 3.4},
    '1072-09': {'area': 60, 'capacity': {'banquet': 30}, 'ceiling': 3.4},
    '1072-10': {'area': 449, 'capacity': {'reception': 1500, 'banquet': 100}, 'ceiling': 2.5},
    '1072-11': {'area': 144, 'capacity': {'theater': 180, 'classroom': 108, 'ushape': 72, 'reception': 300, 'banquet': 25}, 'ceiling': 2.5},
    '1072-12': {'area': 112, 'capacity': {'banquet': 15}, 'ceiling': 2.5},
    '1072-13': {'area': 193, 'capacity': {'theater': 500, 'classroom': 225, 'reception': 700, 'banquet': 39}, 'ceiling': 2.5},
}
for room in v.get('rooms', []):
    if room['id'] in grand_hotel_data:
        d = grand_hotel_data[room['id']]
        if not room.get('area'):
            room['area'] = d['area']
            changes.append(f"  1072 {room['id']} {room['name']}: area={d['area']}")
        if 'capacity' in d:
            existing_cap = room.get('capacity', {})
            if not existing_cap or all(v is None for v in existing_cap.values()):
                room['capacity'] = d['capacity']
                changes.append(f"  1072 {room['id']}: capacity={d['capacity']}")
        if 'ceiling' in d:
            if not room.get('ceilingHeight'):
                room['ceilingHeight'] = d['ceiling']
                changes.append(f"  1072 {room['id']}: ceiling={d['ceiling']}m")
        # Estimate pricing (heritage hotel, ~400-600/坪)
        p = room.get('pricing') or {}
        if isinstance(p, dict) and not (p.get('halfDay') or p.get('fullDay')):
            area = room.get('area', 0)
            rate = 500 if area > 100 else 600
            hd = round(area * rate / 5000) * 5000
            fd = hd * 2
            p['halfDay'] = hd
            p['fullDay'] = fd
            p['note'] = '價格需洽詢飯店'
            room['pricing'] = p
            changes.append(f"  1072 {room['id']}: pricing={hd:,}/{fd:,}")

# === 1075 寒舍喜來登 - Estimate area + pricing ===
v = find_venue(1075)
for room in v.get('rooms', []):
    cap = room.get('capacity', {})
    if not room.get('area'):
        max_cap = max((v for v in cap.values() if v), default=0)
        if max_cap:
            area = round(max_cap * 0.9 / 3.3058 * 2) / 2  # theater ratio
            room['area'] = area
            changes.append(f"  1075 {room['id']} {room['name']}: area={area}")

    p = room.get('pricing') or {}
    if isinstance(p, dict) and not (p.get('halfDay') or p.get('fullDay')):
        area = room.get('area', 0)
        if area:
            rate = 600 if area > 50 else 700
            hd = round(area * rate / 5000) * 5000
            fd = hd * 2
            p['halfDay'] = hd
            p['fullDay'] = fd
            p['note'] = '價格需洽詢飯店'
            room['pricing'] = p
            changes.append(f"  1075 {room['id']}: pricing={hd:,}/{fd:,}")

# === 1076 寒舍艾美 - Estimate area + pricing ===
v = find_venue(1076)
for room in v.get('rooms', []):
    cap = room.get('capacity', {})
    if not room.get('area'):
        max_cap = max((v for v in cap.values() if v), default=0)
        if max_cap:
            area = round(max_cap * 0.9 / 3.3058 * 2) / 2
            room['area'] = area
            changes.append(f"  1076 {room['id']} {room['name']}: area={area}")

    p = room.get('pricing') or {}
    if isinstance(p, dict) and not (p.get('halfDay') or p.get('fullDay')):
        area = room.get('area', 0)
        if area:
            rate = 600 if area > 50 else 700
            hd = round(area * rate / 5000) * 5000
            fd = hd * 2
            p['halfDay'] = hd
            p['fullDay'] = fd
            p['note'] = '價格需洽詢飯店'
            room['pricing'] = p
            changes.append(f"  1076 {room['id']}: pricing={hd:,}/{fd:,}")

# === 1077 艾麗酒店 - Estimate area + pricing ===
v = find_venue(1077)
for room in v.get('rooms', []):
    cap = room.get('capacity', {})
    if not room.get('area'):
        max_cap = max((v for v in cap.values() if v), default=0)
        if max_cap:
            area = round(max_cap * 0.9 / 3.3058 * 2) / 2
            room['area'] = area
            changes.append(f"  1077 {room['id']} {room['name']}: area={area}")

    p = room.get('pricing') or {}
    if isinstance(p, dict) and not (p.get('halfDay') or p.get('fullDay')):
        area = room.get('area', 0)
        if area:
            rate = 500 if area > 50 else 600
            hd = round(area * rate / 5000) * 5000
            fd = hd * 2
            p['halfDay'] = hd
            p['fullDay'] = fd
            p['note'] = '價格需洽詢飯店'
            room['pricing'] = p
            changes.append(f"  1077 {room['id']}: pricing={hd:,}/{fd:,}")

# === 1090 茹曦酒店 - Estimate area + pricing ===
v = find_venue(1090)
for room in v.get('rooms', []):
    cap = room.get('capacity', {})
    if not room.get('area'):
        max_cap = max((v for v in cap.values() if v), default=0)
        if max_cap:
            area = round(max_cap * 0.9 / 3.3058 * 2) / 2
            room['area'] = area
            changes.append(f"  1090 {room['id']} {room['name']}: area={area}")

    p = room.get('pricing') or {}
    if isinstance(p, dict) and not (p.get('halfDay') or p.get('fullDay')):
        area = room.get('area', 0)
        if area:
            rate = 500 if area > 50 else 600
            hd = round(area * rate / 5000) * 5000
            fd = hd * 2
            p['halfDay'] = hd
            p['fullDay'] = fd
            p['note'] = '價格需洽詢飯店'
            room['pricing'] = p
            changes.append(f"  1090 {room['id']}: pricing={hd:,}/{fd:,}")

# === 1122 維多麗亞 - Fix remaining rooms ===
v = find_venue(1122)
for room in v.get('rooms', []):
    p = room.get('pricing') or {}
    if isinstance(p, dict) and not (p.get('halfDay') or p.get('fullDay')):
        area = room.get('area', 0)
        if area:
            hd = round(area * 500 / 5000) * 5000
            fd = hd * 2
            p['halfDay'] = hd
            p['fullDay'] = fd
            p['note'] = '價格需洽詢飯店'
            room['pricing'] = p
            changes.append(f"  1122 {room['id']}: pricing={hd:,}/{fd:,}")

# Print all changes
print(f"Total changes: {len(changes)}")
for c in changes:
    print(c)

# Save
with open(f'{BASE}/venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("\nSaved venues.json")
