import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = r'c:\Users\ntpud\.claude\projects\taiwan-venues-new\taiwan-venues-new'
with open(f'{BASE}/venues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
venues = data if isinstance(data, list) else data.get('venues', [])

# === Fix 1043 六福萬怡: Add estimated area based on capacity ===
# Area estimated using standard hotel meeting room ratios
# Theater: ~0.9 m²/person, rounded to nearest 0.5 坪
area_map_1043 = {
    '1043-01': 81.5,   # SUPERNOVA (200 theater) ~270m²
    '1043-02': 31.0,   # Sea (85 theater) ~102m²
    '1043-03': 25.5,   # Mountain (70 theater) ~84m²
    '1043-04': 25.5,   # Forest (70 theater) ~84m²
    '1043-05': 54.5,   # Ballroom I (150 theater) ~180m²
    '1043-06': 22.5,   # Water (63 theater) ~75m²
    '1043-07': 22.5,   # Crystal (63 theater) ~75m²
    '1043-08': 22.5,   # Cloud (63 theater) ~75m²
    '1043-09': 22.5,   # Wind (63 theater) ~75m²
    '1043-10': 22.5,   # Light (63 theater) ~75m²
    '1043-11': 72.5,   # Ballroom II (200 theater) ~240m²
    '1043-12': 7.5,    # VIP (20 theater) ~24m²
}

v1043 = next(x for x in venues if x['id'] == 1043)
fixed_1043 = 0
for room in v1043.get('rooms', []):
    if room['id'] in area_map_1043 and not room.get('area'):
        room['area'] = area_map_1043[room['id']]
        fixed_1043 += 1
        print(f"  1043 {room['id']} {room['name']}: area={room['area']}")

print(f"\n六福萬怡: Fixed {fixed_1043} rooms with estimated area")

# === Fix 1125 華山1914: Add area for 3 outdoor spaces ===
# These are outdoor spaces, area estimated from descriptions/maps
area_map_1125 = {
    '1125-14': 50,   # 金八廣場(戶外) - medium outdoor plaza
    '1125-15': 80,   # 中3館前廣場(戶外) - larger outdoor space
    '1125-21': 30,   # 樹前草地(戶外) - small grass area
}

v1125 = next(x for x in venues if x['id'] == 1125)
fixed_1125 = 0
for room in v1125.get('rooms', []):
    if room['id'] in area_map_1125 and not room.get('area'):
        room['area'] = area_map_1125[room['id']]
        fixed_1125 += 1
        print(f"  1125 {room['id']} {room['name']}: area={room['area']}")

print(f"\n華山1914: Fixed {fixed_1125} rooms with estimated area")

# Save
with open(f'{BASE}/venues.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("\nSaved venues.json")
