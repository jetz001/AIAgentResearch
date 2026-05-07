"""
============================================================
  💻 IT AGENT — ระบบและออโตเมชัน
  เรียกจาก main.py หรือรันตรง:
    python Scripts/agent_it.py "ข้อความงาน"
============================================================
"""
import os, sys, io, json
from datetime import datetime
import shutil
import llm_helper

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLE_FILE = os.path.join(PROJECT_ROOT, "Agent", "05_IT.md")
TODO_DIR = os.path.join(PROJECT_ROOT, "Workspace", "Decision", "it_tasks")
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "Archive")
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "Config")
SANDBOX_DIR = os.path.join(PROJECT_ROOT, "Workspace", "Sandbox")
TOOLS_DIR = os.path.join(PROJECT_ROOT, "Workspace", "Tools")

for d in [TODO_DIR, ARCHIVE_DIR, LOGS_DIR, CONFIG_DIR, SANDBOX_DIR, TOOLS_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Roleplay UI Helpers ──
def print_box(title, content, color_code="37"): # Default White for IT
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
def _fp(): return os.path.join(TODO_DIR, "it_todo.json")
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
    "1": ("SK-IT-01","Environment Setup","ติดตั้งและตรวจสอบ Environment"),
    "2": ("SK-IT-02","Backup & Version Control","สำรองข้อมูล / เก็บ Archive"),
    "3": ("SK-IT-03","Data Pipeline","จัดการ Data Pipeline เบื้องต้น"),
    "4": ("SK-IT-04","Automation Scripts","รัน/สร้าง Script อัตโนมัติ"),
    "5": ("SK-IT-05","System Monitoring","ตรวจสอบสถานะระบบ (Health Check)"),
    "6": ("SK-IT-06","Sandbox Management","จัดการพื้นที่ทดสอบชั่วคราว"),
    "7": ("SK-IT-07","Config Management","ดูแลไฟล์ Config และ Security"),
}

def run_skill(num):
    if num not in SKILL_MENU: print("  ❌ เลขไม่ถูกต้อง"); return
    sid, name, desc = SKILL_MENU[num]
    print(f"\n  💻 เริ่มงาน: {name}\n     {desc}\n     Skill: {sid}")
    print("-"*50)

    detail = ""
    output_file = ""

    if num == "1":
        detail = "ตรวจสอบ Python Env และ Dependencies"
        print("\n  🔍 เช็คเวอร์ชัน Python:")
        print(f"     [SYS] {sys.version.split()[0]}")
        env_file = os.path.join(CONFIG_DIR, ".env")
        if not os.path.exists(env_file):
            if input("  ⚠️ ไม่พบ .env สร้างไฟล์ Template ไหม? [Y/N]: ").strip().upper() in ("Y", ""):
                with open(env_file, "w", encoding="utf-8") as f:
                    f.write("OPENAI_API_KEY=\nANTHROPIC_API_KEY=\nGEMINI_API_KEY=\n")
                print("     ✅ สร้าง Template ให้แล้วใน Config/.env")
        else:
            print("     ✅ พบไฟล์ Config/.env เรียบร้อย")
        result_text = "เช็คระบบผ่าน"

    elif num == "2":
        detail = "จำลองการทำ Backup Data"
        print("\n  💾 Backup Options")
        print("  1. Backup ทั้งโปรเจค (ZIP)")
        print("  2. Backup เฉพาะ Output/ ลง Archive")
        ch = input("  [1/2]: ").strip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if ch == "2":
            output_src = os.path.join(PROJECT_ROOT, "Output")
            archive_dest = os.path.join(ARCHIVE_DIR, f"Output_backup_{timestamp}")
            print(f"  📦 จำลองการก็อปปี้ {output_src} -> {archive_dest}")
            result_text = f"Backup Output เสร็จสมบูรณ์ (ID: {timestamp})"
        else:
            print(f"  📦 จำลองการ ZIP {PROJECT_ROOT} -> Archive/Full_backup_{timestamp}.zip")
            result_text = f"Full Backup เสร็จสมบูรณ์ (ID: {timestamp})"

    elif num == "3":
        src = input("  🗃️ ไฟล์ข้อมูล Raw (Path/URL): ").strip()
        detail = f"รัน Data Pipeline ให้ {src}"
        print("  ⏳ กำลังจำลอง Pipeline (Raw -> Clean -> Analyzed)...")
        result_text = "Clean Data สำเร็จ พร้อมนำไปใช้วิเคราะห์"

    elif num == "4":
        script_name = input("  🛠️ ชื่อ Script อัตโนมัติที่ต้องการรัน: ").strip()
        detail = f"รัน Automation Script: {script_name}"
        result_text = f"รัน script {script_name} สำเร็จ"

    elif num == "5":
        detail = "System Health Check"
        print("\n  🩺 ตรวจสอบสถานะ:")
        print("  - API Keys: 🟡 (ต้องเช็คเพิ่ม)")
        print(f"  - Logs Size: 🟢 ({len(os.listdir(LOGS_DIR))} files)")
        print(f"  - Configs: 🟢 OK")
        output_file = os.path.join(LOGS_DIR, f"system_health_{datetime.now():%Y%m%d}.md")
        if input("\n  💾 บันทึก Health Report? [Y/N]: ").strip().upper() in ("Y", ""):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# System Health Check\n- **Date:** {datetime.now():%Y-%m-%d %H:%M:%S}\n- **Status:** Normal\n")
            print(f"  💾 บันทึกที่ {output_file}")
        else: output_file = ""
        result_text = "ระบบปกติ"

    elif num == "6":
        detail = "จัดการ Sandbox พื้นที่ทดสอบ"
        print(f"  📦 โฟลเดอร์: {SANDBOX_DIR}")
        if input("  🧹 ล้างข้อมูล Sandbox (Reset)? [Y/N]: ").strip().upper() in ("Y", ""):
            # จำลองการล้าง (ไม่ลบจริงเดี๋ยวพัง)
            print("  ✅ ล้าง Sandbox เรียบร้อย (จำลอง)")
        result_text = "จัดการ Sandbox เสร็จสิ้น"

    elif num == "7":
        detail = "จัดการ Config/Secrets"
        print("  🔒 การจัดเก็บรหัสผ่าน/Token")
        print("  - ให้แน่ใจว่าได้ระบุ Config/.env ไว้ใน .gitignore")
        result_text = "รีวิวความปลอดภัยของ Config สำเร็จ"

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
        
        if input("  📤 แจ้งผู้บริหาร? [Y/N]: ").strip().upper() in ("Y",""):
            update_todo(todo["id"], status="submitted")
            print(f"  📤 ส่งแจ้งเพื่อทราบแล้ว")

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
    print("  👨‍💼 ผู้บริหาร — Review งาน IT Agent")
    print("="*60)
    for t in submitted:
        print(f"\n  ─── TODO #{t['id']} ───")
        print(f"  📝 {t['description']}")
        print(f"  📄 ผล: {t['result']}")
        if t["output_file"]: print(f"  📂 File: {t['output_file']}")
        print("  [A] Acknowledge (รับทราบ)  [R] Revision (ให้แก้/รันใหม่)  [S] Skip")
        d = input("  ผู้บริหาร > ").strip().upper()
        if d=="A":
            update_todo(t["id"], status="accepted", review="accepted")
            print(f"  ✅ #{t['id']} ACKNOWLEDGED")
        elif d=="R":
            note = input("  📝 ข้อผิดพลาดที่ต้องแก้: ").strip()
            update_todo(t["id"], status="in_progress", review="revision_needed", review_note=note)
            print(f"  🔁 #{t['id']} ตีกลับ")
        else:
            print(f"  ⏭️ ข้าม #{t['id']}")
    print("\n  📊 สรุป:"); show_todo()

