#!/usr/bin/env python3
"""
台北喜來登資料恢復腳本
從 95fb2ef 恢復空間資訊，合併到目前資料
"""

import json
import subprocess
from datetime import datetime

def get_old_data():
    """從 95fb2ef 獲取舊資料"""
    result = subprocess.run(
        ["git", "show", "95fb2ef:venues.json"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

def merge_room_data(old_room, new_room):
    """合併新舊會議室資料"""
    merged = new_room.copy()
    
    # 從舊資料恢復的欄位
    fields_to_restore = [
        "floor",
        "ceiling", 
        "hasWindow",
        "features",
        "notes",
        "areaUnit"
    ]
    
    for field in fields_to_restore:
        if field in old_room:
            merged[field] = old_room[field]
    
    # 恢復正確的面積（如果舊資料有 areaUnit，使用舊的 area）
    if "areaUnit" in old_room:
        merged["area"] = old_room["area"]
    
    # 恢復會議室專屬照片（如果有 image 欄位）
    if "image" in old_room:
        merged["images"] = [old_room["image"]]
        merged["photo"] = old_room["image"]
    
    return merged

def restore_sheraton_data():
    """主程式"""
    print("=== 台北喜來登資料恢復 ===\n")
    
    # 1. 讀取目前資料
    with open("venues.json", "r", encoding="utf-8") as f:
        current_venues = json.load(f)
    
    # 2. 獲取舊資料
    print("正在從 95fb2ef 提取舊資料...")
    old_venues = get_old_data()
    
    # 3. 找到喜來登
    old_sheraton = None
    new_sheraton = None
    
    for v in old_venues:
        if v.get("id") == 1067:
            old_sheraton = v
            break
    
    for i, v in enumerate(current_venues):
        if v.get("id") == 1067:
            new_sheraton = v
            new_sheraton_index = i
            break
    
    if not old_sheraton or not new_sheraton:
        print("❌ 找不到喜來登資料！")
        return
    
    print(f"✅ 找到舊資料：{len(old_sheraton.get('rooms', []))} 個會議室")
    print(f"✅ 找到新資料：{len(new_sheraton.get('rooms', []))} 個會議室\n")
    
    # 4. 合併會議室資料
    print("正在合併會議室資料...")
    
    # 建立名稱對應
    old_rooms_by_name = {r["name"]: r for r in old_sheraton.get("rooms", [])}
    
    merged_rooms = []
    for new_room in new_sheraton.get("rooms", []):
        room_name = new_room["name"]
        
        if room_name in old_rooms_by_name:
            old_room = old_rooms_by_name[room_name]
            merged = merge_room_data(old_room, new_room)
            merged_rooms.append(merged)
            print(f"  ✅ {room_name}: 已恢復空間資訊")
        else:
            # 保留新資料
            merged_rooms.append(new_room)
            print(f"  ⚠️  {room_name}: 使用新資料（舊資料中找不到）")
    
    # 5. 更新喜來登資料
    current_venues[new_sheraton_index]["rooms"] = merged_rooms
    current_venues[new_sheraton_index]["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
    
    # 6. 備份並保存
    backup_file = f"venues.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n正在備份到 {backup_file}...")
    
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(current_venues, f, ensure_ascii=False, indent=2)
    
    print(f"正在保存到 venues.json...")
    with open("venues.json", "w", encoding="utf-8") as f:
        json.dump(current_venues, f, ensure_ascii=False, indent=2)
    
    # 7. 顯示結果
    print("\n=== 恢復結果 ===")
    print(f"✅ 已恢復 {len(merged_rooms)} 個會議室的空間資訊")
    print(f"✅ 備份已保存到 {backup_file}")
    print(f"✅ 資料已更新到 venues.json")
    
    # 8. 顯示第一個會議室的恢復結果
    print("\n=== 第一個會議室（福廳）恢復結果 ===")
    first_room = merged_rooms[0]
    print(f"樓層: {first_room.get('floor', '❌ 無')}")
    print(f"天花板高度: {first_room.get('ceiling', '❌ 無')} 公尺")
    print(f"窗戶: {'有' if first_room.get('hasWindow') else '無'}")
    print(f"特色: {', '.join(first_room.get('features', []))}")
    print(f"備註: {first_room.get('notes', '❌ 無')}")
    print(f"照片: {len(first_room.get('images', []))} 張")
    
    print("\n✅ 恢復完成！請執行以下命令驗證：")
    print("  python3 scripts/validate_room_data.py")
    print("\n如果驗證通過，請提交：")
    print("  git add venues.json")
    print('  git commit -m "修復: 恢復台北喜來登會議室空間資訊"')

if __name__ == "__main__":
    try:
        restore_sheraton_data()
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
