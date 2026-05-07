"""
============================================================
  📰 EDITOR AGENT — ผู้เชี่ยวชาญการตีพิมพ์
  เรียกจาก main.py หรือรันตรง:
    python Scripts/agent_editor.py "ข้อความงาน"
============================================================
"""
import os, sys, io, json
from datetime import datetime
import llm_helper

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLE_FILE = os.path.join(PROJECT_ROOT, "Agent", "04_Editor.md")
TODO_DIR = os.path.join(PROJECT_ROOT, "Workspace", "Decision", "editor_tasks")
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, "Workspace", "Decision")
FEEDBACK_DIR = os.path.join(PROJECT_ROOT, "Meetings", "feedback")
PUBS_DIR = os.path.join(PROJECT_ROOT, "Output", "publications")
SUBMISSION_DIR = os.path.join(PUBS_DIR, "submission_package")
LOGS_DIR = os.path.join(PROJECT_ROOT, "Logs")

for d in [TODO_DIR, WORKSPACE_DIR, FEEDBACK_DIR, PUBS_DIR, SUBMISSION_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Roleplay UI Helpers ──
def print_box(title, content, color_code="32"): # Default Green for Editor
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
def _fp(): return os.path.join(TODO_DIR, "editor_todo.json")
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
    "1": ("SK-EDT-01","Journal Targeting","ค้นหาและเปรียบเทียบวารสารเป้าหมาย"),
    "2": ("SK-EDT-02","Publishability Assessment","ประเมินโอกาสตีพิมพ์ (ปรึกษา Advisor)"),
    "3": ("SK-EDT-03","Peer Review Simulation","จำลองการเป็น Reviewer โหดๆ"),
    "4": ("SK-EDT-04","Submission Strategy","วางกลยุทธ์, ร่าง Cover Letter/Highlights"),
    "5": ("SK-EDT-05","Response to Reviewers","ช่วยร่างจดหมายตอบกลับ Reviewer"),
}

