"""
============================================================
  📋 Planner — แผนงานและติดตามงาน
  ผู้บริหารวางแผนก่อนกระจายงาน + ติดตาม progress
============================================================
"""

import os
import sys
import io
import json
from datetime import datetime
import llm_helper

# ── Fix Windows encoding ──
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANS_DIR = os.path.join(PROJECT_ROOT, "Workspace", "Decision", "plans")
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")

# สร้างโฟลเดอร์ถ้ายังไม่มี
os.makedirs(PLANS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action: str):
    """บันทึกประวัติลง log"""
    log_file = os.path.join(LOGS_DIR, "orchestrator_agent.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [ORCHESTRATOR] {action}\n")

# ── Roleplay UI Helpers ──
def print_box(title, content, color_code="36"): # Default Cyan
    """แสดงกล่องข้อความสไตล์ Roleplay"""
    print(f"\n\033[{color_code}m┌" + "─" * 68 + "┐")
    print(f"│ {title:<66} │")
    print("├" + "─" * 68 + "┤")
    for line in content.split('\n'):
        # จัดการข้อความยาวเกินไป
        while len(line) > 66:
            print(f"│ {line[:66]:<66} │")
            line = line[66:]
        print(f"│ {line:<66} │")
    print("└" + "─" * 68 + "┘\033[0m")

# ──────────────────────────────────────────────
# 🔑 Keywords (เหมือน main.py — import ตรงนี้เพื่อให้ planner ใช้ standalone ได้)
# ──────────────────────────────────────────────
CASE_KEYWORDS = {
    "research": [
        "ค้นหา", "หาข้อมูล", "literature", "paper", "วิจัย", "research",
        "scopus", "google scholar", "journal", "ทบทวนวรรณกรรม", "review",
        "gap", "keyword", "reference", "อ้างอิง", "แหล่งข้อมูล",
        "เก็บข้อมูล", "data collection", "วิเคราะห์ข้อมูล", "analysis",
        "สถิติ", "ผลการวิจัย", "methodology", "วิธีการวิจัย",
    ],
    "writer": [
        "เขียน", "write", "draft", "ร่าง", "thesis", "วิทยานิพนธ์",
        "บท", "chapter", "abstract", "บทคัดย่อ", "บทนำ", "introduction",
        "สรุป", "conclusion", "อภิปราย", "discussion", "manuscript",
        "แก้ไขเนื้อหา", "เรียบเรียง", "พิมพ์", "เนื้อหา",
    ],
    "advisor": [
        "อาจารย์", "ที่ปรึกษา", "advisor", "feedback", "ความเห็น",
        "approve", "อนุมัติ", "ตรวจ", "ส่งงาน", "submit",
        "แก้ไขตามคำแนะนำ", "revision", "gate", "ผ่าน", "ไม่ผ่าน",
        "นัดพบ", "ประชุม advisor",
    ],
    "editor": [
        "จัดรูปแบบ", "format", "ตีพิมพ์", "publish", "publication",
        "บรรณาธิการ", "editor", "proofread", "ตรวจภาษา", "สะกดคำ",
        "citation", "apa", "journal submission", "หนังสือ",
        "book", "isbn", "ปก", "สารบัญ", "cover letter",
    ],
    "it": [
        "ติดตั้ง", "install", "setup", "config", "api", "key",
        "backup", "สำรอง", "git", "script", "automation", "ระบบ",
        "error", "bug", "แก้บั๊ก", "environment", "server", "deploy",
        "sandbox", "ทดสอบระบบ", "pipeline", "health check",
    ],
    "hr": [
        "กำหนดการ", "timeline", "deadline", "ประชุม", "meeting",
        "นัด", "schedule", "progress", "ความคืบหน้า", "รายงาน",
        "report", "risk", "ความเสี่ยง", "แผน", "plan", "milestone",
        "ติดตาม", "เตือน", "remind", "ทีม", "team",
    ],
    "qa": [
        "ตรวจสอบ", "check", "validate", "quality", "คุณภาพ",
        "plagiarism", "ลอก", "consistency", "สอดคล้อง", "ถูกต้อง",
        "เลขหน้า", "numbering", "checklist", "final check",
        "ก่อน submit", "ก่อนส่ง", "cross-check",
    ],
}

