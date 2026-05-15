"""
============================================================
  ✅ QA Agent — ควบคุมคุณภาพ
  เรียกจาก main.py หรือรันตรง:
    python Scripts/agent_qa.py "ข้อความงาน"
============================================================
"""
import os, sys, io, json
from datetime import datetime
import llm_helper

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLE_FILE = os.path.join(PROJECT_ROOT, "Agent", "07_QA.md")
TODO_DIR = os.path.join(PROJECT_ROOT, "Workspace", "Decision", "qa_tasks")
TEST_DIR = os.path.join(PROJECT_ROOT, "Test")
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")

for d in [TODO_DIR, TEST_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Roleplay UI Helpers ──
def print_box(title, content, color_code="31"): # Default Red for QA
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

# ── Role ──
def load_my_role() -> str:
    if os.path.exists(ROLE_FILE):
        with open(ROLE_FILE, "r", encoding="utf-8") as f: return f.read()
    return "(ไม่พบ role file)"

def get_my_skills() -> list[str]:
    return [l.strip().replace("### ","") for l in load_my_role().split("\n") if l.strip().startswith("### SK-")]

# ── TODO ──
def _fp(): return os.path.join(TODO_DIR, "qa_todo.json")
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
         "review":"","review_note":"","issues_found":0,"pass":None}
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
    print("  ┌─────┬──────────────────────────────────┬──────────┬────────┬──────┐")
    print("  │  #  │ งาน                              │ สถานะ    │ Review │ Pass │")
    print("  ├─────┼──────────────────────────────────┼──────────┼────────┼──────┤")
    for t in todos:
        ri = SI.get(t["review"],"  —") if t["review"] else "  —"
        ps = "✅" if t.get("pass") == True else ("❌" if t.get("pass") == False else " —")
        print(f"  │ {t['id']:>3} │ {t['description'][:30]:<32} │ {SI.get(t['status'],'❓'):<8} │ {ri:<6} │  {ps}  │")
    print("  └─────┴──────────────────────────────────┴──────────┴────────┴──────┘")
    done_c = sum(1 for t in todos if t["status"] in ("done","submitted","accepted"))
    pct = int(done_c/len(todos)*100) if todos else 0
    print(f"  Progress: [{'█'*(pct//10)}{'░'*(10-pct//10)}] {pct}% ({done_c}/{len(todos)})")

# ── Skills ──
SKILL_MENU = {
    "1": ("SK-QA-01","Content Consistency","ตรวจความสอดคล้องระหว่าง chapters"),
    "2": ("SK-QA-02","Plagiarism Check","ตรวจ similarity / การลอก"),
    "3": ("SK-QA-03","Data Validation","ตรวจข้อมูล ตัวเลข calculations"),
    "4": ("SK-QA-04","Format Validation","ตรวจรูปแบบตาม template"),
    "5": ("SK-QA-05","Final Checklist","ตรวจสอบทุกอย่างก่อน submit"),
}

# ── Checklist items for Final Check ──
FINAL_CHECKLIST = [
    "สารบัญตรงกับเนื้อหา",
    "เลขหน้าถูกต้อง",
    "ภาพ/ตารางมี caption ครบ",
    "References ครบทุกตัว",
    "Abstract ไม่เกิน word limit",
    "ไม่มี TODO/FIXME ค้าง",
    "Spell check ผ่าน",
    "ชื่อตาราง/ภาพ สอดคล้อง",
    "Appendix ครบ",
]

