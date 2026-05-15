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
import json
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

def log_action(action: str, phase: str = "IMPLEMENTATION"):
    """บันทึกประวัติการทำงานของผู้บริหารลง log"""
    log_file = os.path.join(LOGS_DIR, "orchestrator_agent.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [ORCHESTRATOR] [{phase}] {action}\n")

def log_score_csv(plan_id: str, task_order: int, agent: str, score: int, note: str):
    """บันทึกคะแนนลง CSV เพื่อการวิเคราะห์"""
    csv_file = os.path.join(LOGS_DIR, "answer_scores.csv")
    file_exists = os.path.exists(csv_file)
    with open(csv_file, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("Timestamp,PlanID,TaskOrder,Agent,Score,Note\n")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clean_note = note.replace(",", ";").replace("\n", " ")
        f.write(f"{timestamp},{plan_id},{task_order},{agent},{score},{clean_note}\n")

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
# 📦 Agent Scripts
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
# 📄 Agent Role Definitions
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
    filepath = AGENT_ROLE_FILES.get(agent_name)
    if filepath and os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return f"(ไม่พบ role file สำหรับ {agent_name})"

def get_role_summary(agent_name: str) -> list[str]:
    content = load_role(agent_name)
    skills = []
    for line in content.split("\n"):
        if line.strip().startswith("### SK-"):
            skill = line.strip().replace("### ", "")
            skills.append(skill)
    return skills

# ──────────────────────────────────────────────
# 🔑 Keywords
# ──────────────────────────────────────────────
CASE_KEYWORDS = {
    "research": ["ค้นหา", "หาข้อมูล", "literature", "paper", "วิจัย", "research", "gap", "keyword", "reference", "methodology"],
    "writer":   ["เขียน", "write", "draft", "ร่าง", "thesis", "chapter", "abstract", "สรุป"],
    "advisor":  ["อาจารย์", "ที่ปรึกษา", "advisor", "feedback", "approve", "ส่งงาน", "submit"],
    "editor":   ["จัดรูปแบบ", "format", "ตีพิมพ์", "proofread", "citation", "apa"],
    "it":       ["ติดตั้ง", "install", "setup", "config", "api", "script", "error", "bug"],
    "hr":       ["กำหนดการ", "deadline", "ประชุม", "meeting", "progress", "plan"],
    "qa":       ["ตรวจสอบ", "check", "validate", "quality", "plagiarism", "สอดคล้อง"],
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
    skills = get_role_summary("orchestrator")
    if skills:
        print("  📋 My Skills:")
        for sk in skills: print(f"     • {sk}")
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
    for num, name, desc in agents:
        print(f"│ {num}  │ {name:<17} │ {desc:<21} │")
    print("└────┴───────────────────┴───────────────────────┘\n")

def dispatch_to_agent(agent_name: str, message: str):
    """
    ส่งงานไปยัง agent script ที่เลือก
    """
    script_path = AGENT_SCRIPTS.get(agent_name)

    if not script_path or not os.path.exists(script_path):
        print(f"  ❌ ไม่พบ agent script: {agent_name}")
        return

    # เรียก agent script พร้อมส่งข้อความผ่าน argument และส่ง env ไปด้วย
    import subprocess
    import sys
    
    # ส่งต่อ environment variables ทั้งหมด (รวมถึง AUTOMATED)
    env = os.environ.copy()
    
    print(f"\n  🚀 กำลังส่งงานไปยัง {AGENT_DISPLAY[agent_name]}...")
    subprocess.run([sys.executable, script_path, message], env=env)
    log_action(f"ส่งงานไปยัง {agent_name} สำเร็จ")

from planner import (
    create_and_approve_plan,
    get_approved_tasks,
    show_tracker,
    interactive_tracker,
    update_task_status,
)

AGENT_DISPLAY = {
    "research": "📚 Research Agent", "writer": "✍️  Writer Agent", "advisor": "👨‍🏫 Advisor Agent",
    "editor": "📰 Editor Agent", "it": "💻 IT Agent", "hr": "👥 HR Agent", "qa": "✅ QA Agent",
}
AGENT_NUM_MAP = {"1": "research", "2": "writer", "3": "advisor", "4": "editor", "5": "it", "6": "hr", "7": "qa"}

def dispatch_plan(plan: dict, automated: bool = False):
    tasks = get_approved_tasks(plan)
    if not tasks: return
    context_summary = ""
    for task in tasks:
        agent = task["agent"]
        display = AGENT_DISPLAY.get(agent, agent)
        full_message = f"🎯 คำสั่งจากผู้บริหาร (Orchestrator):\n{task['description']}\n\n📋 ข้อความต้นฉบับ: \"{plan.get('original_message', '')}\"\n"
        if context_summary.strip(): full_message += f"\n💡 ข้อมูลแวดล้อม: {context_summary}"
        
        attempt = 0
        max_attempts = 3
        is_passed = False
        
        while attempt < max_attempts and not is_passed:
            attempt += 1
            if automated: confirm = "Y"
            else: confirm = input(f"  ▶️  ส่งงาน #{task['order']} ไป {display} (Attempt {attempt})? [Y/N]: ").strip().upper()

            if confirm == "Y" or confirm == "":
                # 📝 LOG: บันทึกการจ่ายงาน (ทวนคำสั่ง)
                log_msg = f"SENDING TASK #{task['order']} to {display}\n   👉 INSTRUCTION: {task['description']}"
                log_action(log_msg, phase="DISPATCH")
                
                update_task_status(plan, task["order"], "in_progress")
                dispatch_to_agent(agent, full_message)
                
                # --- [QUALITY GATE] ---
                result_note = "ดำเนินการสำเร็จ"
                todo_paths = {
                    "research": os.path.join(PROJECT_ROOT, "Workspace", "Decision", "research_tasks", "research_todo.json"),
                    "writer": os.path.join(PROJECT_ROOT, "Workspace", "Decision", "writer_tasks", "writer_todo.json"),
                    "advisor": os.path.join(PROJECT_ROOT, "Workspace", "Decision", "advisor_tasks", "advisor_todo.json"),
                    "editor": os.path.join(PROJECT_ROOT, "Workspace", "Decision", "editor_tasks", "editor_todo.json"),
                    "it": os.path.join(PROJECT_ROOT, "Workspace", "Decision", "it_tasks", "it_todo.json"),
                    "hr": os.path.join(PROJECT_ROOT, "Workspace", "Decision", "hr_tasks", "hr_todo.json"),
                    "qa": os.path.join(PROJECT_ROOT, "Workspace", "Decision", "qa_tasks", "qa_todo.json"),
                }
                if agent in todo_paths and os.path.exists(todo_paths[agent]):
                    try:
                        with open(todo_paths[agent], "r", encoding="utf-8") as f:
                            todos = json.load(f)
                            # 🔍 ค้นหางานล่าสุดที่สถานะเป็น 'done' และต้องตรงกับคำสั่งปัจจุบัน (เพื่อป้องกันการอ่านงานเก่ามาตรวจ)
                            current_desc = task['description'].strip()
                            completed_tasks = [
                                t for t in todos 
                                if t.get("status") in ["done", "submitted", "accepted"] 
                                and (current_desc in t.get("description", "") or t.get("description", "") in current_desc)
                            ]
                            if completed_tasks:
                                latest_task = completed_tasks[-1]
                                result_note = latest_task.get("result", result_note)
                    except Exception as e:
                        print(f"  ⚠️ ไม่สามารถอ่านไฟล์ TODO ของ {agent}: {e}")

                # 🧠 ตรวจสอบคุณภาพงาน (Automated Review)
                print(f"  🔍 กำลังตรวจสอบคุณภาพงานของ {display}...")
                review_prompt = f"ตรวจสอบว่าผลลัพธ์นี้ตรงตามคำสั่งหรือไม่: '{task['description']}'\n\nผลลัพธ์จากเอเจ้นท์: {result_note}\n\nตอบเพียง 'PASS' หรือ 'FAIL: [เหตุผล]' เท่านั้น"
                review_decision = llm_helper.get_roleplay_response("Quality Checker", review_prompt, "คุณคือผู้ตรวจสอบคุณภาพงานวิจัยที่เฮี้ยบที่สุด", agent_key="orchestrator")
                
                if "PASS" in review_decision.upper():
                    is_passed = True
                    update_task_status(plan, task["order"], "done", result_note, 5)
                    context_summary += f"\n[ผลลัพธ์จาก {display}]: {result_note}\n"
                    print(f"  ✅ {display} สอบผ่านในรอบที่ {attempt}!")
                    
                    # 📝 LOG: บันทึกความสำเร็จ (โชว์เนื้องาน)
                    success_log = f"SUCCESS TASK #{task['order']} by {display}\n   📄 RESULT PREVIEW: {result_note[:300]}..."
                    log_action(success_log, phase="COMPLETED")
                else:
                    print(f"  ❌ {display} สอบตก! เหตุผล: {review_decision}")
                    log_action(f"REJECTED TASK #{task['order']} ({display})\n   ⚠️ REASON: {review_decision}", phase="REVISION")
                    full_message += f"\n\n⚠️ งานเก่าถูกตีกลับ! เหตุผล: {review_decision}\nกรุณาแก้ไขให้ถูกต้องและห้ามทำพลาดซ้ำเดิม!"
                    if attempt == max_attempts:
                        print(f"  ⚠️ ทำงานพลาดเกิน {max_attempts} รอบ ยอมรับงานตามสภาพ")
                        log_action(f"FORCE ACCEPT TASK #{task['order']} ({display}) after {max_attempts} fails", phase="WARNING")
                        update_task_status(plan, task["order"], "done", result_note, 2)
                        is_passed = True # บังคับผ่านเพื่อออกจากลูป
            else:
                break

def generate_final_report(plan: dict) -> str:
    """สร้างรายงานสรุปผลงานจากทุกเอเจ้นท์"""
    orchestrator_role = load_role("orchestrator")
    work_summary = f"ภารกิจ: {plan['original_message']}\n"
    for task in plan["tasks"]:
        work_summary += f"{task['order']}. [{task['status']}] {task['agent']}: {task['result']}\n"
    report_content = llm_helper.get_report_response("Orchestrator Agent", work_summary, orchestrator_role, agent_key="orchestrator")
    return report_content

def combine_and_export_step():
    """ขั้นตอนที่ 8-10: รวบรวมและ Export ไฟล์"""
    print_box("📂 STEP 8-10: Combine & Export", "กำลังรวบรวมเนื้อหาและสร้างไฟล์เอกสาร...")
    import subprocess
    
    # 8. Combine Thesis
    combine_script = os.path.join(SCRIPTS_DIR, "combine_thesis.py")
    subprocess.run([sys.executable, combine_script])
    
    # 9-10. Export Word/HTML (ถ้ามีสคริปต์รองรับ)
    html_script = os.path.join(SCRIPTS_DIR, "generate_html.py")
    if os.path.exists(html_script):
        subprocess.run([sys.executable, html_script])
    
    log_action("Thesis combined and exported to Word/HTML", phase="EXPORT")

def orchestrator_review_gate(plan: dict, report: str, automated: bool = False) -> str:
    """ด่านที่ 11: ผู้บริหาร (Orchestrator) ตรวจสอบ"""
    print_box("🛡️ GATE 11: Orchestrator Review", "กำลังประเมินภาพรวมของงาน...")
    if automated:
        # ในโหมดอัตโนมัติ ให้ AI ช่วยประเมินเบื้องต้น
        prompt = f"ในฐานะผู้บริหาร (Orchestrator) โปรดตรวจสอบรายงานนี้: {report}\nหากงานมีคุณภาพและครบถ้วนตามโจทย์ '{plan['original_message']}' ให้ตอบ 'PASS' มิฉะนั้นตอบ 'FAIL: [เหตุผล]'"
        decision = llm_helper.call_llm(prompt, "คุณคือผู้บริหารที่ต้องการงานคุณภาพสูงสุด", agent_key="orchestrator")
        if "PASS" in decision.upper():
            log_action(f"AUTO-GATE 11 APPROVED\n   📊 REPORT SUMMARY: {report[:300]}...", phase="GATE_11")
            return "PASS"
        log_action(f"AUTO-GATE 11 REJECTED\n   ⚠️ CRITIQUE: {decision}", phase="GATE_11")
        return f"REPLAN: {decision}"
    
    confirm = input("\n👔 [GATE 11] ท่านพอใจกับผลลัพธ์นี้หรือไม่? (Y=ผ่าน / N=ตีกลับไปวางแผนใหม่): ").strip().upper()
    if confirm == "Y":
        log_action(f"CEO/ORCHESTRATOR APPROVED (Manual)\n   📄 REPORT: {report[:300]}...", phase="GATE_11")
        return "PASS"
    reason = input("📝 ระบุเหตุผลที่ตีกลับ (เพื่อให้ Planner ปรับแผน): ").strip()
    log_action(f"CEO/ORCHESTRATOR REJECTED (Manual)\n   ⚠️ FEEDBACK: {reason}", phase="GATE_11")
    return f"REPLAN: {reason}"

def advisor_final_gate(report: str) -> bool:
    """ด่านที่ 12: ที่ปรึกษา (Advisor) ตรวจสอบ"""
    print_box("🎓 GATE 12: Advisor Final Review", "กำลังตรวจสอบความถูกต้องทางวิชาการ...")
    prompt = f"ในฐานะที่ปรึกษาวิทยานิพนธ์ โปรดตรวจสอบความถูกต้องทางวิชาการจากรายงานนี้: {report}\nตอบ 'PASS' หากผ่าน หรือ 'FAIL: [เหตุผล]' หากต้องแก้ไข"
    decision = llm_helper.call_llm(prompt, "คุณคืออาจารย์ที่ปรึกษาที่เคร่งครัดเรื่องความถูกต้องทางวิชาการ", agent_key="advisor")
    if "PASS" in decision.upper():
        print("  ✅ Advisor: อนุมัติผ่านทางวิชาการ")
        log_action("Advisor APPROVED the work", phase="GATE_12")
        return True
    print(f"  ❌ Advisor: ตีกลับ! {decision}")
    log_action(f"Advisor REJECTED the work: {decision}", phase="GATE_12")
    return False

def editor_final_gate(report: str) -> bool:
    """ด่านที่ 13: Editor Agent ตรวจสอบ"""
    print_box("📰 GATE 13: Editor Final Review", "กำลังตรวจสอบความสวยงามและภาษา...")
    prompt = f"ในฐานะบรรณาธิการ โปรดตรวจสอบภาษาและการจัดรูปแบบจากรายงานนี้: {report}\nตอบ 'PASS' หากผ่าน หรือ 'FAIL: [เหตุผล]' หากต้องแก้ไข"
    decision = llm_helper.call_llm(prompt, "คุณคือบรรณาธิการมืออาชีพที่เน้นความสละสลวยของภาษา", agent_key="editor")
    if "PASS" in decision.upper():
        print("  ✅ Editor: ตรวจสอบภาษาผ่านเรียบร้อย")
        log_action("Editor APPROVED the work", phase="GATE_13")
        return True
    print(f"  ❌ Editor: ตีกลับเรื่องภาษา! {decision}")
    log_action(f"Editor REJECTED the work: {decision}", phase="GATE_13")
    return False

def notify_ceo(report: str):
    """ด่านที่ 15: รายงานผลต่อ CEO (จบบริบูรณ์)"""
    log_action("MISSION COMPLETE: Sent final delivery to CEO", phase="GATE_15")
    print_box("👑 MISSION COMPLETE: FINAL DELIVERY TO CEO", "รายงานผลการปฏิบัติงานต่อท่าน CEO (จบบริบูรณ์)")
    print(f"\n[CEO Notification]: ท่านครับ งานวิทยานิพนธ์สมบูรณ์แบบ 100% แล้วครับ!")
    print(f"สรุปความสำเร็จ: {report[:200]}...")
    print("\n✅ ภารกิจเสร็จสิ้น (จบบริบูรณ์)")

# ──────────────────────────────────────────────
def main():
    is_automated = os.getenv("AUTOMATED") == "1"
    
    if len(sys.argv) > 1:
        initial_msg = sys.argv[1]
        os.environ["AUTOMATED"] = "1"
        is_automated = True
        
        current_msg = initial_msg
        while True: # 🔁 LOOP: Planning & Execution
            plan = create_and_approve_plan(current_msg, automated=True)
            if not plan: break
            
            dispatch_plan(plan, automated=True)
            combine_and_export_step()
            report = generate_final_report(plan)
            print_box("📄 INTERIM REPORT: 🎯 Orchestrator", report, "36")
            
            # --- 🛡️ SUB-LOOP: Review Gates (Step 11-13) ---
            replan_needed = False
            while True:
                # 11. ผู้บริหาร (Orchestrator) ตรวจสอบ
                decision = orchestrator_review_gate(plan, report, automated=True)
                if decision.startswith("REPLAN"):
                    current_msg = f"แก้ไขงานเดิมตามข้อผิดพลาด: {decision.split(':', 1)[1]}"
                    replan_needed = True
                    break # ออกไปวางแผนใหม่
                
                # 12. ที่ปรึกษา (Advisor) ตรวจสอบ
                if not advisor_final_gate(report):
                    print("\n🔄 Advisor ไม่ให้ผ่าน! ตีกลับไปให้ Orchestrator ตรวจสอบใหม่...")
                    continue # วนกลับไปที่ด่าน 11
                
                # 13. Editor Agent ตรวจสอบ
                if not editor_final_gate(report):
                    print("\n🔄 Editor ไม่ให้ผ่าน! ตีกลับไปให้ Orchestrator ตรวจสอบใหม่...")
                    continue # วนกลับไปที่ด่าน 11
                
                # 15. CEO (จบบริบูรณ์)
                notify_ceo(report)
                return # จบภารกิจทั้งหมด
            
            if replan_needed: continue
            break
        return

    clear_screen()
    print_banner()
    print_agent_menu()

    while True:
        try: user_input = input("\n🔹 ผู้บริหาร > ").strip()
        except: break
        if not user_input: continue
        
        # --- [IT TRIGGER] /load/ ---
        if "/load/" in user_input:
            import subprocess
            url = user_input.split("/load/")[1].strip().split()[0]
            print(f"\n[IT] ⚡ Trigger /load/ detected!")
            subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "downloader.py"), url])

        cmd = user_input.lower()
        if cmd == 'quit': break
        elif cmd == 'status': show_tracker(); continue
        elif cmd == 'menu': print_agent_menu(); continue
        elif user_input in AGENT_NUM_MAP:
            agent = AGENT_NUM_MAP[user_input]
            msg = input(f"📝 ส่งให้ {agent}: ")
            dispatch_to_agent(agent, msg)
            continue
        
        # Orchestration Mode with 15-Step Flowchart Synchronization
        current_msg = user_input
        while True: # 🔁 LOOP: Planning & Execution
            plan = create_and_approve_plan(current_msg, automated=is_automated)
            if not plan: break
            
            dispatch_plan(plan, automated=is_automated)
            combine_and_export_step()
            report = generate_final_report(plan)
            print_box("📄 INTERIM REPORT: 🎯 Orchestrator", report, "36")
            
            # --- 🛡️ SUB-LOOP: Review Gates (Step 11-13) ---
            replan_needed = False
            while True:
                # 11. ผู้บริหาร (Orchestrator) ตรวจสอบ
                decision = orchestrator_review_gate(plan, report, automated=is_automated)
                if decision.startswith("REPLAN"):
                    current_msg = f"ปรับปรุงแผนงานใหม่ตาม Feedback: {decision.split(':', 1)[1]}"
                    print(f"\n🔄 ระบบกำลังตีกลับไปวางแผนใหม่ตามคำสั่งท่าน...")
                    replan_needed = True
                    break # ออกไปวางแผนใหม่
                
                # 12. ที่ปรึกษา (Advisor) ตรวจสอบ
                if not advisor_final_gate(report):
                    print("\n🔄 Advisor ไม่ให้ผ่าน! ตีกลับไปให้ท่าน (Orchestrator) ตรวจสอบความเรียบร้อยอีกครั้ง...")
                    continue # วนกลับไปที่ด่าน 11
                    
                # 13. Editor Agent ตรวจสอบ
                if not editor_final_gate(report):
                    print("\n🔄 Editor ไม่ให้ผ่าน! ตีกลับไปให้ท่าน (Orchestrator) ตรวจสอบความสวยงามอีกครั้ง...")
                    continue # วนกลับไปที่ด่าน 11
                
                # 15. CEO (จบบริบูรณ์)
                notify_ceo(report)
                return # จบภารกิจทั้งหมด
                
            if replan_needed: continue
            break

if __name__ == "__main__":
    main()
