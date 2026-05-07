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
    if not todos: print("\n  📭 ไม่มี TODO"); return
    print("\n  ┌─────┬──────────────────────────────────┬──────────┬────────┐")
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

def log_action(action):
    with open(os.path.join(LOGS_DIR,"writer_agent.log"),"a",encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [Writer] {action}\n")

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
    print("  │todo │ 📋 ดู TODO list                    │")
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
        roleplay_msg = llm_helper.get_roleplay_response("Writer Agent", initial_message, my_role, agent_key="writer")
        
        print_box("🎭 ROLEPLAY: ✍️ Writer Agent", roleplay_msg, "35")
        
        print(f"\n  📨 งานจากผู้บริหาร: \"{initial_message[:80]}\"")
        if input("  ➕ เพิ่มเป็น TODO? [Y/N]: ").strip().upper() in ("Y",""):
            t=add_todo(initial_message); print(f"  ✅ TODO #{t['id']}")
            log_action(f"รับงาน: {initial_message[:50]}")
    while True:
        print("\n"+"-"*50)
        try: cmd = input("  ✍️ Writer > ").strip().lower()
        except: print("\n  🔙 กลับ"); break
        if not cmd: continue
        if cmd in ("back","quit"): print("  🔙 กลับ main"); break
        if cmd=="menu": print_menu(); continue
        if cmd=="todo": show_todo(); continue
        if cmd in ("sub","submit"): submit_to_orchestrator(); continue
        if cmd in ("rev","revision"): handle_revisions(); continue
        if cmd=="role": print("\n"+load_my_role()); continue
        if cmd=="review": orchestrator_review(); continue
        if cmd in SKILL_MENU: run_skill(cmd); log_action(f"Skill: {SKILL_MENU[cmd][1]}"); continue
        print(f"  ➕ ไม่พบ '{cmd}' — เพิ่มเป็น TODO?")
        if input("  [Y/N]: ").strip().upper() in ("Y",""): 
            t=add_todo(cmd); print(f"  ✅ TODO #{t['id']}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "")