def run_skill(num):
    if num not in SKILL_MENU: print("  ❌ เลขไม่ถูกต้อง"); return
    sid, name, desc = SKILL_MENU[num]
    print(f"\n  📰 เริ่มงาน: {name}\n     {desc}\n     Skill: {sid}")
    print("-"*50)

    detail = ""
    output_file = ""

    if num == "1":
        # Journal Targeting
        topic = input("  🔍 หัวข้อวิจัยคร่าวๆ: ").strip()
        detail = f"ค้นหาวารสารสำหรับหัวข้อ: {topic}"
        j1 = input("  🎯 วารสารที่แนะนำ (1): ").strip()
        j2 = input("  🎯 วารสารที่แนะนำ (2): ").strip()
        output_file = os.path.join(WORKSPACE_DIR, f"target_journals_{datetime.now():%Y%m%d}.md")
        if input("\n  💾 บันทึกตารางเปรียบเทียบวารสาร? [Y/N]: ").strip().upper() in ("Y", ""):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Target Journals for: {topic}\n\n")
                f.write(f"1. **{j1}**\n2. **{j2}**\n")
            print(f"  💾 บันทึกที่ {output_file}")
        else: output_file = ""

    elif num == "2":
        # Publishability Assessment
        manuscript = input("  📄 ร่างงานที่นำมาประเมิน: ").strip()
        detail = f"ประเมินโอกาสตีพิมพ์ของ {manuscript}"
        print("\n  ⚠️ คำเตือนจาก Editor: การตัดสินใจสุดท้ายอยู่ที่ Advisor")
        novelty = input("  💡 Novelty (สูง/กลาง/ต่ำ): ").strip()
        readiness = input("  📊 ความพร้อมของข้อมูล (%): ").strip()
        verdict = input("  ⚖️ สรุปความเห็นของ Editor (ตีพิมพ์ได้เลย/ต้องแก้ก่อน): ").strip()
        
        output_file = os.path.join(WORKSPACE_DIR, f"publishability_assessment_{datetime.now():%Y%m%d}.md")
        if input("\n  💾 บันทึกเพื่อส่งปรึกษา Advisor? [Y/N]: ").strip().upper() in ("Y", ""):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Publishability Assessment\n- **Target:** {manuscript}\n- **Novelty:** {novelty}\n- **Readiness:** {readiness}%\n- **Editor's Verdict:** {verdict}\n\n*รอการตัดสินใจจาก Advisor Agent*\n")
            print(f"  💾 บันทึกที่ {output_file}")
        else: output_file = ""

    elif num == "3":
        # Peer Review Simulation
        target = input("  📄 บทหรือส่วนไหนที่จะ Mock Review: ").strip()
        detail = f"Simulated Peer Review: {target}"
        print("\n  👹 สวมบท Reviewer โหดๆ:")
        q1 = input("  ❓ คำถามแทงใจดำที่ 1: ").strip()
        q2 = input("  ❓ คำถามแทงใจดำที่ 2: ").strip()
        output_file = os.path.join(FEEDBACK_DIR, f"simulated_peer_review_{datetime.now():%Y%m%d}.md")
        if input("\n  💾 บันทึกคำถามให้ Writer/Research ไปคิดต่อ? [Y/N]: ").strip().upper() in ("Y", ""):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Simulated Peer Review\n- **Target:** {target}\n\n### Hard Questions:\n1. {q1}\n2. {q2}\n")
            print(f"  💾 บันทึกที่ {output_file}")
        else: output_file = ""

    elif num == "4":
        # Submission Strategy
        journal = input("  🎯 Target Journal: ").strip()
        detail = f"เตรียม Strategy & Package สำหรับ {journal}"
        print("\n  กลยุทธ์การนำเสนอ:")
        hl1 = input("  🌟 Highlight 1: ").strip()
        hl2 = input("  🌟 Highlight 2: ").strip()
        output_file = os.path.join(SUBMISSION_DIR, f"cover_letter_draft_{datetime.now():%Y%m%d}.md")
        if input("\n  💾 ร่าง Cover Letter & Highlights? [Y/N]: ").strip().upper() in ("Y", ""):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Submission Package for {journal}\n\n## Highlights\n- {hl1}\n- {hl2}\n\n## Draft Cover Letter\nDear Editor of {journal}...\n")
            print(f"  💾 บันทึกที่ {output_file}")
        else: output_file = ""

    elif num == "5":
        # Response to Reviewers
        rev_count = input("  💬 มี Reviewer กี่คน: ").strip()
        detail = f"ร่างจดหมายตอบกลับ Reviewers ({rev_count} คน)"
        tone = input("  🎭 Tone การตอบ (เช่น อ่อนน้อม, หนักแน่นในวิชาการ): ").strip()
        output_file = os.path.join(PUBS_DIR, f"response_to_reviewers_{datetime.now():%Y%m%d}.md")
        if input("\n  💾 บันทึก Draft Response? [Y/N]: ").strip().upper() in ("Y", ""):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Response to Reviewers\n- **Tone:** {tone}\n\nDear Reviewers,\nThank you for your valuable feedback...\n")
            print(f"  💾 บันทึกที่ {output_file}")
        else: output_file = ""

    if not detail: detail = f"{name}: {desc}"
    
    todo = add_todo(detail, sid)
    print(f"  ✅ สร้าง TODO #{todo['id']}: {detail}")

    start = input("  ▶️ เริ่มทำ/บันทึกผลเลย? [Y/N]: ").strip().upper()
    if start in ("Y",""):
        update_todo(todo["id"], status="in_progress")
        print(f"\n  🔄 กำลังทำ: {detail}")
        result = input("  📄 ผลลัพธ์สรุป: ").strip()
        if not output_file:
            output_file = input("  📂 Output file path (Enter=ไม่มี): ").strip()
        
        update_todo(todo["id"], status="done",
                    result=result or "(ไม่ได้บันทึก)", output_file=output_file)
        print(f"  ✅ TODO #{todo['id']} เสร็จ!")
        
        # Editor ส่งให้ Orchestrator ทราบ แต่ถ้าเป็น SK-EDT-02 ควรเตือนว่าต้องปรึกษา Advisor
        if num == "2":
            print("\n  ⚠️ งานประเมินนี้ กรุณาส่งให้ Advisor Agent อนุมัติชี้ขาดอีกที")
            
        if input("  📤 Submit แจ้งผู้บริหาร? [Y/N]: ").strip().upper() in ("Y",""):
            update_todo(todo["id"], status="submitted")
            print(f"  📤 ส่งแจ้งเพื่อทราบแล้ว (Editor สั่งอนุมัติไม่ได้)")

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
    print("  👨‍💼 ผู้บริหาร — Review งาน Editor Agent (ฝั่งตีพิมพ์)")
    print("  ⚠️ ผู้บริหาร: โปรดจำไว้ว่า Editor ให้แค่ 'คำปรึกษา' ตัดสินใจจริงต้องถาม Advisor")
    print("="*60)
    for t in submitted:
        print(f"\n  ─── TODO #{t['id']} ───")
        print(f"  📝 {t['description']}")
        print(f"  📄 ผล: {t['result']}")
        if t["output_file"]: print(f"  📂 File: {t['output_file']}")
        print("  [A] Acknowledge (รับทราบ)  [R] Revision (ให้ปรับกลยุทธ์)  [S] Skip")
        d = input("  ผู้บริหาร > ").strip().upper()
        if d=="A":
            update_todo(t["id"], status="accepted", review="accepted")
            print(f"  ✅ #{t['id']} ACKNOWLEDGED (รับทราบคำแนะนำแล้ว)")
        elif d=="R":
            note = input("  📝 สิ่งที่ต้องปรับกลยุทธ์: ").strip()
            update_todo(t["id"], status="in_progress", review="revision_needed", review_note=note)
            print(f"  🔁 #{t['id']} ตีกลับให้คิดกลยุทธ์ใหม่")
        else:
            print(f"  ⏭️ ข้าม #{t['id']}")
    print("\n  📊 สรุป:"); show_todo()