AGENT_DISPLAY = {
    "research": "📚 Research",
    "writer":   "✍️  Writer",
    "advisor":  "👨‍🏫 Advisor",
    "editor":   "📰 Editor",
    "it":       "💻 IT",
    "hr":       "👥 HR",
    "qa":       "✅ QA",
}

STATUS_ICON = {
    "pending":     "⬜",
    "in_progress": "🔄",
    "done":        "✅",
    "blocked":     "🚫",
    "skipped":     "⏭️",
}


# ──────────────────────────────────────────────
# 📋 Plan Data Structure
# ──────────────────────────────────────────────
def new_plan(message: str) -> dict:
    """สร้าง plan object ใหม่"""
    return {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "created": datetime.now().isoformat(),
        "original_message": message,
        "status": "draft",       # draft → approved → in_progress → done
        "tasks": [],
        "notes": "",
    }


def new_task(order: int, agent: str, description: str) -> dict:
    """สร้าง task object ใหม่"""
    return {
        "order": order,
        "agent": agent,
        "description": description,
        "status": "pending",     # pending → in_progress → done / blocked / skipped
        "result": "",
        "updated": "",
    }


# ──────────────────────────────────────────────
# 🧠 วิเคราะห์ข้อความ → สร้างแผนงาน
# ──────────────────────────────────────────────
def analyze_and_plan(message: str) -> dict:
    """
    วิเคราะห์ข้อความจาก user → สร้างแผนงานพร้อม tasks
    """
    plan = new_plan(message)
    message_lower = message.lower()

    # หาลำดับคำที่ปรากฏ (Index) ของแต่ละ agent
    scores = {}
    matched_keywords = {}
    for agent, keywords in CASE_KEYWORDS.items():
        matched = []
        min_idx = len(message_lower)
        for kw in keywords:
            kw_lower = kw.lower()
            idx = message_lower.find(kw_lower)
            if idx != -1:
                matched.append(kw)
                if idx < min_idx:
                    min_idx = idx
        
        if matched:
            matched_keywords[agent] = matched
            scores[agent] = min_idx

    # เรียงตามลำดับคำที่ปรากฏในประโยค (จากซ้ายไปขวา / index น้อยไปมาก)
    sorted_agents = sorted(scores.items(), key=lambda x: x[1])

    for i, (agent, score) in enumerate(sorted_agents, 1):
        kw_list = ", ".join(matched_keywords[agent][:3])
        desc = f"จัดการเรื่อง: {kw_list} (จากข้อความ user)"
        plan["tasks"].append(new_task(i, agent, desc))

    return plan


# ──────────────────────────────────────────────
# 🖥️ แสดงแผนงาน
# ──────────────────────────────────────────────
def show_plan(plan: dict):
    """แสดงแผนงานในรูปแบบตาราง"""
    print()
    print("=" * 60)
    print("  📋 แผนงาน (Plan)")
    print("=" * 60)
    print(f"  📝 ID:       {plan['id']}")
    print(f"  📅 สร้างเมื่อ: {plan['created'][:16]}")
    print(f"  📌 สถานะ:    {plan['status']}")
    print()
    print(f"  💬 ข้อความต้นฉบับ:")
    print(f"     \"{plan['original_message'][:100]}\"")

    if not plan["tasks"]:
        print("\n  ⚠️  ไม่มี tasks — ไม่สามารถจับคู่ agent ได้")
        return

    print()
    print("  ┌─────┬──────────────┬──────────────────────────────┬──────┐")
    print("  │ ลำดับ│ Agent        │ งาน                          │สถานะ │")
    print("  ├─────┼──────────────┼──────────────────────────────┼──────┤")

    for task in plan["tasks"]:
        icon = STATUS_ICON.get(task["status"], "❓")
        agent_name = AGENT_DISPLAY.get(task["agent"], task["agent"])
        desc = task["description"][:28]
        print(f"  │  {task['order']}  │ {agent_name:<12} │ {desc:<28} │  {icon}  │")

    print("  └─────┴──────────────┴──────────────────────────────┴──────┘")

    # ---- LOGGING ----
    log_action(f"📋 แสดงแผนงาน ID: {plan['id']}")
    log_action("┌─────┬──────────────┬──────────────────────────────┬──────┐")
    log_action("│ ลำดับ│ Agent        │ งาน                          │สถานะ │")
    log_action("├─────┼──────────────┼──────────────────────────────┼──────┤")
    for task in plan["tasks"]:
        icon = STATUS_ICON.get(task["status"], "❓")
        agent_name = AGENT_DISPLAY.get(task["agent"], task["agent"])
        desc = task["description"][:28]
        log_action(f"│  {task['order']}  │ {agent_name:<12} │ {desc:<28} │  {icon}  │")
    log_action("└─────┴──────────────┴──────────────────────────────┴──────┘")
    # -----------------

    if plan.get("notes"):
        print(f"\n  📝 หมายเหตุ: {plan['notes']}")
        log_action(f"📝 หมายเหตุ: {plan['notes']}")
    print()


