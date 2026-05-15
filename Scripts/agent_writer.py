"""
============================================================
  ✍️ Writer Agent — นักเขียน
  เรียกจาก main.py หรือรันตรง:
    python Scripts/agent_writer.py "ข้อความงาน"
============================================================
"""
import os, sys, io, json
from datetime import datetime
import llm_helper

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLE_FILE = os.path.join(PROJECT_ROOT, "Agent", "02_Writer.md")
TODO_DIR = os.path.join(PROJECT_ROOT, "Workspace", "Decision", "writer_tasks")
THESIS_DIR = os.path.join(PROJECT_ROOT, "Output", "thesis")
PUBS_DIR = os.path.join(PROJECT_ROOT, "Output", "publications")
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "Archive", "thesis_drafts")
REFS_DIR = os.path.join(PROJECT_ROOT, "References")
FEEDBACK_DIR = os.path.join(PROJECT_ROOT, "Meetings", "feedback")
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")

for d in [TODO_DIR, THESIS_DIR, PUBS_DIR, ARCHIVE_DIR, REFS_DIR, FEEDBACK_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Roleplay UI Helpers ──
def print_box(title, content, color_code="35"): # Default Magenta for Writer
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
def _fp(): return os.path.join(TODO_DIR, "writer_todo.json")
def load_todo() -> list[dict]:
    if os.path.exists(_fp()):
        with open(_fp(),"r",encoding="utf-8") as f: return json.load(f)
    return []
def save_todo(t): 
    with open(_fp(),"w",encoding="utf-8") as f: json.dump(t,f,ensure_ascii=False,indent=2)

def clean_description(msg):
    # กรณีรูปแบบใหม่
    if "คำสั่งจากผู้บริหาร (Orchestrator):" in msg:
        # ดึงบรรทัดถัดจากหัวข้อ
        lines = msg.split("คำสั่งจากผู้บริหาร (Orchestrator):")[-1].strip().split("\n")
        if lines:
            return lines[0].strip()
    
    # กรณีรูปแบบเก่า (เพื่อความยืดหยุ่น)
    if "--- งานที่ต้องทำ ---" in msg:
        return msg.split("--- งานที่ต้องทำ ---")[-1].strip()
        
    # ถ้าไม่เจอเลย เอา 50 ตัวแรก
    return (msg[:50].strip() + "...") if len(msg) > 50 else msg

def add_todo(desc, skill_id=""):
    todos = load_todo()
    t = {"id":len(todos)+1,"description":desc,"skill_id":skill_id,
         "status":"pending","thinking":"","result":"","output_file":"",
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

def read_shared_context():
    """[SK-WRT-06] อ่านข้อมูลวิจัยจาก Shared Context"""
    shared_file = os.path.join(PROJECT_ROOT, "Memory", "Shared", "Shared_Context.json")
    if os.path.exists(shared_file):
        try:
            with open(shared_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("research_findings", "")
        except Exception as e:
            print(f"  ⚠️ ไม่สามารถอ่าน Shared Context: {e}")
    return ""

# ── Skills ──
SKILL_MENU = {
    "1": ("SK-WRT-01","Thesis Outline","สร้างโครงร่างวิทยานิพนธ์"),
    "2": ("SK-WRT-02","Chapter Writing","เขียนเนื้อหาแต่ละบท"),
    "3": ("SK-WRT-03","Abstract Writing","เขียนบทคัดย่อ ไทย+EN"),
    "4": ("SK-WRT-04","Manuscript Drafting","เขียน manuscript สำหรับ journal"),
    "5": ("SK-WRT-05","Revision Handling","แก้ไขตาม feedback"),
    "6": ("SK-WRT-06","Citation Integration","ใส่ citation ในเนื้อหา"),
}

def run_skill(num):
    if num not in SKILL_MENU: print("  ❌ เลขไม่ถูกต้อง"); return
    sid, name, desc = SKILL_MENU[num]
    print(f"\n  ✍️ เริ่มงาน: {name}\n     {desc}\n     Skill: {sid}")
    print("-"*50)

    # ถามรายละเอียดเฉพาะ skill
    detail = ""
    if num == "1":
        print("  📝 โครงร่าง Thesis:")
        chapters = ["บทนำ","ทบทวนวรรณกรรม","วิธีการวิจัย","ผลการวิจัย","สรุป อภิปราย"]
        for i,ch in enumerate(chapters,1): print(f"     บทที่ {i}: {ch}")
        extra = input("  เพิ่มบทพิเศษ (Enter=ไม่): ").strip()
        detail = f"Thesis Outline ({len(chapters)} บท)" + (f" +{extra}" if extra else "")
    elif num == "2":
        ch = input("  เขียนบทที่ [1-5]: ").strip()
        section = input("  หัวข้อย่อย (Enter=ทั้งบท): ").strip()
        detail = f"เขียนบทที่ {ch}" + (f" - {section}" if section else "")
    elif num == "3":
        lang = input("  ภาษา [TH/EN/BOTH]: ").strip().upper()
        detail = f"เขียน Abstract ({lang if lang else 'BOTH'})"
    elif num == "4":
        journal = input("  Target Journal: ").strip()
        detail = f"Manuscript สำหรับ {journal if journal else '(ยังไม่ระบุ)'}"
    elif num == "5":
        source = input("  Feedback จากใคร (advisor/reviewer): ").strip()
        detail = f"แก้ไขตาม feedback {source}"
    elif num == "6":
        style = input("  Citation style [APA/IEEE/อื่น]: ").strip()
        detail = f"ใส่ citation ({style if style else 'APA 7th'})"

    if not detail: detail = f"{name}: {desc}"
    todo = add_todo(detail, sid)
    print(f"  ✅ สร้าง TODO #{todo['id']}: {detail}")

    start = input("  ▶️ เริ่มทำเลย? [Y/N]: ").strip().upper()
    if start in ("Y",""):
        update_todo(todo["id"], status="in_progress")
        print(f"\n  🔄 กำลังทำ: {detail}")
        print("  ─────────────────────────────────")
        result = input("  📄 ผลลัพธ์/สรุป: ").strip()
        outfile = input("  📂 Output file path (Enter=ไม่มี): ").strip()
        update_todo(todo["id"], status="done",
                    result=result or "(ไม่ได้บันทึก)", output_file=outfile)
        print(f"  ✅ TODO #{todo['id']} เสร็จ!")
        if input("  📤 Submit ให้ผู้บริหาร? [Y/N]: ").strip().upper() in ("Y",""):
            update_todo(todo["id"], status="submitted")
            print(f"  📤 ส่งแล้ว")

def generate_report(work_details: str):
    """สร้างรายงานสรุปผลการทำงาน"""
    my_role = load_my_role()
    print(f"\n  🧠 กำลังสรุปรายงาน (Reporting) เพื่อส่งผู้บริหาร...")
    report_content = llm_helper.get_report_response("Writer Agent", work_details, my_role, agent_key="writer")
    
    print_box("📄 REPORT: ✍️ Writer Agent", report_content, "35")
    
    # บันทึกลงไฟล์
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(PROJECT_ROOT, "Output", "reports")
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, f"writer_report_{timestamp}.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# 📊 Writer Report\n")
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
        sub = sum(1 for t in todos if t["status"]=="submitted")
        if sub: print(f"  📤 มี {sub} งานรอ review อยู่")
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
        else: print(f"  ❌ #{tid} ไม่อยู่ใน done")

def orchestrator_review():
    todos = load_todo()
    submitted = [t for t in todos if t["status"]=="submitted"]
    if not submitted: print("\n  📭 ไม่มีงานรอ review"); return
    print("\n"+"="*60)
    print("  👨‍💼 ผู้บริหาร — Review งาน Writer Agent")
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
            note = input("  📝 สิ่งที่ต้องแก้: ").strip()
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
    print("\n  🔁 งานที่ถูกตีกลับ:")
    for t in revs:
        print(f"\n  ─── #{t['id']} ───")
        print(f"  📝 {t['description']}\n  📄 ผลเดิม: {t['result']}\n  💬 เหตุผล: {t['review_note']}")
        if input("  ▶️ แก้ไข? [Y/N]: ").strip().upper() in ("Y",""):
            nr = input("  📄 ผลใหม่: ").strip()
            nf = input("  📂 File ใหม่ (Enter=เดิม): ").strip()
            update_todo(t["id"], result=nr or t["result"], output_file=nf or t["output_file"],
                        status="done", review="", review_note="")
            print(f"  ✅ แก้ #{t['id']} แล้ว — พร้อม submit")

def log_action(action, phase="IMPLEMENTATION"):
    with open(os.path.join(LOGS_DIR,"writer_agent.log"),"a",encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [Writer] [{phase}] {action}\n")

# ── UI ──
def print_banner():
    print("\n"+"="*60)
    print("  ✍️ WRITER AGENT — นักเขียน")
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
    print("  │        📋 Writer Agent Menu              │")
    print("  ├─────┬───────────────────────────────────┤")
    print("  │  1  │ 📝 Thesis Outline                 │")
    print("  │  2  │ ✍️ Chapter Writing                │")
    print("  │  3  │ 📄 Abstract Writing               │")
    print("  │  4  │ 📰 Manuscript Drafting            │")
    print("  │  5  │ 🔁 Revision Handling              │")
    print("  │  6  │ 📚 Citation Integration           │")
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
        # [SK-WRT-06] ดึงข้อมูลจาก Shared Context มาช่วยเขียน
        shared_info = read_shared_context()
        if shared_info:
            print(f"  🤝 [SK-WRT-06] พบข้อมูลวิจัยใน Shared Context — กำลังนำมาประมวลผล...")
            initial_message += f"\n\n[Shared Context from Research]:\n{shared_info}"

        # ดึง Role มาให้ LLM วิเคราะห์
        my_role = load_my_role()
        
        # ขอความเห็นจาก LLM (Ollama/Online)
        print(f"\n  🧠 กำลังติดต่อ LLM เพื่อเตรียมการตอบกลับ...")
        roleplay_msg = llm_helper.get_roleplay_response("Writer Agent", initial_message, my_role, agent_key="writer")
        
        print_box("🎭 ROLEPLAY: ✍️ Writer Agent", roleplay_msg, "35")
        
        # --- Thinking Phase ---
        print(f"\n  🧠 กำลังวิเคราะห์งาน (Thinking)...")
        thinking_msg = llm_helper.get_thinking_response("Writer Agent", initial_message, my_role, agent_key="writer")
        print_box("💭 THINKING: ✍️ Writer Agent", thinking_msg, "35")
        
        # 📝 DEEP LOG: บันทึกโครงสร้างความคิดเบื้องต้น
        log_action(f"WRITING STRATEGY:\n   💡 โจทย์: {initial_message}\n   🧠 แผนการเขียน: {thinking_msg[:500]}...", phase="THINKING")

        # --- Implementation Phase ---
        print(f"\n  " + "═"*20 + " 🛠️ Implementation Phase " + "═"*20)
        print(f"  📨 งานที่ได้รับจากผู้บริหาร: \"{initial_message[:80]}\"")
        
        # 🤖 AUTOMATED: ข้ามการถามถ้าอยู่ในโหมดอัตโนมัติ
        is_auto = os.getenv("AUTOMATED") == "1"
        if is_auto or input("  ➕ เพิ่มเข้าแผนการดำเนินการ (TODO)? [Y/N]: ").strip().upper() in ("Y",""):
            t=add_todo(clean_description(initial_message))
            # บันทึก Thinking ลงใน TODO
            update_todo(t["id"], thinking=thinking_msg)
            print(f"  ✅ เพิ่มแผนงานสำเร็จ #{t['id']}")
            
            # 📝 DEEP LOG: บันทึกการรับงานเขียน
            log_action(f"WRITING TASK START (TODO #{t['id']}):\n   📋 หัวข้อ: {initial_message}", phase="IMPLEMENTATION")
            
            # --- Reporting Phase ---
            work_details = f"งานที่ได้รับ: {initial_message}\n"
            work_details += f"การวิเคราะห์ (Thinking): {thinking_msg}\n"
            work_details += f"สถานะแผนงาน (Implementation): สร้าง TODO #{t['id']} เรียบร้อย"
            
            # --- Draft Generation Phase ---
            print(f"\n  ✍️ [SK-WRT-02] กำลังเขียนเนื้อหาตามคำสั่งของผู้บริหาร (Academic Style)...")
            
            # ตรวจสอบบทที่หรือภาคผนวก
            import re
            chapter_match = re.search(r'(?:บทที่|Chapter)\s*(\d+)', initial_message)
            appendix_match = re.search(r'ภาคผนวก', initial_message)
            
            if chapter_match:
                chapter_num = chapter_match.group(1)
            elif appendix_match:
                chapter_num = "Appendix"
            else:
                chapter_num = "1"
            
            draft_sys_prompt = f"""คุณคือผู้เชี่ยวชาญการเขียนวิทยานิพนธ์ระดับดุษฎีบัณฑิต (PhD) ที่เน้นความสละสลวยของภาษาไทย
กฎการทำงาน:
- ใช้ภาษาไทยระดับวิชาการสูงสุด (Academic Thai) เท่านั้น
- ห้ามมีภาษาอังกฤษปนในเนื้อหาเด็ดขาด (ห้ามมีภาษาอังกฤษในวงเล็บ)
- ใช้คำทับศัพท์ภาษาไทยที่ถูกต้อง (เช่น คาร์บอนฟุตพริ้นท์, ดิจิทัล, ฟล็กซ์โกราฟิก)
- อ้างอิงแหล่งที่มาเป็นภาษาไทยตามมาตรฐาน APA 7th
- ห้ามมีคำทักทาย หรือกระบวนการคิด เริ่มต้นที่เนื้อหาทันที
- หากมีการแทรกรูปภาพ ให้ใช้รูปแบบ ![ชื่อรูป](พาธรูปภาพ) ในตำแหน่งที่เหมาะสม"""
            
            draft_prompt = f"คำสั่งจากผู้บริหาร: {initial_message}\n\nกรุณาเขียนเนื้อหาให้สมบูรณ์แบบตามโครงสร้างวิทยานิพนธ์ไทย"
            actual_draft = llm_helper.call_llm(draft_prompt, draft_sys_prompt, agent_key="writer")
            
            # 📝 DEEP LOG: พรีวิวเนื้อหาที่ร่างสำเร็จ
            log_action(f"DRAFT COMPLETED (Chapter {chapter_num}):\n   ✍️ เนื้อหาบางส่วน: {actual_draft[:500]}...", phase="DRAFTING")
            
            # อัปเดตผลงานลง TODO ทันที (เพื่อให้ Orchestrator อ่านได้)
            update_todo(t["id"], status="done", result=actual_draft)
            work_details += f"\n✍️ ร่างเนื้อหาสำเร็จ (ความยาว {len(actual_draft)} ตัวอักษร)"

            # --- [IT TRIGGER] Word Generation ---
            if "Word" in initial_message or ".docx" in initial_message:
                print(f"  📂 [IT] กำลังสร้างไฟล์ Word จากเนื้อหาที่ร่างสำเร็จ...")
                
                # ตั้งชื่อไฟล์ให้ตรงกับบท
                safe_name = initial_message.split("บันทึกเป็น Word ชื่อไฟล์")[-1].strip().replace('"', '')
                if not safe_name.endswith(".docx"):
                    safe_name = f"Chapter{chapter_num}_Draft.docx"
                
                draft_file = os.path.join(THESIS_DIR, f"chapter{chapter_num}_draft.md")
                word_file = os.path.join(THESIS_DIR, safe_name)
                
                # เขียนร่างจริงลง md
                with open(draft_file, "w", encoding="utf-8") as f:
                    f.write(actual_draft)
                
                import subprocess
                gen_script = os.path.join(PROJECT_ROOT, "Scripts", "word_generator.py")
                python_exe = r"C:\Users\Boss-QA\AppData\Local\Programs\Python\Python312\python.exe"
                subprocess.run([python_exe, gen_script, draft_file, word_file])
                
                update_todo(t["id"], output_file=word_file)
                work_details += f"\n📂 สร้างไฟล์ Word สำเร็จ: {word_file}"
                log_action(f"FILE GENERATED: {word_file}", phase="EXPORT")

            generate_report(work_details)
            
            if is_auto:
                print("\n✅ [AUTO] งานเสร็จสิ้น — กำลังส่งคืนการควบคุมให้ผู้บริหาร...")
                return

    while True:
        print("\n"+"-"*50)
        try: cmd = input("  ✍️ Writer > ").strip().lower()
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