def run_skill(num):
    if num not in SKILL_MENU: print("  ❌ เลขไม่ถูกต้อง"); return
    sid, name, desc = SKILL_MENU[num]
    print(f"\n  ✅ เริ่มตรวจ: {name}\n     {desc}\n     Skill: {sid}")
    print("-"*50)

    detail = ""
    issues = 0
    passed = None

    if num == "1":
        # Content Consistency
        target = input("  📄 ตรวจไฟล์/บทไหน (Enter=ทั้งหมด): ").strip()
        detail = f"Consistency Check: {target if target else 'ทั้งหมด'}"
        print("\n  🔍 รายการตรวจ:")
        checks = ["ตัวเลขตรงกันทุกจุด","คำศัพท์สม่ำเสมอ","อ้างอิงภายในถูกต้อง","ตาราง/ภาพตรง"]
        for c in checks:
            r = input(f"     {c} [Y/N]: ").strip().upper()
            if r == "N": issues += 1
        passed = issues == 0

    elif num == "2":
        # Plagiarism
        target = input("  📄 ตรวจไฟล์/บทไหน: ").strip()
        detail = f"Plagiarism Check: {target if target else 'ทั้งหมด'}"
        try:
            score = int(input("  📊 Similarity score (%): ").strip() or "0")
        except ValueError:
            score = 0
        threshold = 20
        passed = score < threshold
        issues = 0 if passed else 1
        print(f"\n  {'✅' if passed else '❌'} Similarity: {score}% (threshold: {threshold}%)")
        if not passed:
            print("  ⚠️ ต้อง paraphrase เนื้อหาที่ similarity สูง")

    elif num == "3":
        # Data Validation
        detail = input("  📊 ตรวจข้อมูลอะไร: ").strip() or "Data Validation"
        checks = ["ตัวเลขถูกต้อง","หน่วยถูกต้อง","สูตรคำนวณถูก","ตาราง-กราฟตรงกัน","N/sample size ถูก"]
        print("\n  🔍 ตรวจข้อมูล:")
        for c in checks:
            r = input(f"     {c} [Y/N]: ").strip().upper()
            if r == "N": issues += 1
        passed = issues == 0

    elif num == "4":
        # Format Validation
        template = input("  📐 Template (มหาวิทยาลัย/journal): ").strip()
        detail = f"Format Check: {template if template else 'ทั่วไป'}"
        checks = ["Margins ถูก","Font/Size ถูก","Spacing ถูก","Numbering ถูก","Header/Footer ถูก","Page break ถูก"]
        print("\n  🔍 ตรวจรูปแบบ:")
        for c in checks:
            r = input(f"     {c} [Y/N]: ").strip().upper()
            if r == "N": issues += 1
        passed = issues == 0

    elif num == "5":
        # Final Checklist
        detail = "Final Submission Checklist"
        print("\n  📋 Final Checklist:")
        for item in FINAL_CHECKLIST:
            r = input(f"     [ ] {item} [Y/N]: ").strip().upper()
            if r != "Y": issues += 1
        passed = issues == 0
        print(f"\n  {'✅ พร้อม submit!' if passed else f'❌ ยังไม่ผ่าน ({issues} ข้อ)'}")

    if not detail: detail = f"{name}: {desc}"

    # สร้าง report file
    report_file = ""
    report_name = f"qa_{sid.lower().replace('-','_')}_{datetime.now():%Y%m%d_%H%M}.md"
    report_path = os.path.join(TEST_DIR, report_name)
    save_report = input("\n  💾 บันทึก report? [Y/N]: ").strip().upper()
    if save_report in ("Y",""):
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# QA Report: {name}\n\n")
            f.write(f"- **Date:** {datetime.now():%Y-%m-%d %H:%M}\n")
            f.write(f"- **Skill:** {sid}\n")
            f.write(f"- **Detail:** {detail}\n")
            f.write(f"- **Issues Found:** {issues}\n")
            f.write(f"- **Result:** {'✅ PASS' if passed else '❌ FAIL'}\n")
        report_file = report_path
        print(f"  💾 Report: {report_path}")

    # สร้าง TODO
    todo = add_todo(detail, sid)
    result_text = f"{'PASS' if passed else 'FAIL'} — {issues} issues"
    update_todo(todo["id"], status="done", result=result_text,
                output_file=report_file, issues_found=issues, **{"pass": passed})
    print(f"\n  {'✅' if passed else '❌'} QA #{todo['id']}: {result_text}")

    if input("  📤 Submit ให้ผู้บริหาร? [Y/N]: ").strip().upper() in ("Y",""):
        update_todo(todo["id"], status="submitted")
        print("  📤 ส่งแล้ว")