# ──────────────────────────────────────────────
# ✏️ แก้ไขแผนงาน
# ──────────────────────────────────────────────
def edit_plan(plan: dict) -> dict:
    """ให้ผู้บริหารแก้ไขแผนก่อน approve"""
    while True:
        print("  ✏️  แก้ไขแผน:")
        print("     [A] เพิ่ม task")
        print("     [D] ลบ task (ระบุลำดับ)")
        print("     [E] แก้ไข task (ระบุลำดับ)")
        print("     [N] เพิ่มหมายเหตุ")
        print("     [OK] เสร็จ กลับ")
        choice = input("     > ").strip().upper()

        if choice == "OK" or choice == "":
            break

        elif choice == "A":
            print("\n     เลือก Agent:")
            for num, key in [("1","research"),("2","writer"),("3","advisor"),
                             ("4","editor"),("5","it"),("6","hr"),("7","qa")]:
                print(f"       {num}. {AGENT_DISPLAY[key]}")
            agent_num = input("     เลือก [1-7]: ").strip()
            agent_map = {"1":"research","2":"writer","3":"advisor",
                         "4":"editor","5":"it","6":"hr","7":"qa"}
            agent = agent_map.get(agent_num)
            if agent:
                desc = input("     รายละเอียดงาน: ").strip()
                order = len(plan["tasks"]) + 1
                plan["tasks"].append(new_task(order, agent, desc if desc else "งานใหม่"))
                print(f"     ✅ เพิ่ม task #{order} แล้ว")
                log_action(f"✏️ ผู้บริหารเพิ่ม task #{order} ให้กับ {agent}")
            else:
                print("     ❌ เลขไม่ถูกต้อง")

        elif choice == "D":
            num = input("     ลบ task ลำดับที่: ").strip()
            if num.isdigit():
                idx = int(num) - 1
                if 0 <= idx < len(plan["tasks"]):
                    removed = plan["tasks"].pop(idx)
                    # renumber
                    for i, t in enumerate(plan["tasks"], 1):
                        t["order"] = i
                    print(f"     ✅ ลบ task '{removed['description'][:30]}' แล้ว")
                    log_action(f"✏️ ผู้บริหารลบ task '{removed['description'][:30]}'")
                else:
                    print("     ❌ ลำดับไม่ถูกต้อง")

        elif choice == "E":
            num = input("     แก้ไข task ลำดับที่: ").strip()
            if num.isdigit():
                idx = int(num) - 1
                if 0 <= idx < len(plan["tasks"]):
                    task = plan["tasks"][idx]
                    print(f"     งานปัจจุบัน: {task['description']}")
                    new_desc = input("     รายละเอียดใหม่ (Enter = ไม่แก้): ").strip()
                    if new_desc:
                        task["description"] = new_desc
                        print("     ✅ แก้ไขแล้ว")
                        log_action(f"✏️ ผู้บริหารแก้ไขเนื้อหา task เป็น '{new_desc[:40]}'")

        elif choice == "N":
            note = input("     หมายเหตุ: ").strip()
            plan["notes"] = note
            print("     ✅ บันทึกหมายเหตุแล้ว")
            log_action(f"✏️ ผู้บริหารเพิ่มหมายเหตุ: '{note[:50]}'")

        show_plan(plan)

    return plan


