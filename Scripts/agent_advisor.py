"""
============================================================
  👨‍🏫 ADVISOR AGENT — ที่ปรึกษา
  เรียกจาก main.py หรือรันตรง:
    python Scripts/agent_advisor.py "ข้อความงาน"
============================================================
"""
import os, sys, io, json
from datetime import datetime
import llm_helper

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLE_FILE = os.path.join(PROJECT_ROOT, "Agent", "03_Advisor.md")
TODO_DIR = os.path.join(PROJECT_ROOT, "Workspace", "Decision", "advisor_tasks")
FEEDBACK_DIR = os.path.join(PROJECT_ROOT, "Meetings", "feedback")
PREP_DIR = os.path.join(PROJECT_ROOT, "Meetings", "preparation")
LONG_MEM_DIR = os.path.join(PROJECT_ROOT, "Memory", "Long Memory")
PREF_FILE = os.path.join(LONG_MEM_DIR, "advisor_preferences.md")
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")

for d in [TODO_DIR, FEEDBACK_DIR, PREP_DIR, LONG_MEM_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Role ──
def load_my_role() -> str:
    if os.path.exists(ROLE_FILE):
        with open(ROLE_FILE, "r", encoding="utf-8") as f: return f.read()
    return "(ไม่พบ role file)"

def get_my_skills() -> list[str]:
    return [l.strip().replace("### ","") for l in load_my_role().split("\n") if l.strip().startswith("### SK-")]

# ── TODO ──
def _fp(): return os.path.join(TODO_DIR, "advisor_todo.json")
def load_todo() -> list[dict]:
    if os.path.exists(_fp()):
        with open(_fp(),"r",encoding="utf-8") as f: return json.load(f)
    return []
def save_todo(t):
    with open(_fp(),"w",encoding="utf-8") as f: json.dump(t,f,ensure_ascii=False,indent=2)

def add_todo(desc, skill_id=""):
    todos = load_todo()
    t = {"id":len(todos)+1,"description":desc,"skill_id":skill_id,
         "status":"pending","result":"","output_file":"",
         "created":datetime.now().isoformat(),"updated":"",
         "review":"","review_note":""}
    todos.append(t); save_todo(todos); return t

def update_todo(tid, **kw):
    todos = load_todo()
    for t in todos:
        if t["id"]==tid:
            for k,v in kw.items(): t[k]=v
            t["updated"]=datetime.now().isoformat(); break
    save_todo(todos)

SI = {"pending":"⬜","in_progress":"🔄","done":"✅","submitted":"📤",
      "accepted":"🎉","rejected":"❌","revision_needed":"🔁"}

def show_todo():
    todos = load_todo()
    if not todos: print("\n  📭 ไม่มีงานในแผนการดำเนินการ (TODO)"); return
    print("\n  " + "─"*20 + " 🛠️ Implementation Status " + "─"*20)
    print("  ┌─────┬──────────────────────────────────┬──────────┬────────┐")
    print("  │  #  │ งาน                              │ สถานะ    │ Review │")
    print("  ├─────┼──────────────────────────────────┼──────────┼────────┤")
    for t in todos:
        ri = SI.get(t["review"],"  —") if t["review"] else "  —"
        print(f"  │ {t['id']:>3} │ {t['description'][:30]:<32} │ {SI.get(t['status'],'❓'):<8} │ {ri:<6} │")
    print("  └─────┴──────────────────────────────────┴──────────┴────────┘")
    done_c = sum(1 for t in todos if t["status"] in ("done","submitted","accepted"))
    pct = int(done_c/len(todos)*100) if todos else 0
    print(f"  Progress: [{'█'*(pct//10)}{'░'*(10-pct//10)}] {pct}% ({done_c}/{len(todos)})")

# ── Skills ──
SKILL_MENU = {
    "1": ("SK-ADV-01","Academic Review","ตรวจคุณภาพงานวิชาการเชิงลึก"),
    "2": ("SK-ADV-02","Feedback Generation","สร้าง Feedback และสั่งแก้"),
    "3": ("SK-ADV-03","Gate Approval","อนุมัติผ่าน Phase (Gate Keeper)"),
    "4": ("SK-ADV-04","Preference Tracking","จดจำและบันทึกสไตล์ของที่ปรึกษา"),
    "5": ("SK-ADV-05","Meeting Preparation","เตรียมตัวก่อนเข้าพบอาจารย์"),
}

def run_skill(num):
    if num not in SKILL_MENU: print("  ❌ เลขไม่ถูกต้อง"); return
    sid, name, desc = SKILL_MENU[num]
    print(f"\n  👨‍🏫 เริ่มงาน: {name}\n     {desc}\n     Skill: {sid}")
    print("-"*50)

    detail = ""
    output_file = ""

    if num == "1":
        phase = input("  📄 ตรวจงาน Phase/บทไหน: ").strip()
        detail = f"Academic Review: {phase}"
        checks = ["RQ ชัดเจนตอบได้","Methodology เหมาะสม","Literature ครอบคลุม","น่าเชื่อถือ","ข้อมูลสอดคล้องกัน"]
        print("\n  🔍 ตรวจสอบทางวิชาการ:")
        issues = 0
        for c in checks:
            r = input(f"     ✓ {c} [Y/N]: ").strip().upper()
            if r == "N": issues += 1
        result_text = f"พบ {issues} จุดอ่อน" if issues > 0 else "คุณภาพผ่านเกณฑ์"
        output_file = os.path.join(FEEDBACK_DIR, f"review_{datetime.now():%Y%m%d}.md")
        if input("\n  💾 บันทึก Review Report? [Y/N]: ").strip().upper() in ("Y", ""):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Academic Review: {phase}\n- **Date:** {datetime.now():%Y-%m-%d}\n- **Issues found:** {issues}\n")
            print(f"  💾 บันทึกที่ {output_file}")
        else: output_file = ""

    elif num == "2":
        topic = input("  💬 สร้าง Feedback เรื่องอะไร: ").strip()
        detail = f"Generate Feedback: {topic}"
        critical = int(input("  🔴 ข้อผิดพลาดร้ายแรง (Critical): ").strip() or "0")
        major = int(input("  🟡 ข้อผิดพลาดสำคัญ (Major): ").strip() or "0")
        minor = int(input("  🟢 ข้อผิดพลาดเล็กน้อย (Minor): ").strip() or "0")
        result_text = f"C:{critical} M:{major} m:{minor}"
        output_file = os.path.join(FEEDBACK_DIR, f"feedback_{datetime.now():%Y%m%d}.md")
        if input("\n  💾 บันทึก Feedback Document? [Y/N]: ").strip().upper() in ("Y", ""):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Feedback: {topic}\n- Critical: {critical}\n- Major: {major}\n- Minor: {minor}\n")
            print(f"  💾 บันทึกที่ {output_file}")
        else: output_file = ""

    elif num == "3":
        phase = input("  🚧 ขออนุมัติผ่าน Phase ไหน: ").strip()
        detail = f"Gate Approval: {phase}"
        critical = int(input("  🔴 มี Critical Feedback ค้างกี่ข้อ: ").strip() or "0")
        major = int(input("  🟡 มี Major Feedback ค้างกี่ข้อ: ").strip() or "0")
        
        print("\n  📋 Gate Review Summary:")
        print(f"  🔴 Critical: {critical}")
        print(f"  🟡 Major: {major}")
        if critical == 0 and major == 0:
            appr = input("  ✅ Approve to next phase? [Y/N]: ").strip().upper()
            result_text = "✅ APPROVE" if appr in ("Y","") else "⏸️ HOLD"
        else:
            print("  ❌ ยังไม่สามารถ approve ได้ — ต้องแก้ไข Critical/Major ก่อน")
            result_text = "❌ REVISE"
        print(f"  สรุป: {result_text}")

    elif num == "4":
        pref = input("  💡 ลักษณะ/สไตล์ที่อาจารย์ชอบ (เช่น ชอบ APA): ").strip()
        detail = "อัปเดตสไตล์ของอาจารย์"
        if not os.path.exists(PREF_FILE):
            with open(PREF_FILE, "w", encoding="utf-8") as f: f.write("# Advisor Preferences\n\n")
        with open(PREF_FILE, "a", encoding="utf-8") as f:
            f.write(f"- {pref}\n")
        output_file = PREF_FILE
        result_text = f"เพิ่ม: {pref}"
        print(f"  💾 บันทึกลง Long Memory: {PREF_FILE}")

    elif num == "5":
        date = input("  📅 วันที่นัดพบ: ").strip()
        detail = f"เตรียมความพร้อมพบนัดอาจารย์ {date}"
        q = input("  ❓ คำถามที่เตรียมไปถาม: ").strip()
        output_file = os.path.join(PREP_DIR, f"meeting_prep_{datetime.now():%Y%m%d}.md")
        if input("\n  💾 บันทึก Prep Doc? [Y/N]: ").strip().upper() in ("Y", ""):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Meeting Prep: {date}\n- **Questions:** {q}\n")
            print(f"  💾 บันทึกที่ {output_file}")
        else: output_file = ""
        result_text = "เตรียมเอกสารสำเร็จ"

    if not detail: detail = f"{name}: {desc}"
    
    todo = add_todo(detail, sid)
    print(f"  ✅ สร้าง TODO #{todo['id']}: {detail}")

    start = input("  ▶️ เริ่มทำ/บันทึกผลเลย? [Y/N]: ").strip().upper()
    if start in ("Y",""):
        update_todo(todo["id"], status="in_progress")
        print(f"\n  🔄 กำลังทำ: {detail}")
        if 'result_text' not in locals():
            result_text = input("  📄 ผลลัพธ์สรุป: ").strip()
        if not output_file:
            output_file = input("  📂 Output file path (Enter=ไม่มี): ").strip()
        
        update_todo(todo["id"], status="done",
                    result=result_text or "(ไม่ได้บันทึก)", output_file=output_file)
        print(f"  ✅ TODO #{todo['id']} เสร็จ!")
        if input("  📤 Submit ให้ผู้บริหาร? [Y/N]: ").strip().upper() in ("Y",""):
            update_todo(todo["id"], status="submitted")
            print(f"  📤 ส่งแล้ว")

def generate_report(work_details: str):
    """สร้างรายงานสรุปผลการทำงาน"""
    my_role = load_my_role()
    print(f"\n  🧠 กำลังสรุปรายงาน (Reporting) เพื่อส่งผู้บริหาร...")
    report_content = llm_helper.get_report_response("Advisor Agent", work_details, my_role, agent_key="advisor")
    
    # UI Helper สำหรับ Advisor คือ print_box สี 33 (Yellow/Orange)
    # แต่ในไฟล์ advisor_agent.py ไม่ได้นิยาม print_box ไว้แบบสมบูรณ์เหมือน Research/Writer
    # ผมจะนิยามให้เลยเพื่อความสวยงาม
    print_box("📄 REPORT: 👨‍🏫 Advisor Agent", report_content, "33")
    
    # บันทึกลงไฟล์
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(PROJECT_ROOT, "Output", "reports")
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, f"advisor_report_{timestamp}.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# 📊 Advisor Report\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(report_content)
    
    log_action(f"สร้างรายงานสำเร็จ: {os.path.basename(report_file)}")
    print(f"  💾 บันทึกรายงาน: {report_file}")
    return report_content

def print_box(title, content, color_code="33"):
    """แสดงกล่องข้อความสไตล์ Roleplay"""
    print(f"\n\033[{color_code}m┌" + "─" * 68 + "┐")
    print(f"│ {title:<66} │")
    print("├" + "─" * 68 + "┤")
    for line in content.split('\n'):
        while len(line) > 66:
            print(f"│ {line[:66]:<66} │")
            line = line[66:]
        print(f"│ {line:<66} │")
    print("└" + "─" * 68 + "┘\033[0m")

# ── Submit / Review / Revision ──
def submit_to_orchestrator():
    todos = load_todo()
    done = [t for t in todos if t["status"]=="done"]
    if not done:
        print("\n  📭 ไม่มีงาน done รอ submit")
        return
    print("\n  📋 งานพร้อม submit:")
    for t in done: print(f"    ✅ #{t['id']}: {t['description'][:40]}")
    ch = input("  [A] ทั้งหมด / [เลข] เฉพาะ / [N] ยกเลิก: ").strip().upper()
    if ch=="A":
        for t in done: update_todo(t["id"], status="submitted")
        print(f"  📤 ส่ง {len(done)} งานแล้ว")
    elif ch.isdigit():
        tid=int(ch)
        if any(t["id"]==tid for t in done):
            update_todo(tid, status="submitted"); print(f"  📤 ส่ง #{tid}")

def orchestrator_review():
    todos = load_todo()
    submitted = [t for t in todos if t["status"]=="submitted"]
    if not submitted: print("\n  📭 ไม่มีงานรอ review"); return
    print("\n"+"="*60)
    print("  👨‍💼 ผู้บริหาร — Review งาน Advisor Agent")
    print("="*60)
    for t in submitted:
        print(f"\n  ─── TODO #{t['id']} ───")
        print(f"  📝 {t['description']}")
        print(f"  📄 ผล: {t['result']}")
        if t["output_file"]: print(f"  📂 File: {t['output_file']}")
        print("  [A] Accept  [R] Revision  [X] Reject  [S] Skip")
        d = input("  ผู้บริหาร > ").strip().upper()
        if d=="A":
            update_todo(t["id"], status="accepted", review="accepted")
            print(f"  ✅ #{t['id']} ACCEPTED")
        elif d=="R":
            note = input("  📝 สิ่งที่ต้องปรับ: ").strip()
            update_todo(t["id"], status="in_progress", review="revision_needed", review_note=note)
            print(f"  🔁 #{t['id']} ตีกลับ")
        elif d=="X":
            note = input("  📝 เหตุผล: ").strip()
            update_todo(t["id"], status="rejected", review="rejected", review_note=note)
            print(f"  ❌ #{t['id']} REJECTED")
    print("\n  📊 สรุป:"); show_todo()

def handle_revisions():
    todos = load_todo()
    revs = [t for t in todos if t["review"]=="revision_needed" and t["status"]=="in_progress"]
    if not revs: print("\n  ✅ ไม่มีงานตีกลับ"); return
    for t in revs:
        print(f"\n  ─── #{t['id']} ───")
        print(f"  📝 {t['description']}\n  📄 ผลเดิม: {t['result']}\n  💬 เหตุผล: {t['review_note']}")
        if input("  ▶️ แก้ไข? [Y/N]: ").strip().upper() in ("Y",""):
            nr = input("  📄 ผลใหม่: ").strip()
            update_todo(t["id"], result=nr or t["result"], status="done", review="", review_note="")
            print(f"  ✅ แก้ #{t['id']} แล้ว — พร้อม submit")

def log_action(action, phase="IMPLEMENTATION"):
    with open(os.path.join(LOGS_DIR,"advisor_agent.log"),"a",encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [Advisor] [{phase}] {action}\n")

# ── UI ──
def print_banner():
    print("\n"+"="*60)
    print("  👨‍🏫 ADVISOR AGENT — ที่ปรึกษาวิทยานิพนธ์")
    print("="*60)
    print(f"  📅 {datetime.now():%Y-%m-%d %H:%M}")
    print(f"  📂 Project: {PROJECT_ROOT}")
    print("="*60)
    skills = get_my_skills()
    if skills:
        print("  📋 My Skills:")
        for s in skills: print(f"     • {s}")
    todos = load_todo()
    p=sum(1 for t in todos if t["status"]=="pending")
    ip=sum(1 for t in todos if t["status"]=="in_progress")
    sb=sum(1 for t in todos if t["status"]=="submitted")
    rv=sum(1 for t in todos if t["review"]=="revision_needed")
    if todos: print(f"\n  📊 ⬜{p} รอ | 🔄{ip} ทำ | 📤{sb} review | 🔁{rv} ตีกลับ")
    print()

def print_menu():
    print("  ┌─────────────────────────────────────────┐")
    print("  │        📋 Advisor Agent Menu             │")
    print("  ├─────┬───────────────────────────────────┤")
    print("  │  1  │ 🔍 Academic Review                │")
    print("  │  2  │ 📝 Feedback Generation            │")
    print("  │  3  │ 🚧 Gate Approval                  │")
    print("  │  4  │ 🧠 Preference Tracking            │")
    print("  │  5  │ 💼 Meeting Preparation            │")
    print("  ├─────┼───────────────────────────────────┤")
    print("  │todo │ 🛠️ Implementation (TODO List)           │")
    print("  │sub  │ 📤 Submit ให้ผู้บริหาร             │")
    print("  │rev  │ 🔁 งานตีกลับ                      │")
    print("  │role │ 📄 ดู Role ตัวเอง                  │")
    print("  │back │ 🔙 กลับ main                      │")
    print("  └─────┴───────────────────────────────────┘")

# ── Main ──
def main(initial_message=""):
    print_banner(); print_menu()
    if initial_message and initial_message != "(ไม่มีข้อความ)":
        # ดึง Role มาให้ LLM วิเคราะห์
        my_role = load_my_role()
        
        # ขอความเห็นจาก LLM (Ollama/Online)
        print(f"\n  🧠 กำลังติดต่อ LLM เพื่อเตรียมการตอบกลับ...")
        roleplay_msg = llm_helper.get_roleplay_response("Advisor Agent", initial_message, my_role, agent_key="advisor")
        
        print_box("🎭 ROLEPLAY: 👨‍🏫 Advisor Agent", roleplay_msg, "33")
        
        # --- Thinking Phase ---
        print(f"\n  🧠 กำลังวิเคราะห์งาน (Thinking)...")
        thinking_msg = llm_helper.get_thinking_response("Advisor Agent", initial_message, my_role, agent_key="advisor")
        print_box("💭 THINKING: 👨‍🏫 Advisor Agent", thinking_msg, "33")
        
        # 📝 DEEP LOG: บันทึกเกณฑ์การตรวจสอบ
        log_action(f"ADVISOR CRITERIA:\n   💡 โจทย์ตรวจสอบ: {initial_message}\n   🧠 เกณฑ์การพิจารณา: {thinking_msg[:500]}...", phase="THINKING")

        # --- Implementation Phase ---
        print(f"\n  " + "═"*20 + " 🛠️ Implementation Phase " + "═"*20)
        print(f"  📨 งานที่ได้รับจากผู้บริหาร: \"{initial_message[:80]}\"")
        
        # 🤖 AUTOMATED: ประมวลผลงานและ Exit ทันทีเพื่อส่งคิวต่อให้ main.py
        is_auto = os.getenv("AUTOMATED") == "1"
        if is_auto:
            t = add_todo(initial_message)
            print(f"  🔍 [AUTO] กำลังประมวลผลคำปรึกษา (Advisor Implementation)...")
            
            # --- Substantive Implementation Call ---
            implementation_prompt = f"""
            คุณคือ Advisor Agent จงกรอกข้อมูลลงในแบบฟอร์ม 'บันทึกการให้คำปรึกษา' นี้ให้สมบูรณ์ "เดี๋ยวนี้"! 
            ห้ามมีประโยคทักทาย ห้ามบอกว่าจะทำภายหลัง ห้ามมีเนื้อหาอื่นนอกจากรายงานนี้:
            
            --- บันทึกการให้คำปรึกษา (Advisor Consultancy Note) ---
            หัวข้อ: {initial_message}
            
            1. ขอบเขตการวิจัย (Research Scope):
            [เขียนรายละเอียดขอบเขต LCA และความสำคัญอย่างน้อย 3 ย่อหน้า]
            
            2. คำถามวิจัยและวัตถุประสงค์ (RQ & Objectives):
            [ระบุคำถามวิจัยอย่างน้อย 3 ข้อ และวัตถุประสงค์ที่สอดคล้องกับมาตรฐาน ISO 14040/44]
            
            3. ข้อเสนอแนะเชิงเทคนิค (Technical Advice):
            [ระบุเครื่องมือที่ต้องใช้ และจุดเสี่ยงที่ต้องระวัง]
            
            4. ขั้นตอนถัดไป (Next Steps):
            [ระบุงานที่ Research Agent และ Writer Agent ต้องทำต่อ]
            
            --- จบรายงาน ---
            
            แนวคิดจากการวิเคราะห์ (Thinking): {thinking_msg}
            """
            final_result = llm_helper.get_roleplay_response("Advisor Agent", implementation_prompt, my_role, agent_key="advisor")
            
            log_action(f"ADVISOR IMPLEMENTATION COMPLETED (TODO #{t['id']})", phase="IMPLEMENTATION")
            update_todo(t["id"], status="done", result=final_result)
            generate_report(f"การให้คำปรึกษาอัตโนมัติสำเร็จ:\n{final_result}")
            
            print("\n✅ [AUTO] งานเสร็จสิ้น — ส่งคืนคำปรึกษาให้ผู้บริหาร")
            return
            
        if input("  ➕ เพิ่มเข้าแผนการดำเนินการ (TODO)? [Y/N]: ").strip().upper() in ("Y",""):
            t=add_todo(initial_message); print(f"  ✅ เพิ่มแผนงานสำเร็จ #{t['id']}")
            
            # 📝 DEEP LOG: บันทึกการรับงานตรวจสอบ
            # --- Auto-execution log ---
            log_action(f"ดำเนินการตามแผนงาน TODO #{t['id']}", phase="IMPLEMENTATION")
            generate_report(f"เริ่มดำเนินการ: {initial_message}\nสร้างแผนงาน (TODO) #{t['id']}")
    while True:
        print("\n"+"-"*50)
        try: cmd = input("  👨‍🏫 Advisor > ").strip().lower()
        except: print("\n  🔙 กลับ"); break
        if not cmd: continue
        if cmd in ("back","quit"): print("  🔙 กลับ main"); break
        if cmd=="menu": print_menu(); continue
        if cmd=="todo": show_todo(); continue
        if cmd in ("sub","submit"): submit_to_orchestrator(); continue
        if cmd=="report":
            todos = load_todo()
            summary = "\n".join([f"- {t['description']} ({t['status']})" for t in todos[-5:]])
            generate_report(f"สถานะงานล่าสุด:\n{summary}")
            continue
        if cmd in ("rev","revision"): handle_revisions(); continue
        if cmd=="role": print("\n"+load_my_role()); continue
        if cmd=="review": orchestrator_review(); continue
        if cmd in SKILL_MENU: run_skill(cmd); log_action(f"Skill: {SKILL_MENU[cmd][1]}"); continue
        print(f"  ➕ ไม่พบ '{cmd}' — เพิ่มเป็น TODO?")
        if input("  [Y/N]: ").strip().upper() in ("Y",""): 
            t=add_todo(cmd); print(f"  ✅ TODO #{t['id']}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "")
