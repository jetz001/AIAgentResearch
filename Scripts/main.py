"""
============================================================
  🎯 Main Runner — Orchestrator Agent (ผู้บริหาร)
  Master's Thesis Research Project
  Multi-Agent AI Research Assistant
============================================================
  วิธีใช้: python Scripts/main.py
  ผู้บริหาร paste ข้อความจาก user → ระบบวิเคราะห์ → ส่งต่อไป agent ที่เหมาะสม
============================================================
"""

import os
import sys
import io
from datetime import datetime
import llm_helper

# ── Fix Windows encoding (cp874 → UTF-8) ──
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

# ──────────────────────────────────────────────
# 📁 Project Root (ปรับ path ให้ชี้ไปที่ AgentResearch)
# ──────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # AgentResearch/

# --- Simple Env Loader ---
def load_env():
    # ตรวจสอบทั้งที่ root และในโฟลเดอร์ Config
    paths = [
        os.path.join(PROJECT_ROOT, ".env"),
        os.path.join(PROJECT_ROOT, "Config", ".env")
    ]
    for env_path in paths:
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()

load_env()

SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "Scripts")
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")
os.makedirs(LOGS_DIR, exist_ok=True)

def log_action(action: str):
    """บันทึกประวัติการทำงานของผู้บริหารลง log"""
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
# 📦 Agent Scripts (ประกาศไว้ก่อน — ยังไม่ต้องสร้าง)
# ──────────────────────────────────────────────
AGENT_SCRIPTS = {
    "research":  os.path.join(SCRIPTS_DIR, "agent_research.py"),
    "writer":    os.path.join(SCRIPTS_DIR, "agent_writer.py"),
    "advisor":   os.path.join(SCRIPTS_DIR, "agent_advisor.py"),
    "editor":    os.path.join(SCRIPTS_DIR, "agent_editor.py"),
    "it":        os.path.join(SCRIPTS_DIR, "agent_it.py"),
    "hr":        os.path.join(SCRIPTS_DIR, "agent_hr.py"),
    "qa":        os.path.join(SCRIPTS_DIR, "agent_qa.py"),
}

# ──────────────────────────────────────────────
# 📄 Agent Role Definitions (อ่านจาก Agent/*.md)
# ──────────────────────────────────────────────
AGENT_ROLES_DIR = os.path.join(PROJECT_ROOT, "Agent")

AGENT_ROLE_FILES = {
    "orchestrator": os.path.join(AGENT_ROLES_DIR, "00_Orchestrator.md"),
    "research":     os.path.join(AGENT_ROLES_DIR, "01_Research.md"),
    "writer":       os.path.join(AGENT_ROLES_DIR, "02_Writer.md"),
    "advisor":      os.path.join(AGENT_ROLES_DIR, "03_Advisor.md"),
    "editor":       os.path.join(AGENT_ROLES_DIR, "04_Editor.md"),
    "it":           os.path.join(AGENT_ROLES_DIR, "05_IT.md"),
    "hr":           os.path.join(AGENT_ROLES_DIR, "06_HR.md"),
    "qa":           os.path.join(AGENT_ROLES_DIR, "07_QA.md"),
}


def load_role(agent_name: str) -> str:
    """อ่าน role definition จากไฟล์ .md"""
    filepath = AGENT_ROLE_FILES.get(agent_name)
    if filepath and os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return f"(ไม่พบ role file สำหรับ {agent_name})"


def get_role_summary(agent_name: str) -> list[str]:
    """ดึงเฉพาะ skill IDs จาก role file"""
    content = load_role(agent_name)
    skills = []
    for line in content.split("\n"):
        if line.strip().startswith("### SK-"):
            # เช่น "### SK-ORC-01: Workflow Management"
            skill = line.strip().replace("### ", "")
            skills.append(skill)
    return skills

