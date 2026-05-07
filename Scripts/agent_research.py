"""
============================================================
  📚 Research Agent — นักวิจัย
  Master's Thesis Research Project
============================================================
  วิธีใช้: เรียกจาก main.py หรือรันตรง:
    python Scripts/agent_research.py "ข้อความงาน"
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

# ──────────────────────────────────────────────
# 📁 Paths
# ──────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT_DIR = os.path.join(PROJECT_ROOT, "Agent")
ROLE_FILE = os.path.join(AGENT_DIR, "01_Research.md")
TODO_DIR = os.path.join(PROJECT_ROOT, "Workspace", "Decision", "research_tasks")
DOCS_DIR = os.path.join(PROJECT_ROOT, "Docs")
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
REFS_DIR = os.path.join(PROJECT_ROOT, "References")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "Output", "reports")
MEMORY_DIR = os.path.join(PROJECT_ROOT, "Memory", "Short memory")
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")

# สร้างโฟลเดอร์ถ้ายังไม่มี
for d in [TODO_DIR, DOCS_DIR, DATA_DIR, REFS_DIR, OUTPUT_DIR, MEMORY_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Roleplay UI Helpers ──
def print_box(title, content, color_code="34"): # Default Blue for Research
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
# 📄 อ่าน Role ตัวเอง
# ──────────────────────────────────────────────
def load_my_role() -> str:
    if os.path.exists(ROLE_FILE):
        with open(ROLE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "(ไม่พบ role file)"


def get_my_skills() -> list[str]:
    content = load_my_role()
    skills = []
    for line in content.split("\n"):
        if line.strip().startswith("### SK-"):
            skill = line.strip().replace("### ", "")
            skills.append(skill)
    return skills


# ──────────────────────────────────────────────
# 📋 TODO List Management
# ──────────────────────────────────────────────
def todo_filepath() -> str:
    return os.path.join(TODO_DIR, "research_todo.json")


def load_todo() -> list[dict]:
    fp = todo_filepath()
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_todo(todos: list[dict]):
    with open(todo_filepath(), "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def add_todo(description: str, skill_id: str = ""):
    todos = load_todo()
    todo = {
        "id": len(todos) + 1,
        "description": description,
        "skill_id": skill_id,
        "status": "pending",      # pending → in_progress → done → submitted
        "result": "",
        "output_file": "",
        "created": datetime.now().isoformat(),
        "updated": "",
        "review": "",              # accepted / rejected / revision_needed
        "review_note": "",
    }
    todos.append(todo)
    save_todo(todos)
    return todo


def update_todo(todo_id: int, **kwargs):
    todos = load_todo()
    for t in todos:
        if t["id"] == todo_id:
            for k, v in kwargs.items():
                t[k] = v
            t["updated"] = datetime.now().isoformat()
            break
    save_todo(todos)


STATUS_ICON = {
    "pending": "⬜", "in_progress": "🔄", "done": "✅",
    "submitted": "📤", "accepted": "🎉", "rejected": "❌",
    "revision_needed": "🔁",
}


def show_todo():
    todos = load_todo()
    if not todos:
        print("\n  📭 ไม่มี TODO")
        return

    print("\n  ┌─────┬──────────────────────────────────┬──────────┬────────┐")
    print("  │  #  │ งาน                              │ สถานะ    │ Review │")
    print("  ├─────┼──────────────────────────────────┼──────────┼────────┤")
    for t in todos:
        icon = STATUS_ICON.get(t["status"], "❓")
        review_icon = STATUS_ICON.get(t["review"], "  —") if t["review"] else "  —"
        desc = t["description"][:30]
        print(f"  │ {t['id']:>3} │ {desc:<32} │ {icon:<8} │ {review_icon:<6} │")
    print("  └─────┴──────────────────────────────────┴──────────┴────────┘")

    # Progress summary
    done_count = sum(1 for t in todos if t["status"] in ("done", "submitted", "accepted"))
    total = len(todos)
    pct = int(done_count / total * 100) if total > 0 else 0
    bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
    print(f"  Progress: [{bar}] {pct}% ({done_count}/{total})")


# ──────────────────────────────────────────────
# 🔬 Skill Functions (จำลอง — user ทำจริงแล้วบันทึก)
# ──────────────────────────────────────────────
SKILL_MENU = {
    "1": ("SK-RES-01", "Literature Search",     "ค้นหา papers จาก database"),
    "2": ("SK-RES-02", "Paper Screening",       "คัดกรอง papers ตามเกณฑ์"),
    "3": ("SK-RES-03", "Data Extraction",       "สกัดข้อมูลจาก papers"),
    "4": ("SK-RES-04", "Gap Analysis",          "วิเคราะห์ Gap of Knowledge"),
    "5": ("SK-RES-05", "Data Collection",       "เก็บข้อมูลจากแหล่งวิจัย"),
    "6": ("SK-RES-06", "Primary Analysis",      "วิเคราะห์ตามกรอบวิจัยหลัก"),
    "7": ("SK-RES-07", "Secondary Analysis",    "วิเคราะห์ตามกรอบวิจัยรอง"),
}


def run_skill(skill_num: str):
    """รัน skill ที่เลือก — สร้าง TODO + ให้ user ทำงานแล้วบันทึกผล"""
    if skill_num not in SKILL_MENU:
        print("  ❌ เลขไม่ถูกต้อง")
        return

    skill_id, skill_name, skill_desc = SKILL_MENU[skill_num]

    print(f"\n  🔬 เริ่มงาน: {skill_name}")
    print(f"     {skill_desc}")
    print(f"     Skill ID: {skill_id}")
    print("-" * 50)

    # รายละเอียดเพิ่ม
    detail = input("  📝 รายละเอียดงาน (หรือ Enter ใช้ default): ").strip()
    if not detail:
        detail = f"{skill_name}: {skill_desc}"

    # สร้าง TODO
    todo = add_todo(detail, skill_id)
    print(f"  ✅ สร้าง TODO #{todo['id']}: {detail}")

    # เริ่มทำงาน?
    start_now = input("  ▶️  เริ่มทำงานเลย? [Y/N]: ").strip().upper()
    if start_now == "Y" or start_now == "":
        update_todo(todo["id"], status="in_progress")
        print(f"\n  🔄 กำลังทำ: {detail}")
        print("  ─────────────────────────────────")
        print("  ทำงานตามขั้นตอน แล้วบันทึกผลด้านล่าง:")
        print("  (พิมพ์ผลลัพธ์ หรือระบุ path ไฟล์ output)")
        print("  ─────────────────────────────────")

        result = input("  📄 ผลลัพธ์: ").strip()
        output_file = input("  📂 Output file path (Enter = ไม่มี): ").strip()

        update_todo(todo["id"],
                     status="done",
                     result=result if result else "(ไม่ได้บันทึก)",
                     output_file=output_file)
        print(f"  ✅ TODO #{todo['id']} เสร็จแล้ว!")

        # ถามว่าจะ submit ให้ผู้บริหาร review ไหม
        submit = input("  📤 ส่งให้ผู้บริหาร review? [Y/N]: ").strip().upper()
        if submit == "Y" or submit == "":
            update_todo(todo["id"], status="submitted")
            print(f"  📤 ส่ง TODO #{todo['id']} ให้ผู้บริหาร review แล้ว")
    else:
        print(f"  ⬜ TODO #{todo['id']} รอไว้ — ทำทีหลัง")


# ──────────────────────────────────────────────
# 📤 Submit งานให้ผู้บริหาร
# ──────────────────────────────────────────────
def submit_to_orchestrator():
    """ส่งงานที่เสร็จแล้วให้ผู้บริหาร review"""
    todos = load_todo()
    done_tasks = [t for t in todos if t["status"] == "done"]

    if not done_tasks:
        print("\n  📭 ไม่มีงานที่เสร็จแล้วรอ submit")
        submitted = [t for t in todos if t["status"] == "submitted"]
        if submitted:
            print(f"  📤 มี {len(submitted)} งานที่ส่ง review แล้ว — รอผู้บริหารตรวจ")
        return

    print("\n  📋 งานที่เสร็จแล้ว (พร้อม submit):")
    for t in done_tasks:
        print(f"    ✅ #{t['id']}: {t['description'][:40]}")
        if t["result"]:
            print(f"       ผลลัพธ์: {t['result'][:50]}")

    print("\n  [A] Submit ทั้งหมด")
    print("  [เลข] Submit เฉพาะ TODO #")
    print("  [N] ยกเลิก")
    choice = input("  > ").strip().upper()

    if choice == "A":
        for t in done_tasks:
            update_todo(t["id"], status="submitted")
        print(f"  📤 ส่ง {len(done_tasks)} งานให้ผู้บริหาร review แล้ว")
    elif choice.isdigit():
        tid = int(choice)
        if any(t["id"] == tid for t in done_tasks):
            update_todo(tid, status="submitted")
            print(f"  📤 ส่ง TODO #{tid} แล้ว")
        else:
            print(f"  ❌ TODO #{tid} ไม่อยู่ในรายการ done")
    else:
        print("  ⏭️  ยกเลิก")


# ──────────────────────────────────────────────
# 👨‍💼 ผู้บริหาร Review (เรียกจาก main.py หรือรันตรง)
# ──────────────────────────────────────────────
def orchestrator_review():
    """ให้ผู้บริหารตรวจงานที่ Research submit มา"""
    todos = load_todo()
    submitted = [t for t in todos if t["status"] == "submitted"]

    if not submitted:
        print("\n  📭 ไม่มีงานรอ review")
        return

    print("\n" + "=" * 60)
    print("  👨‍💼 ผู้บริหาร — Review งาน Research Agent")
    print("=" * 60)

    for t in submitted:
        print(f"\n  ─── TODO #{t['id']} ───")
        print(f"  📝 งาน:    {t['description']}")
        print(f"  🔬 Skill:  {t['skill_id']}")
        print(f"  📄 ผลลัพธ์: {t['result']}")
        if t["output_file"]:
            print(f"  📂 Output: {t['output_file']}")
        print()
        print("  [A] ✅ Accept — รับ")
        print("  [R] 🔁 Revision — ตีกลับแก้ไข")
        print("  [X] ❌ Reject — ไม่รับ")
        print("  [S] ⏭️  Skip — ข้ามไว้ก่อน")

        decision = input("  ผู้บริหาร > ").strip().upper()

        if decision == "A":
            update_todo(t["id"], status="accepted", review="accepted")
            print(f"  ✅ TODO #{t['id']} — ACCEPTED")

        elif decision == "R":
            note = input("  📝 เหตุผล/สิ่งที่ต้องแก้: ").strip()
            update_todo(t["id"],
                        status="in_progress",
                        review="revision_needed",
                        review_note=note)
            print(f"  🔁 TODO #{t['id']} — ตีกลับแก้ไข")

        elif decision == "X":
            note = input("  📝 เหตุผลที่ไม่รับ: ").strip()
            update_todo(t["id"],
                        status="rejected",
                        review="rejected",
                        review_note=note)
            print(f"  ❌ TODO #{t['id']} — REJECTED")

        else:
            print(f"  ⏭️  ข้าม TODO #{t['id']}")

    print("\n  📊 สรุปหลัง review:")
    show_todo()


# ──────────────────────────────────────────────
# 🔄 จัดการงานที่ถูกตีกลับ
# ──────────────────────────────────────────────
def handle_revisions():
    """แสดงงานที่ถูกตีกลับ + ให้แก้ไข"""
    todos = load_todo()
    revisions = [t for t in todos if t["review"] == "revision_needed" and t["status"] == "in_progress"]

    if not revisions:
        print("\n  ✅ ไม่มีงานที่ต้องแก้ไข")
        return

    print("\n  🔁 งานที่ถูกตีกลับ:")
    for t in revisions:
        print(f"\n  ─── TODO #{t['id']} ───")
        print(f"  📝 งาน:      {t['description']}")
        print(f"  📄 ผลเดิม:   {t['result']}")
        print(f"  💬 เหตุผล:   {t['review_note']}")
        print()

        fix = input("  ▶️  แก้ไขตอนนี้? [Y/N]: ").strip().upper()
        if fix == "Y" or fix == "":
            new_result = input("  📄 ผลลัพธ์ใหม่: ").strip()
            new_file = input("  📂 Output file ใหม่ (Enter = เดิม): ").strip()
            update_todo(t["id"],
                        result=new_result if new_result else t["result"],
                        output_file=new_file if new_file else t["output_file"],
                        status="done",
                        review="",
                        review_note="")
            print(f"  ✅ แก้ไข TODO #{t['id']} แล้ว — พร้อม submit อีกครั้ง")


# ──────────────────────────────────────────────
# 📝 Log
# ──────────────────────────────────────────────
def log_action(action: str):
    logfile = os.path.join(LOGS_DIR, "research_agent.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [Research] {action}\n")


# ──────────────────────────────────────────────
# 🎨 UI
# ──────────────────────────────────────────────
def print_banner():
    print()
    print("=" * 60)
    print("  📚 RESEARCH AGENT — นักวิจัย")
    print("=" * 60)
    print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  📂 Project: {PROJECT_ROOT}")
    print("=" * 60)

    # แสดง skill summary
    skills = get_my_skills()
    if skills:
        print("  📋 My Skills:")
        for sk in skills:
            print(f"     • {sk}")

    # แสดงงานค้าง
    todos = load_todo()
    pending = sum(1 for t in todos if t["status"] == "pending")
    in_prog = sum(1 for t in todos if t["status"] == "in_progress")
    submitted = sum(1 for t in todos if t["status"] == "submitted")
    revisions = sum(1 for t in todos if t["review"] == "revision_needed")
    if todos:
        print(f"\n  📊 สถานะ: ⬜{pending} รอ | 🔄{in_prog} กำลังทำ | 📤{submitted} รอ review | 🔁{revisions} ตีกลับ")
    print()


def print_menu():
    print("  ┌─────────────────────────────────────────┐")
    print("  │        📋 Research Agent Menu            │")
    print("  ├─────┬───────────────────────────────────┤")
    print("  │ CMD │ หน้าที่                            │")
    print("  ├─────┼───────────────────────────────────┤")
    print("  │  1  │ 🔬 Literature Search              │")
    print("  │  2  │ 📄 Paper Screening                │")
    print("  │  3  │ 📊 Data Extraction                │")
    print("  │  4  │ 🔍 Gap Analysis                   │")
    print("  │  5  │ 📦 Data Collection                │")
    print("  │  6  │ 📈 Primary Analysis               │")
    print("  │  7  │ 📉 Secondary Analysis             │")
    print("  ├─────┼───────────────────────────────────┤")
    print("  │todo │ 📋 ดู TODO list                    │")
    print("  │sub  │ 📤 Submit งานให้ผู้บริหาร          │")
    print("  │rev  │ 🔁 ดูงานที่ถูกตีกลับ              │")
    print("  │role │ 📄 ดู Role ตัวเอง                  │")
    print("  │back │ 🔙 กลับ main                      │")
    print("  └─────┴───────────────────────────────────┘")


# ──────────────────────────────────────────────
# 🔄 Main Loop
# ──────────────────────────────────────────────
def main(initial_message: str = ""):
    print_banner()
    print_menu()

    # ถ้ามีข้อความจาก orchestrator → สร้าง TODO อัตโนมัติ
    if initial_message and initial_message != "(ไม่มีข้อความ)":
        # ดึง Role มาให้ LLM วิเคราะห์
        my_role = load_my_role()
        
        # ขอความเห็นจาก LLM (Ollama)
        print(f"\n  🧠 กำลังติดต่อ {llm_helper.OLLAMA_MODEL} เพื่อเตรียมการตอบกลับ...")
        roleplay_msg = llm_helper.get_roleplay_response("Research Agent", initial_message, my_role)
        
        print_box("🎭 ROLEPLAY: 📚 Research Agent", roleplay_msg, "34")
        
        print(f"\n  📨 ได้รับงานจากผู้บริหาร:")
        print(f"     \"{initial_message[:80]}\"")
        auto_add = input("  ➕ เพิ่มเป็น TODO? [Y/N]: ").strip().upper()
        if auto_add == "Y" or auto_add == "":
            todo = add_todo(initial_message)
            print(f"  ✅ สร้าง TODO #{todo['id']}")
            log_action(f"รับงานจากผู้บริหาร: {initial_message[:50]}")

    while True:
        print("\n" + "-" * 50)
        try:
            cmd = input("  📚 Research > ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n  🔙 กลับ main")
            break

        if not cmd:
            continue

        if cmd == "back" or cmd == "quit":
            print("  🔙 กลับ main")
            break

        if cmd == "menu":
            print_menu()
            continue

        if cmd == "todo":
            show_todo()
            continue

        if cmd == "sub" or cmd == "submit":
            submit_to_orchestrator()
            continue

        if cmd == "rev" or cmd == "revision":
            handle_revisions()
            continue

        if cmd == "role":
            print("\n" + load_my_role())
            continue

        if cmd == "review":
            # ผู้บริหารเรียกตรงเพื่อ review
            orchestrator_review()
            continue

        if cmd in SKILL_MENU:
            run_skill(cmd)
            log_action(f"รัน skill: {SKILL_MENU[cmd][1]}")
            continue

        # ถ้าพิมพ์อย่างอื่น → ถือเป็น TODO ใหม่
        print(f"  ➕ ไม่พบคำสั่ง '{cmd}' — เพิ่มเป็น TODO?")
        confirm = input("  [Y/N]: ").strip().upper()
        if confirm == "Y" or confirm == "":
            todo = add_todo(cmd)
            print(f"  ✅ สร้าง TODO #{todo['id']}: {cmd}")


# ──────────────────────────────────────────────
if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else ""
    main(msg)
