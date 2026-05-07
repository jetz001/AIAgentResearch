"""
============================================================
  👥 HR Agent — ทรัพยากรบุคคล
  เรียกจาก main.py หรือรันตรง:
    python Scripts/agent_hr.py "ข้อความงาน"
============================================================
"""
import os, sys, io, json
from datetime import datetime

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLE_FILE = os.path.join(PROJECT_ROOT, "Agent", "06_HR.md")
TODO_DIR = os.path.join(PROJECT_ROOT, "Workspace", "Decision", "hr_tasks")
MEETINGS_DIR = os.path.join(PROJECT_ROOT, "Meetings")
SCHEDULES_DIR = os.path.join(PROJECT_ROOT, "Meetings", "schedules")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "Output", "reports")
RISK_REGISTER = os.path.join(PROJECT_ROOT, "Workspace", "Decision", "risk_register.md")
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")

for d in [TODO_DIR, MEETINGS_DIR, SCHEDULES_DIR, REPORTS_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Role ──
def load_my_role() -> str:
    if os.path.exists(ROLE_FILE):
        with open(ROLE_FILE, "r", encoding="utf-8") as f: return f.read()
    return "(ไม่พบ role file)"

def get_my_skills() -> list[str]:
    return [l.strip().replace("### ","") for l in load_my_role().split("\n") if l.strip().startswith("### SK-")]

# ── TODO ──
def _fp(): return os.path.join(TODO_DIR, "hr_todo.json")
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
    "1": ("SK-HR-01","Timeline & Milestone","จัดการกำหนดการและ milestone"),
    "2": ("SK-HR-02","Meeting Coordination","นัดหมายและเตรียมการประชุม"),
    "3": ("SK-HR-03","Progress Tracking","จัดทำรายงานความคืบหน้ารายสัปดาห์"),
    "4": ("SK-HR-04","Resource Allocation","ติดตามและจัดการภาระงาน"),
    "5": ("SK-HR-05","Risk Management","ดูแล Risk Register ประเมินความเสี่ยง"),
}

