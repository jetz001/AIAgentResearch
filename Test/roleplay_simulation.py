import os
import sys
import io
import time
from datetime import datetime

# Fix Windows encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Scripts"))

import main
from planner import analyze_and_plan, update_task_status

# --- UI Helpers ---
def print_box(title, content, color_code="36"): # Default Cyan
    print(f"\n\033[{color_code}m┌" + "─" * 68 + "┐")
    print(f"│ {title:<66} │")
    print("├" + "─" * 68 + "┤")
    for line in content.split('\n'):
        print(f"│ {line:<66} │")
    print("└" + "─" * 68 + "┘\033[0m")

def simulate_agent_working(agent_name, agent_display, action_text, response_content):
    print(f"\n\033[1;33m[SYSTEM] กระจายงานไปยัง {agent_display}...\033[0m")
    time.sleep(1)
    
    # Simulate thinking/working
    print(f"  {agent_display} กำลังประมวลผล...")
    time.sleep(1.5)
    
    # Roleplay Output
    color_map = {
        "research": "34", # Blue
        "writer": "32",   # Green
        "qa": "35",       # Magenta
        "it": "37",       # White
        "hr": "33",       # Yellow
        "editor": "36",   # Cyan
        "advisor": "31"    # Red
    }
    color = color_map.get(agent_name, "37")
    
    print_box(f"🎭 ROLEPLAY: {agent_display}", response_content, color)
    
    # Log the action
    main.log_action(f"[{agent_display}] {action_text}")
    # Update agent log
    agent_log = os.path.join(PROJECT_ROOT, "Logs", f"{agent_name}_agent.log")
    with open(agent_log, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [{agent_name.upper()}] {action_text}\n")

def run_roleplay_test():
    # Capture output
    output_capture = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = output_capture

    try:
        os.system("cls" if os.name == "nt" else "clear")
        print("\n" + "★" * 70)
        print("  🚀 GIGA-AGENT ROLEPLAY SIMULATION — ระบบสวมบทบาทเอเจ้นท์เต็มรูปแบบ")
        print("  เป้าหมาย: ค้นคว้าและเตรียมหัวข้อวิทยานิพนธ์ระดับ Enterprise")
        print("★" * 70)

        user_query = "หาเปเปอร์ Carbon Footprint ในโรงงานกล่อง แล้วร่างบทนำให้ที ตรวจความถูกต้องด้วย"
        print(f"\n\033[1;36m🔹 ผู้บริหาร (User): \"{user_query}\"\033[0m")
        time.sleep(1)

        # Step 1: Planning
        print("\n\033[1;37m[Orchestrator] วิเคราะห์ความต้องการและวางโครงสร้างงาน...\033[0m")
        plan = analyze_and_plan(user_query)
        time.sleep(1)
        
        # Roleplay as Orchestrator
        print_box("👔 ORCHESTRATOR", 
                  "คำสั่งนี้ต้องการการทำงานแบบ Pipeline: \n"
                  "1. Research ค้นหาข้อมูลเฉพาะทาง\n"
                  "2. Writer เรียบเรียงเนื้อหาบทนำ\n"
                  "3. QA ตรวจสอบคุณภาพงานเขียน\n"
                  "ผมอนุมัติแผนงานนี้ และจะเริ่มส่งต่อหน้าที่ทันทีครับ", "36")
        
        main.log_action(f"รับคำสั่ง: {user_query}")
        main.log_action("สร้างแผนงานและเริ่มสวมบทบาทการทำงาน")

        # Step 2: Research Roleplay
        simulate_agent_working(
            "research", "📚 Research Agent",
            "ค้นหาเปเปอร์ Carbon Footprint ในอุตสาหกรรมบรรจุภัณฑ์สำเร็จ",
            "สวัสดีครับ ผมกำลังเข้าถึงฐานข้อมูล Scopus และ ScienceDirect...\n"
            "พบเปเปอร์ที่เกี่ยวข้อง 5 ฉบับ เน้นเรื่อง MFCA และ Carbon Footprint\n"
            "ในโรงงานกล่องลูกฟูก ผมสรุปใจความสำคัญลงใน Workspace เรียบร้อยครับ\n"
            "Gaps ที่พบคือ การลดของเสียในช่วง Setup เครื่องจักรครับ"
        )

        # Step 3: Writer Roleplay
        simulate_agent_working(
            "writer", "✍️  Writer Agent",
            "ร่างบทนำ (Introduction) ตามข้อมูลวิจัย",
            "รับไม้ต่อครับ! ผมกำลังเรียบเรียงบทนำโดยเน้นปัญหาโลกร้อนและความสำคัญ\n"
            "ของอุตสาหกรรมกล่องกระดาษต่อระบบเศรษฐกิจหมุนเวียน...\n"
            "เขียนร่างบทที่ 1 เสร็จแล้วครับ มีความยาว 3 หน้ากระดาษ A4\n"
            "ภาษาทางการระดับวิชาการ พร้อมสำหรับการตรวจสอบครับ"
        )

        # Step 4: QA Roleplay
        simulate_agent_working(
            "qa", "✅ QA Agent",
            "ตรวจสอบความถูกต้องและเกณฑ์วิทยานิพนธ์",
            "ตรวจสอบเรียบร้อยครับ! \n"
            "- ตรวจสอบ Plagiarism: ผ่าน (12%)\n"
            "- ตรวจสอบการอ้างอิง: รูปแบบ APA 7th ถูกต้องทุกจุด\n"
            "- ตรวจสอบเนื้อหา: ครบถ้วนตามข้อมูลที่ Research หามา\n"
            "งานชิ้นนี้พร้อมส่งต่อให้ Advisor หรือ Editor แล้วครับ"
        )

        # Conclusion
        print("\n" + "★" * 70)
        print("  📊 สรุปผลการทำงาน: ภารกิจสำเร็จ 100%")
        print("  ประวัติการสวมบทบาททั้งหมดถูกบันทึกลง Logs เรียบร้อย")
        print("★" * 70)


    finally:
        # Restore stdout and get captured text
        sys.stdout = original_stdout
        captured_text = output_capture.getvalue()
        print(captured_text) # Still print to screen

        # Save output to file
        output_dir = os.path.join(PROJECT_ROOT, "Output")
        os.makedirs(output_dir, exist_ok=True)
        filename = f"roleplay_result_{datetime.now():%Y%m%d_%H%M%S}.txt"
        filepath = os.path.join(output_dir, filename)
        
        # Remove ANSI color codes for the text file
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        plain_text = ansi_escape.sub('', captured_text)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(plain_text)

        print(f"\n  💾 บันทึกประวัติการสวมบทบาทลงใน: {filepath}")

if __name__ == "__main__":
    run_roleplay_test()
