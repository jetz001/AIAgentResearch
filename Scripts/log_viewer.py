"""
============================================================
  🔎 LOG VIEWER — ระบบตรวจสอบประวัติการทำงาน (System Logs)
============================================================
  วิธีใช้: python Scripts/log_viewer.py
"""
import os
import sys
import io
import time
from datetime import datetime

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")

def get_all_logs():
    all_logs = []
    if not os.path.exists(LOGS_DIR):
        return all_logs
        
    for filename in os.listdir(LOGS_DIR):
        if filename.endswith(".log"):
            filepath = os.path.join(LOGS_DIR, filename)
            agent_name = filename.replace("_agent.log", "").replace(".log", "").upper()
            
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("["):
                        # Format: [2026-05-07 14:31:00] [IT] message...
                        try:
                            # Extract timestamp
                            end_idx = line.find("]")
                            ts_str = line[1:end_idx]
                            ts_obj = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                            
                            # Extract message
                            msg = line[end_idx+1:].strip()
                            all_logs.append((ts_obj, agent_name, msg))
                        except ValueError:
                            # Parse error, just append as raw
                            all_logs.append((datetime.min, agent_name, line))
    
    # Sort by timestamp descending (newest first)
    all_logs.sort(key=lambda x: x[0], reverse=True)
    return all_logs

def print_banner():
    os.system("cls" if os.name == "nt" else "clear")
    print("\n" + "="*70)
    print("  🔎 SYSTEM LOG VIEWER — ระบบตรวจสอบประวัติการทำงานของ Agent")
    print("="*70)

def display_logs(limit=20):
    logs = get_all_logs()
    if not logs:
        print("\n  📭 ยังไม่มีประวัติการทำงาน (Log ว่างเปล่า)")
        return
        
    print(f"\n  📊 แสดงประวัติล่าสุด {min(limit if isinstance(limit, int) else 15, len(logs))} รายการ:\n")
    print("  TIME                 | AGENT    | ACTION")
    print("  " + "-"*66)
    
    for ts, agent, msg in logs[:limit]:
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if ts != datetime.min else "UNKNOWN TIME"
        agent_pad = agent[:8].ljust(8)
        print(f"  {ts_str}  | {agent_pad} | {msg}")
        
    print("\n  " + "-"*66)
    print(f"  ทั้งหมด: {len(logs)} รายการในระบบ")

def clear_logs():
    print("\n  ⚠️ คำเตือน: คุณต้องการลบประวัติ Log ทั้งหมดหรือไม่? (ลบเฉพาะไฟล์ .log)")
    confirm = input("  พิมพ์ 'DELETE' เพื่อยืนยัน: ").strip()
    if confirm == "DELETE":
        count = 0
        for filename in os.listdir(LOGS_DIR):
            if filename.endswith(".log"):
                os.remove(os.path.join(LOGS_DIR, filename))
                count += 1
        print(f"  🗑️ ลบไฟล์ log ไปทั้งหมด {count} ไฟล์เรียบร้อยแล้ว")
    else:
        print("  ❌ ยกเลิกการลบ")

def main():
    while True:
        print_banner()
        display_logs(limit=15)
        
        print("\n  [R] Refresh ดูล่าสุด  |  [A] ดูทั้งหมด  |  [C] ลบ Log ทั้งหมด  |  [Q] ออก")
        cmd = input("  > ").strip().upper()
        
        if cmd == "Q":
            print("\n  👋 ออกจากระบบ Log")
            break
        elif cmd == "A":
            print_banner()
            display_logs(limit=9999)
            input("\n  กด Enter เพื่อกลับไปหน้าหลัก...")
        elif cmd == "C":
            clear_logs()
            input("\n  กด Enter เพื่อทำต่อ...")
        elif cmd == "R" or cmd == "":
            continue
        else:
            print("  ❌ คำสั่งไม่ถูกต้อง")
            time.sleep(1)

if __name__ == "__main__":
    main()