# ──────────────────────────────────────────────
# ✅ Approve แผน
# ──────────────────────────────────────────────
def approve_plan(plan: dict) -> bool:
    """ถามผู้บริหารว่า approve แผนนี้หรือไม่"""
    show_plan(plan)

    print("  ─────────────────────────────────")
    print("  [Y] ✅ Approve — เริ่มกระจายงาน")
    print("  [E] ✏️  แก้ไขแผนก่อน")
    print("  [N] ❌ ยกเลิกแผนนี้")
    print("  ─────────────────────────────────")
    choice = input("  ผู้บริหาร > ").strip().upper()

    if choice == "Y" or choice == "":
        plan["status"] = "approved"
        save_plan(plan)
        
        # ขอคำพูดจาก LLM
        print(f"  🧠 Orchestrator กำลังวิเคราะห์และอนุมัติแผน...")
        orchestrator_role = ""
        role_path = os.path.join(PROJECT_ROOT, "Agent", "00_Orchestrator.md")
        if os.path.exists(role_path):
            with open(role_path, "r", encoding="utf-8") as f:
                orchestrator_role = f.read()
        
        roleplay_msg = llm_helper.get_roleplay_response("Orchestrator", 
                                                        f"อนุมัติแผนงานวิจัยต้นฉบับ: {plan['original_message']}", 
                                                        orchestrator_role)
        
        print_box("👔 ORCHESTRATOR", roleplay_msg, "36")
        
        print("\n  ✅ แผนได้รับการอนุมัติ!")
        log_action("✅ ผู้บริหารอนุมัติแผนงานเรียบร้อย")
        return True

    elif choice == "E":
        log_action("✏️ ผู้บริหารเลือกแก้ไขแผนก่อนอนุมัติ")
        plan = edit_plan(plan)
        return approve_plan(plan)  # recursive — ถาม approve อีกครั้ง

    else:
        plan["status"] = "cancelled"
        print("\n  ❌ ยกเลิกแผน")
        log_action("❌ ผู้บริหารยกเลิกแผนงาน")
        return False


# ──────────────────────────────────────────────
# 💾 บันทึก / โหลดแผน
# ──────────────────────────────────────────────
def save_plan(plan: dict):
    """บันทึกแผนเป็น JSON"""
    filename = f"plan_{plan['id']}.json"
    filepath = os.path.join(PLANS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"  💾 บันทึกแผน: {filepath}")