# ──────────────────────────────────────────────
# 🔑 Keywords สำหรับจับคู่ case แต่ละ agent
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
        "approve", "อนุมัติ", "ตรวจ", "review", "ส่งงาน", "submit",
        "แก้ไขตามคำแนะนำ", "revision", "gate", "ผ่าน", "ไม่ผ่าน",
        "นัดพบ", "ประชุม advisor",
    ],
    "editor": [
        "จัดรูปแบบ", "format", "ตีพิมพ์", "publish", "publication",
        "บรรณาธิการ", "editor", "proofread", "ตรวจภาษา", "สะกดคำ",
        "citation", "อ้างอิง", "apa", "journal submission", "หนังสือ",
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

# ──────────────────────────────────────────────
# 🎨 UI Helpers
# ──────────────────────────────────────────────
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print("=" * 60)
    print("  🎯 ORCHESTRATOR — ผู้บริหารโปรเจค")
    print("  Master's Thesis Research Agent System")
    print("=" * 60)
    print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  📂 Project: {PROJECT_ROOT}")
    print("=" * 60)

    # แสดง skill summary ของ Orchestrator
    skills = get_role_summary("orchestrator")
    if skills:
        print("  📋 My Skills:")
        for sk in skills:
            print(f"     • {sk}")
    print()


def print_agent_menu():
    agents = [
        ("1", "📚 Research Agent",  "ค้นหา วิเคราะห์ข้อมูลวิจัย"),
        ("2", "✍️  Writer Agent",   "เขียน thesis / manuscript"),
        ("3", "👨‍🏫 Advisor Agent",  "จัดการ advisor / review"),
        ("4", "📰 Editor Agent",    "จัดรูปแบบ / ตีพิมพ์"),
        ("5", "💻 IT Agent",        "ระบบ / automation / backup"),
        ("6", "👥 HR Agent",        "กำหนดการ / ประชุม / ติดตาม"),
        ("7", "✅ QA Agent",        "ตรวจสอบคุณภาพ"),
    ]
    print("┌────────────────────────────────────────────────┐")
    print("│            📋 Agent ที่พร้อมให้บริการ             │")
    print("├────┬───────────────────┬───────────────────────┤")
    print("│ #  │ Agent             │ หน้าที่                │")
    print("├────┼───────────────────┼───────────────────────┤")
    for num, name, desc in agents:
        print(f"│ {num}  │ {name:<17} │ {desc:<21} │")
    print("└────┴───────────────────┴───────────────────────┘")
    print()


# ──────────────────────────────────────────────
# 🧠 Orchestrator Logic — วิเคราะห์ข้อความ → เลือก Agent
# ──────────────────────────────────────────────
def analyze_message(message: str) -> list[tuple[str, int]]:
    """
    วิเคราะห์ข้อความจาก user แล้วให้คะแนนแต่ละ agent
    return: list ของ (agent_name, score) เรียงจากมากไปน้อย
    """
    message_lower = message.lower()
    scores = {}

    for agent, keywords in CASE_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw.lower() in message_lower:
                score += 1
        if score > 0:
            scores[agent] = score

    # เรียงจากคะแนนมากไปน้อย
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_scores


AGENT_DISPLAY = {
    "research": "📚 Research Agent",
    "writer":   "✍️  Writer Agent",
    "advisor":  "👨‍🏫 Advisor Agent",
    "editor":   "📰 Editor Agent",
    "it":       "💻 IT Agent",
    "hr":       "👥 HR Agent",
    "qa":       "✅ QA Agent",
}

AGENT_NUM_MAP = {
    "1": "research",
    "2": "writer",
    "3": "advisor",
    "4": "editor",
    "5": "it",
    "6": "hr",
    "7": "qa",
}


def dispatch_to_agent(agent_name: str, message: str):
    """
    ส่งงานไปยัง agent script ที่เลือก
    """
    script_path = AGENT_SCRIPTS.get(agent_name)

    if not script_path:
        print(f"  ❌ ไม่พบ agent: {agent_name}")
        return

    if not os.path.exists(script_path):
        print(f"  ⚠️  Script ยังไม่ได้สร้าง: {os.path.basename(script_path)}")
        print(f"     Path: {script_path}")
        print(f"     → สร้างไฟล์นี้ก่อนแล้วรันใหม่")
        return

    # เรียก agent script พร้อมส่งข้อความผ่าน argument
    print(f"\n  🚀 กำลังส่งงานไปยัง {AGENT_DISPLAY[agent_name]}...")
    print(f"  📄 Script: {os.path.basename(script_path)}")
    print("-" * 60)

    os.system(f'python "{script_path}" "{message}"')
    log_action(f"ส่งงานไปยัง {agent_name} สำเร็จ")


# ──────────────────────────────────────────────
# 📋 Planner Integration
# ──────────────────────────────────────────────
from planner import (
    create_and_approve_plan,
    get_approved_tasks,
    show_tracker,
    interactive_tracker,
    update_task_status,
)


# ──────────────────────────────────────────────
# 🚀 Dispatch ตามแผนงาน (ทีละ task)
# ──────────────────────────────────────────────
def dispatch_plan(plan: dict):
    """กระจายงานตามแผนที่ approve แล้ว — ทีละ task"""
    tasks = get_approved_tasks(plan)
    if not tasks:
        print("  📭 ไม่มี task ที่ต้องทำ")
        return

    print(f"\n  🚀 เริ่มกระจายงาน ({len(tasks)} tasks)")
    print("=" * 60)

    for task in tasks:
        agent = task["agent"]
        display = AGENT_DISPLAY.get(agent, agent)
        print(f"\n  ──── Task #{task['order']} ────")
        print(f"  👤 Agent: {display}")
        print(f"  📝 งาน:   {task['description']}")

        confirm = input(f"  ▶️  ส่งงานนี้ไป {display}? [Y/N/skip]: ").strip().upper()

        if confirm == "Y" or confirm == "":
            update_task_status(plan, task["order"], "in_progress")
            
            # ขอคำพูดจาก LLM
            print(f"  🧠 Orchestrator กำลังประมวลผลคำสั่งส่งงาน...")
            orchestrator_role = "" # ดึงจากไฟล์ถ้ามี
            if os.path.exists(os.path.join(PROJECT_ROOT, "Agent", "00_Orchestrator.md")):
                with open(os.path.join(PROJECT_ROOT, "Agent", "00_Orchestrator.md"), "r", encoding="utf-8") as f:
                    orchestrator_role = f.read()
            
            roleplay_msg = llm_helper.get_roleplay_response("Orchestrator", 
                                                            f"ส่งงานลำดับที่ {task['order']} ไปยัง {display}: {task['description']}", 
                                                            orchestrator_role,
                                                            agent_key="orchestrator")
            
            print_box("👔 ORCHESTRATOR", roleplay_msg, "36")
            
            dispatch_to_agent(agent, task["description"])
            
            # ถามผลหลัง agent ทำเสร็จ
            result_status = input(f"\n  ผลลัพธ์ task #{task['order']}? [done/blocked/pending]: ").strip().lower()
            if result_status in ("done", "blocked", "pending"):
                result_note = ""
                if result_status == "done":
                    result_note = input("  📝 บันทึกผล (Enter = ข้าม): ").strip()
                update_task_status(plan, task["order"], result_status, result_note)
                log_action(f"Task #{task['order']} (Agent: {agent}) -> {result_status}")
            else:
                update_task_status(plan, task["order"], "done")
                log_action(f"Task #{task['order']} (Agent: {agent}) -> done")
            print(f"  ✅ Task #{task['order']} อัปเดตแล้ว")

        elif confirm == "SKIP":
            update_task_status(plan, task["order"], "skipped")
            print(f"  ⏭️  ข้าม task #{task['order']}")

        else:
            print(f"  ⏸️  หยุดกระจายงาน — tasks ที่เหลือยังเป็น pending")
            break

    print("\n" + "=" * 60)
    print("  📊 สรุปแผนงานหลังกระจาย:")
    show_tracker()


# ──────────────────────────────────────────────
# 🔄 Main Loop
# ──────────────────────────────────────────────
def main():
    log_action("--- เปิดระบบ Orchestrator ---")
    clear_screen()
    print_banner()
    print_agent_menu()

    while True:
        print("-" * 60)
        print("📌 คำสั่ง:")
        print("   วาง (paste) ข้อความ = สร้างแผน → กระจายงาน")
        print("   'status'  = 📊 ดูสถานะงานทั้งหมด")
        print("   'update'  = ✏️  อัปเดตสถานะ task")
        print("   'role'    = 📄 ดู role ของผู้บริหาร")
        print("   'role N'  = 📄 ดู role agent (เช่น role 1)")
        print("   '1'-'7'   = 🎯 ส่งงานตรงไป agent")
        print("   'menu'    = 📋 ดู agent list")
        print("   'quit'    = 👋 ออก")
        print("-" * 60)

        try:
            user_input = input("\n🔹 ผู้บริหาร > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 ออกจากระบบ")
            break

        if not user_input:
            continue

        # ── คำสั่งพิเศษ ──
        cmd = user_input.lower()

        if cmd == "quit":
            print("\n👋 ออกจากระบบ — ขอบคุณครับ")
            log_action("👋 ผู้บริหารออกจากระบบ")
            break

        if cmd == "menu":
            clear_screen()
            print_banner()
            print_agent_menu()
            continue

        if cmd == "clear":
            clear_screen()
            print_banner()
            continue

        if cmd == "status":
            show_tracker()
            log_action("📊 ผู้บริหารเรียกดูสถานะงาน (Status Tracker)")
            continue

        if cmd == "update":
            log_action("✏️ ผู้บริหารเข้าสู่โหมดอัปเดตสถานะงาน (Interactive Update)")
            interactive_tracker()
            continue

        if cmd.startswith("role"):
            parts = cmd.split()
            if len(parts) == 1:
                # 'role' → แสดง role ของ orchestrator
                print("\n" + load_role("orchestrator"))
                log_action("📄 ผู้บริหารเรียกดู Role ของตัวเอง")
            else:
                # 'role 1' → แสดง role ของ agent เลขนั้น
                agent_key = AGENT_NUM_MAP.get(parts[1])
                if agent_key:
                    print(f"\n" + load_role(agent_key))
                    log_action(f"📄 ผู้บริหารเรียกดู Role ของ {agent_key}")
                else:
                    print("  ❌ ระบุเลข 1-7 เช่น 'role 1' = Research Agent")
            continue

        # ── เลือก agent ตรงด้วยเลข (ไม่ผ่านแผน) ──
        if user_input in AGENT_NUM_MAP:
            agent = AGENT_NUM_MAP[user_input]
            print(f"\n  ✅ เลือก {AGENT_DISPLAY[agent]} โดยตรง (ไม่ผ่านแผน)")
            log_action(f"🎯 ผู้บริหารเลือก {agent} โดยตรง (Direct Dispatch)")
            msg = input("  📝 ข้อความที่จะส่ง (หรือ Enter เพื่อข้าม): ").strip()
            dispatch_to_agent(agent, msg if msg else "(ไม่มีข้อความ)")
            continue

        # ── ข้อความจาก user → สร้างแผน → approve → กระจายงาน ──
        print("\n  🧠 กำลังวิเคราะห์ข้อความ...")
        log_action(f"รับคำสั่งจาก user: {user_input[:50]}")
        plan = create_and_approve_plan(user_input)

        if plan:
            log_action("อนุมัติแผนงานแล้ว เริ่มกระจายงาน")
            dispatch_plan(plan)
        else:
            # fallback: ถ้าไม่ approve แผน → ถามเลือก agent ตรง
            print("\n  💡 หรือจะเลือก agent ด้วยตัวเอง?")
            print_agent_menu()
            choice = input("  เลือกเลข [1-7] หรือ Enter = ข้าม: ").strip()
            if choice in AGENT_NUM_MAP:
                agent = AGENT_NUM_MAP[choice]
                log_action(f"🎯 ผู้บริหารเลือก {agent} แบบแมนนวลหลังยกเลิกแผน")
                dispatch_to_agent(agent, user_input)


# ──────────────────────────────────────────────
if __name__ == "__main__":
    main()