def run_skill(num):
    if num not in SKILL_MENU: print("  ❌ เลขไม่ถูกต้อง"); return
    sid, name, desc = SKILL_MENU[num]
    print(f"\n  👥 เริ่มงาน: {name}\n     {desc}\n     Skill: {sid}")
    print("-"*50)

    detail = ""
    output_file = ""

    if num == "1":
        # Timeline
        phase = input("  📅 Phase ที่ติดตาม: ").strip()
        deadline = input("  ⏳ Deadline (YYYY-MM-DD): ").strip()
        status = input("  📊 สถานะปัจจุบัน (On-track/Delayed): ").strip()
        detail = f"Update Timeline: {phase} (Due: {deadline}, {status})"
        
    elif num == "2":
        # Meeting
        topic = input("  💬 หัวข้อประชุม: ").strip()
        with_who = input("  👥 ประชุมกับใคร (เช่น Advisor): ").strip()
        date = input("  📅 วันที่/เวลา: ").strip()
        detail = f"นัดประชุม {with_who} เรื่อง {topic} ({date})"
        output_file = os.path.join(SCHEDULES_DIR, f"meeting_{datetime.now():%Y%m%d}.md")
        
    elif num == "3":
        # Progress Report
        week = input("  📆 สัปดาห์ที่ (เช่น W05): ").strip()
        done = input("  ✅ งานที่สำเร็จ: ").strip()
        doing = input("  🔄 งานที่กำลังทำ: ").strip()
        blocker = input("  ⚠️ ปัญหา/อุปสรรค: ").strip()
        detail = f"จัดทำ Weekly Report {week}"
        report_name = f"weekly_{week}.md"
        output_file = os.path.join(REPORTS_DIR, report_name)
        
        # ถาม save report
        if input("\n  💾 บันทึก report? [Y/N]: ").strip().upper() in ("Y", ""):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"📊 Weekly Progress Report: {week}\n")
                f.write(f"📅 Date: {datetime.now():%Y-%m-%d}\n\n")
                f.write(f"✅ สำเร็จ: {done}\n")
                f.write(f"🔄 กำลังทำ: {doing}\n")
                f.write(f"⚠️ ปัญหา: {blocker}\n")
            print(f"  💾 บันทึกที่ {output_file}")
            
    elif num == "4":
        # Resource
        detail = input("  ⚖️ เรื่องการจัดการงาน: ").strip()
        if not detail: detail = "Resource Allocation Check"
        
    elif num == "5":
        # Risk Management
        risk = input("  ⚠️ ความเสี่ยงใหม่: ").strip()
        impact = input("  💥 ผลกระทบ (สูง/กลาง/ต่ำ): ").strip()
        mitigation = input("  🛡️ แผนรับมือ: ").strip()
        detail = f"อัปเดต Risk: {risk} ({impact})"
        
        if input("\n  💾 บันทึกตาราง Risk? [Y/N]: ").strip().upper() in ("Y", ""):
            # Append to risk register
            if not os.path.exists(RISK_REGISTER):
                with open(RISK_REGISTER, "w", encoding="utf-8") as f:
                    f.write("# ⚠️ Risk Register\n\n| Date | Risk | Impact | Mitigation |\n|------|------|--------|------------|\n")
            with open(RISK_REGISTER, "a", encoding="utf-8") as f:
                f.write(f"| {datetime.now():%Y-%m-%d} | {risk} | {impact} | {mitigation} |\n")
            output_file = RISK_REGISTER
            print(f"  💾 บันทึกที่ {output_file}")

    if not detail: detail = f"{name}: {desc}"
    
    todo = add_todo(detail, sid)
    print(f"  ✅ สร้าง TODO #{todo['id']}: {detail}")

    start = input("  ▶️ เริ่มทำ/บันทึกผลเลย? [Y/N]: ").strip().upper()
    if start in ("Y",""):
        update_todo(todo["id"], status="in_progress")
        print(f"\n  🔄 กำลังทำ: {detail}")
        print("  ─────────────────────────────────")
        result = input("  📄 ผลลัพธ์สรุป: ").strip()
        if not output_file:
            output_file = input("  📂 Output file path (Enter=ไม่มี): ").strip()
        
        update_todo(todo["id"], status="done",
                    result=result or "(ไม่ได้บันทึก)", output_file=output_file)
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
    print("  👨‍💼 ผู้บริหาร — Review งาน HR Agent")
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
            note = input("  📝 สิ่งที่ต้องแก้/ปรับปรุง: ").strip()
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
    with open(os.path.join(LOGS_DIR,"hr_agent.log"),"a",encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [HR] {action}\n")

# ── UI ──
def print_banner():
    print("\n"+"="*60)
    print("  👥 HR AGENT — ทรัพยากรบุคคล (ติดตามและจัดการทีม)")
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
    print("  │        📋 HR Agent Menu                  │")
    print("  ├─────┬───────────────────────────────────┤")
    print("  │  1  │ 📅 Timeline & Milestone           │")
    print("  │  2  │ 🤝 Meeting Coordination           │")
    print("  │  3  │ 📊 Progress Tracking              │")
    print("  │  4  │ ⚖️ Resource Allocation             │")
    print("  │  5  │ ⚠️ Risk Management                │")
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
        print(f"\n  📨 งานจากผู้บริหาร: \"{initial_message[:80]}\"")
        if input("  ➕ เพิ่มเป็น TODO? [Y/N]: ").strip().upper() in ("Y",""):
            t=add_todo(initial_message); print(f"  ✅ TODO #{t['id']}")
            log_action(f"รับงาน: {initial_message[:50]}")
    while True:
        print("\n"+"-"*50)
        try: cmd = input("  👥 HR > ").strip().lower()
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