def load_plan(plan_id: str) -> dict | None:
    """โหลดแผนจาก JSON"""
    filename = f"plan_{plan_id}.json"
    filepath = os.path.join(PLANS_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def list_plans() -> list[dict]:
    """แสดงรายการแผนทั้งหมด"""
    plans = []
    if not os.path.exists(PLANS_DIR):
        return plans
    for f in sorted(os.listdir(PLANS_DIR), reverse=True):
        if f.startswith("plan_") and f.endswith(".json"):
            filepath = os.path.join(PLANS_DIR, f)
            with open(filepath, "r", encoding="utf-8") as fh:
                plans.append(json.load(fh))
    return plans


# ──────────────────────────────────────────────
# 📊 ติดตามงาน (Tracker)
# ──────────────────────────────────────────────
def update_task_status(plan: dict, task_order: int, status: str, result: str = ""):
    """อัปเดตสถานะ task"""
    for task in plan["tasks"]:
        if task["order"] == task_order:
            task["status"] = status
            task["result"] = result
            task["updated"] = datetime.now().isoformat()
            log_action(f"🔄 อัปเดต Task #{task_order} เป็น '{status}' (ผล: {result[:30]})")
            break
    # เช็คว่า tasks ทั้งหมดเสร็จหรือยัง
    all_done = all(t["status"] in ("done", "skipped") for t in plan["tasks"])
    if all_done:
        plan["status"] = "done"
    elif any(t["status"] == "in_progress" for t in plan["tasks"]):
        plan["status"] = "in_progress"
    save_plan(plan)


def show_tracker():
    """แสดงสถานะงานทั้งหมด"""
    plans = list_plans()
    if not plans:
        print("\n  📭 ยังไม่มีแผนงาน")
        return

    print()
    print("=" * 60)
    print("  📊 ติดตามงาน (Task Tracker)")
    print("=" * 60)

    for plan in plans[:5]:  # แสดง 5 แผนล่าสุด
        status_icon = {"draft": "📝", "approved": "✅", "in_progress": "🔄",
                       "done": "🎉", "cancelled": "❌"}.get(plan["status"], "❓")
        msg_preview = plan["original_message"][:40]
        print(f"\n  {status_icon} Plan: {plan['id']} [{plan['status']}]")
        print(f"     \"{msg_preview}...\"")

        if plan["tasks"]:
            done_count = sum(1 for t in plan["tasks"] if t["status"] == "done")
            total = len(plan["tasks"])
            pct = int(done_count / total * 100) if total > 0 else 0
            bar_filled = "█" * (pct // 10)
            bar_empty = "░" * (10 - pct // 10)
            print(f"     Progress: [{bar_filled}{bar_empty}] {pct}% ({done_count}/{total})")

            for task in plan["tasks"]:
                icon = STATUS_ICON.get(task["status"], "❓")
                agent_name = AGENT_DISPLAY.get(task["agent"], task["agent"])
                print(f"       {icon} #{task['order']} {agent_name}: {task['description'][:35]}")
                log_action(f"Tracker: {icon} #{task['order']} {agent_name}: {task['description'][:35]}")

    print()


def interactive_tracker():
    """ให้ผู้บริหารอัปเดตสถานะงาน interactive"""
    plans = list_plans()
    active = [p for p in plans if p["status"] in ("approved", "in_progress")]

    if not active:
        print("\n  📭 ไม่มีแผนงานที่กำลังดำเนินการ")
        return None

    print("\n  📋 แผนงานที่กำลังดำเนินการ:")
    for i, p in enumerate(active, 1):
        msg = p["original_message"][:40]
        print(f"     {i}. [{p['id']}] \"{msg}...\"")

    choice = input("\n  เลือกแผน [เลข]: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(active):
        print("  ❌ ไม่ถูกต้อง")
        return None

    plan = active[int(choice) - 1]
    show_plan(plan)
    log_action(f"🛠️ ผู้บริหารเข้าสู่ Interactive Tracker เพื่ออัปเดตแผน ID: {plan['id']}")

    print("  อัปเดตสถานะ task:")
    print("    ระบุ 'ลำดับ สถานะ' เช่น '1 done' หรือ '2 in_progress'")
    print("    สถานะ: pending | in_progress | done | blocked | skipped")
    print("    พิมพ์ 'back' = กลับ")

    while True:
        cmd = input("  อัปเดต > ").strip().lower()
        if cmd == "back" or cmd == "":
            break

        parts = cmd.split(maxsplit=1)
        if len(parts) < 2 or not parts[0].isdigit():
            print("    ❌ รูปแบบ: 'ลำดับ สถานะ' เช่น '1 done'")
            continue

        order = int(parts[0])
        status = parts[1]
        valid = ["pending", "in_progress", "done", "blocked", "skipped"]
        if status not in valid:
            print(f"    ❌ สถานะต้องเป็น: {', '.join(valid)}")
            continue

        result = ""
        if status == "done":
            result = input("    📝 ผลลัพธ์ (Enter = ข้าม): ").strip()

        update_task_status(plan, order, status, result)
        print(f"    ✅ อัปเดต task #{order} → {STATUS_ICON.get(status, '')} {status}")
        show_plan(plan)

    return plan


# ──────────────────────────────────────────────
# 🔄 Public API (เรียกจาก main.py)
# ──────────────────────────────────────────────
def create_and_approve_plan(message: str) -> dict | None:
    """
    สร้างแผน → แสดง → ให้ approve → return plan ถ้า approved
    ใช้จาก main.py:
        from planner import create_and_approve_plan
        plan = create_and_approve_plan(user_message)
    """
    plan = analyze_and_plan(message)

    if not plan["tasks"]:
        print("\n  ⚠️  ไม่สามารถวิเคราะห์ข้อความได้ — ไม่พบ keyword ที่จับคู่ agent")
        return None

    if approve_plan(plan):
        return plan
    return None


def get_approved_tasks(plan: dict) -> list[dict]:
    """ดึง tasks ที่ pending จากแผนที่ approved แล้ว"""
    if plan["status"] not in ("approved", "in_progress"):
        return []
    return [t for t in plan["tasks"] if t["status"] == "pending"]