def generate_report(work_details: str):
    """สร้างรายงานสรุปผลการทำงาน"""
    my_role = load_my_role()
    print(f"\n  🧠 กำลังสรุปรายงาน (Reporting) เพื่อส่งผู้บริหาร...")
    report_content = llm_helper.get_report_response("QA Agent", work_details, my_role, agent_key="qa")
    
    print_box("📄 REPORT: ✅ QA Agent", report_content, "31")
    
    # บันทึกลงไฟล์
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(PROJECT_ROOT, "Output", "reports")
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, f"qa_report_{timestamp}.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# 📊 QA Report\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(report_content)
    
    log_action(f"สร้างรายงานสำเร็จ: {os.path.basename(report_file)}")
    print(f"  💾 บันทึกรายงาน: {report_file}")
    return report_content

# ── Submit / Review / Revision ──
def submit_to_orchestrator():
    todos = load_todo()
    done = [t for t in todos if t["status"]=="done"]
    if not done:
        print("\n  📭 ไม่มีงาน done รอ submit")
        return
    print("\n  📋 งานพร้อม submit:")
    for t in done:
        ps = "✅PASS" if t.get("pass") else "❌FAIL"
        print(f"    {ps} #{t['id']}: {t['description'][:40]}")
    ch = input("  [A] ทั้งหมด / [เลข] เฉพาะ / [N] ยกเลิก: ").strip().upper()
    if ch=="A":
        for t in done: update_todo(t["id"], status="submitted")
        print(f"  📤 ส่ง {len(done)} งาน")
    elif ch.isdigit():
        tid=int(ch)
        if any(t["id"]==tid for t in done):
            update_todo(tid, status="submitted"); print(f"  📤 ส่ง #{tid}")

def orchestrator_review():
    todos = load_todo()
    submitted = [t for t in todos if t["status"]=="submitted"]
    if not submitted: print("\n  📭 ไม่มีงานรอ review"); return
    print("\n"+"="*60)
    print("  👨‍💼 ผู้บริหาร — Review งาน QA Agent")
    print("="*60)
    for t in submitted:
        ps = "✅ PASS" if t.get("pass") else "❌ FAIL"
        print(f"\n  ─── QA #{t['id']} ───")
        print(f"  📝 {t['description']}")
        print(f"  📊 ผล: {t['result']} | {ps}")
        print(f"  🐛 Issues: {t.get('issues_found',0)}")
        if t["output_file"]: print(f"  📂 Report: {t['output_file']}")
        print("  [A] Accept  [R] Revision  [X] Reject  [S] Skip")
        d = input("  ผู้บริหาร > ").strip().upper()
        if d=="A":
            update_todo(t["id"], status="accepted", review="accepted")
            print(f"  ✅ #{t['id']} ACCEPTED")
        elif d=="R":
            note = input("  📝 สิ่งที่ต้องตรวจเพิ่ม: ").strip()
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
        if input("  ▶️ ตรวจใหม่? [Y/N]: ").strip().upper() in ("Y",""):
            nr = input("  📄 ผลใหม่: ").strip()
            update_todo(t["id"], result=nr or t["result"],
                        status="done", review="", review_note="")
            print(f"  ✅ ตรวจ #{t['id']} ใหม่แล้ว — พร้อม submit")