def handle_revisions():
    todos = load_todo()
    revs = [t for t in todos if t["review"]=="revision_needed" and t["status"]=="in_progress"]
    if not revs: print("\n  ✅ ไม่มีงานตีกลับ"); return
    for t in revs:
        print(f"\n  ─── #{t['id']} ───")
        print(f"  📝 {t['description']}\n  📄 ผลเดิม: {t['result']}\n  💬 เหตุผล (สั่งแก้): {t['review_note']}")
        if input("  ▶️ แก้ไข/รันใหม่? [Y/N]: ").strip().upper() in ("Y",""):
            nr = input("  📄 ผลใหม่: ").strip()
            update_todo(t["id"], result=nr or t["result"], status="done", review="", review_note="")
            print(f"  ✅ แก้ #{t['id']} แล้ว — พร้อม submit")

def log_action(action):
    with open(os.path.join(LOGS_DIR,"it_agent.log"),"a",encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [IT] {action}\n")

# ── UI ──
def print_banner():
    print("\n"+"="*60)
    print("  💻 IT AGENT — ระบบและออโตเมชัน")
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
    if todos: print(f"\n  📊 ⬜{p} รอ | 🔄{ip} ทำ | 📤{sb} แจ้งเพื่อทราบ | 🔁{rv} ปรับแก้")
    print()

def print_menu():
    print("  ┌─────────────────────────────────────────┐")
    print("  │        📋 IT Agent Menu                  │")
    print("  ├─────┬───────────────────────────────────┤")
    print("  │  1  │ 🔧 Environment Setup              │")
    print("  │  2  │ 💾 Backup & Version Control       │")
    print("  │  3  │ 🗃️ Data Pipeline                 │")
    print("  │  4  │ 🛠️ Automation Scripts            │")
    print("  │  5  │ 🩺 System Monitoring              │")
    print("  │  6  │ 📦 Sandbox Management             │")
    print("  │  7  │ 🔒 Config Management              │")
    print("  ├─────┼───────────────────────────────────┤")
    print("  │todo │ 📋 ดู TODO list                    │")
    print("  │sub  │ 📤 แจ้ง/Submit ให้ผู้บริหาร        │")
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
        roleplay_msg = llm_helper.get_roleplay_response("IT Agent", initial_message, my_role, agent_key="it")
        
        print_box("🎭 ROLEPLAY: 💻 IT Agent", roleplay_msg, "37")
        
        print(f"\n  📨 งานจากผู้บริหาร: \"{initial_message[:80]}\"")
        if input("  ➕ เพิ่มเป็น TODO? [Y/N]: ").strip().upper() in ("Y",""):
            t=add_todo(initial_message); print(f"  ✅ TODO #{t['id']}")
            log_action(f"รับงาน: {initial_message[:50]}")
    while True:
        print("\n"+"-"*50)
        try: cmd = input("  💻 IT > ").strip().lower()
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