def handle_revisions():
    todos = load_todo()
    revs = [t for t in todos if t["review"]=="revision_needed" and t["status"]=="in_progress"]
    if not revs: print("\n  ✅ ไม่มีงานตีกลับ"); return
    for t in revs:
        print(f"\n  ─── #{t['id']} ───")
        print(f"  📝 {t['description']}\n  📄 ผลเดิม: {t['result']}\n  💬 เหตุผล (ผู้บริหารสั่งปรับ): {t['review_note']}")
        if input("  ▶️ ปรับกลยุทธ์? [Y/N]: ").strip().upper() in ("Y",""):
            nr = input("  📄 กลยุทธ์ใหม่: ").strip()
            update_todo(t["id"], result=nr or t["result"], status="done", review="", review_note="")
            print(f"  ✅ ปรับ #{t['id']} แล้ว — พร้อม submit")

def log_action(action):
    with open(os.path.join(LOGS_DIR,"editor_agent.log"),"a",encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [Editor] {action}\n")

# ── UI ──
def print_banner():
    print("\n"+"="*60)
    print("  📰 EDITOR AGENT — ที่ปรึกษาฝั่งการตีพิมพ์วารสาร")
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
    if todos: print(f"\n  📊 ⬜{p} รอ | 🔄{ip} ทำ | 📤{sb} แจ้งเพื่อทราบ | 🔁{rv} ปรับกลยุทธ์")
    print()

def print_menu():
    print("  ┌─────────────────────────────────────────┐")
    print("  │        📋 Editor Agent Menu              │")
    print("  ├─────┬───────────────────────────────────┤")
    print("  │  1  │ 🎯 Journal Targeting              │")
    print("  │  2  │ ⚖️ Publishability Assessment      │")
    print("  │  3  │ 👹 Peer Review Simulation         │")
    print("  │  4  │ 📦 Submission Strategy            │")
    print("  │  5  │ 💬 Response to Reviewers          │")
    print("  ├─────┼───────────────────────────────────┤")
    print("  │todo │ 📋 ดู TODO list                    │")
    print("  │sub  │ 📤 Submit แจ้งผู้บริหาร            │")
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
        roleplay_msg = llm_helper.get_roleplay_response("Editor Agent", initial_message, my_role, agent_key="editor")
        
        print_box("🎭 ROLEPLAY: 📰 Editor Agent", roleplay_msg, "32")
        
        print(f"\n  📨 งานจากผู้บริหาร: \"{initial_message[:80]}\"")
        if input("  ➕ เพิ่มเป็น TODO? [Y/N]: ").strip().upper() in ("Y",""):
            t=add_todo(initial_message); print(f"  ✅ TODO #{t['id']}")
            log_action(f"รับงาน: {initial_message[:50]}")
    while True:
        print("\n"+"-"*50)
        try: cmd = input("  📰 Editor > ").strip().lower()
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