def log_action(action, phase="IMPLEMENTATION"):
    with open(os.path.join(LOGS_DIR,"qa_agent.log"),"a",encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [QA] [{phase}] {action}\n")

# ── UI ──
def print_banner():
    print("\n"+"="*60)
    print("  ✅ QA AGENT — ควบคุมคุณภาพ")
    print("="*60)
    print(f"  📅 {datetime.now():%Y-%m-%d %H:%M}")
    print(f"  📂 Project: {PROJECT_ROOT}")
    print("="*60)
    skills = get_my_skills()
    if skills:
        print("  📋 My Skills:")
        for s in skills: print(f"     • {s}")
    todos = load_todo()
    if todos:
        p=sum(1 for t in todos if t["status"]=="pending")
        sb=sum(1 for t in todos if t["status"]=="submitted")
        ps=sum(1 for t in todos if t.get("pass")==True)
        fl=sum(1 for t in todos if t.get("pass")==False)
        print(f"\n  📊 ⬜{p} รอ | 📤{sb} review | ✅{ps} pass | ❌{fl} fail")
    print()

def print_menu():
    print("  ┌─────────────────────────────────────────┐")
    print("  │        📋 QA Agent Menu                  │")
    print("  ├─────┬───────────────────────────────────┤")
    print("  │  1  │ 🔍 Content Consistency Check      │")
    print("  │  2  │ 📝 Plagiarism Check               │")
    print("  │  3  │ 📊 Data Validation                │")
    print("  │  4  │ 📐 Format Validation              │")
    print("  │  5  │ 📋 Final Checklist                │")
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
        roleplay_msg = llm_helper.get_roleplay_response("QA Agent", initial_message, my_role, agent_key="qa")
        
        print_box("🎭 ROLEPLAY: ✅ QA Agent", roleplay_msg, "31")
        
        # --- Thinking Phase ---
        print(f"\n  🧠 กำลังวิเคราะห์งาน (Thinking)...")
        thinking_msg = llm_helper.get_thinking_response("QA Agent", initial_message, my_role, agent_key="qa")
        print_box("💭 THINKING: ✅ QA Agent", thinking_msg, "31")
        
        # 📝 DEEP LOG: บันทึกแผนการตรวจสอบคุณภาพ
        log_action(f"QA STRATEGY:\n   💡 โจทย์ตรวจสอบ: {initial_message}\n   🧠 แผนการ Verification: {thinking_msg[:500]}...", phase="THINKING")

        # --- Implementation Phase ---
        print(f"\n  " + "═"*20 + " 🛠️ Implementation Phase " + "═"*20)
        print(f"  📨 งานที่ได้รับจากผู้บริหาร: \"{initial_message[:80]}\"")
        
        # 🤖 AUTOMATED: ประมวลผลงานและ Exit ทันทีเพื่อส่งคิวต่อให้ main.py
        is_auto = os.getenv("AUTOMATED") == "1"
        if is_auto:
            t = add_todo(initial_message)
            print(f"  🔍 [AUTO] กำลังดำเนินการตรวจสอบคุณภาพ (QA Implementation)...")
            
            # --- Substantive Implementation Call ---
            implementation_prompt = f"""
            ในฐานะ QA Agent จงดำเนินการตรวจสอบคุณภาพตามแผนงานนี้:
            คำสั่ง: {initial_message}
            แผนการตรวจสอบ: {thinking_msg}
            
            จงเขียน 'รายงานการตรวจสอบคุณภาพ (Quality Assessment Report)' ฉบับสมบูรณ์
            โดยระบุจุดที่ผ่าน มาตรฐานที่ใช้ และข้อเสนอแนะเพื่อการปรับปรุง (ถ้ามี)
            """
            final_result = llm_helper.get_roleplay_response("QA Agent", implementation_prompt, my_role, agent_key="qa")
            
            log_action(f"QA IMPLEMENTATION COMPLETED (TODO #{t['id']})", phase="IMPLEMENTATION")
            update_todo(t["id"], status="done", result=final_result)
            generate_report(f"ดำเนินการตรวจสอบคุณภาพสำเร็จ:\n{final_result}")
            
            print("\n✅ [AUTO] งานเสร็จสิ้น — ส่งคืนรายงานคุณภาพให้ผู้บริหาร")
            return
            
        if input("  ➕ เพิ่มเข้าแผนการดำเนินการ (TODO)? [Y/N]: ").strip().upper() in ("Y",""):
            t=add_todo(initial_message); print(f"  ✅ เพิ่มแผนงานสำเร็จ #{t['id']}")
            
            # 📝 DEEP LOG: บันทึกการรับงานตรวจสอบคุณภาพ
            # --- Auto-execution log ---
            log_action(f"ดำเนินการตามแผนงาน TODO #{t['id']}", phase="IMPLEMENTATION")
            generate_report(f"เริ่มดำเนินการ: {initial_message}\nสร้างแผนงาน (TODO) #{t['id']}")
    while True:
        print("\n"+"-"*50)
        try: cmd = input("  ✅ QA > ").strip().lower()
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
