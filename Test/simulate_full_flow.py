import os
import sys
import io

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Scripts"))

from planner import analyze_and_plan, approve_plan, get_approved_tasks, update_task_status, show_tracker
import main

# Mock dispatch_to_agent so it doesn't block waiting for input
def mock_dispatch(agent_name: str, message: str):
    print(f"\n  🚀 [MOCK] กำลังส่งงานไปยัง {agent_name}...")
    main.log_action(f"ส่งงานไปยัง {agent_name} สำเร็จ")
    # Simulate agent generating a log
    agent_log = os.path.join(PROJECT_ROOT, "Logs", f"{agent_name}_agent.log")
    from datetime import datetime
    with open(agent_log, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [{agent_name.upper()}] รับงาน: {message[:40]}\n")
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [{agent_name.upper()}] แจ้ง: ทำงานสำเร็จ\n")

main.dispatch_to_agent = mock_dispatch

def run_simulation():
    # Capture output
    output_capture = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = output_capture

    try:
        print("="*60)
        print("  🚀 เริ่มจำลองการทำงานเต็มรูปแบบ (End-to-End Simulation)")
        print("="*60)
        
        user_input = "รบกวนให้ HR นัดอาจารย์ให้หน่อย จะส่งบทคัดย่อที่เพิ่งจัดรูปแบบให้ QA ตรวจก่อนส่ง"
        print(f"\n🔹 ผู้บริหาร > {user_input}")
        
        main.log_action("--- เปิดระบบ Orchestrator ---")
        main.log_action(f"รับคำสั่งจาก user: {user_input[:50]}")
        
        plan = analyze_and_plan(user_input)
        
        print("\n  🧠 กำลังวิเคราะห์ข้อความ... สร้างแผนเสร็จสิ้น")
        plan["status"] = "approved"
        from planner import save_plan, show_plan
        save_plan(plan)
        show_plan(plan)
        
        main.log_action("อนุมัติแผนงานแล้ว เริ่มกระจายงาน")
        
        tasks = get_approved_tasks(plan)
        for task in tasks:
            agent = task["agent"]
            display = main.AGENT_DISPLAY.get(agent, agent)
            print(f"\n  ──── Task #{task['order']} ────")
            print(f"  👤 Agent: {display}")
            print(f"  ▶️  ส่งงานนี้ไป {display}? [Y/N/skip]: Y (Auto)")
            
            update_task_status(plan, task["order"], "in_progress")
            main.dispatch_to_agent(agent, task["description"])
            
            print(f"  ผลลัพธ์ task #{task['order']}? [done/blocked/pending]: done (Auto)")
            update_task_status(plan, task["order"], "done", "ทำงานเรียบร้อย")
            main.log_action(f"Task #{task['order']} (Agent: {agent}) -> done")
            print(f"  ✅ Task #{task['order']} อัปเดตแล้ว")

        # Simulate some interactive commands
        print("\n🔹 ผู้บริหาร > status")
        main.log_action("📊 ผู้บริหารเรียกดูสถานะงาน (Status Tracker)")
        show_tracker()

        print("\n🔹 ผู้บริหาร > role 1")
        main.log_action("📄 ผู้บริหารเรียกดู Role ของ research")
        print("  (Role Content Shown)")

        print("\n🔹 ผู้บริหาร > 5")
        print("  ✅ เลือก 💻 IT Agent โดยตรง (ไม่ผ่านแผน)")
        main.log_action("🎯 ผู้บริหารเลือก it โดยตรง (Direct Dispatch)")
        main.dispatch_to_agent("it", "อัปเดตระบบ backup")

        print("\n🔹 ผู้บริหาร > quit")
        main.log_action("👋 ผู้บริหารออกจากระบบ")

        print("\n" + "=" * 60)
        print("  📊 สรุปแผนงานหลังกระจาย:")
        show_tracker()

    finally:
        # Restore stdout and get captured text
        sys.stdout = original_stdout
        captured_text = output_capture.getvalue()
        print(captured_text) # Still print to screen

        # Save to Output folder
        output_dir = os.path.join(PROJECT_ROOT, "Output")
        os.makedirs(output_dir, exist_ok=True)
        
        from datetime import datetime
        filename = f"test_result_{datetime.now():%Y%m%d_%H%M%S}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(captured_text)
        print(f"\n  💾 บันทึกผลการทดสอบลงใน: {filepath}")

if __name__ == "__main__":
    run_simulation()
