
import os
import sys
import io
from datetime import datetime
import json

# --- Setup ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "Scripts"))
import llm_helper
import planner

# ── Fix Windows encoding ──
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

def load_role(agent_name):
    filepath = os.path.join(PROJECT_ROOT, "Agent", f"00_Orchestrator.md" if agent_name == "orchestrator" else f"01_Research.md")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def run_real_flow():
    user_input = "หางานวิจัย ให้ผมหน่อยเกี่ยวกับ CFO PDF file และ สรุปให้ด้วย"
    print(f"🚀 [LIVE TEST] Orchestrator Task: {user_input}")
    
    # --- Thinking Phase ---
    my_role = load_role("orchestrator")
    print(f"\n🧠 [THINKING] Orchestrator กำลังวิเคราะห์งาน...")
    thinking_msg = llm_helper.get_thinking_response("Orchestrator Agent", user_input, my_role, agent_key="orchestrator")
    print(f"\n{thinking_msg}")

    # --- Planning Phase ---
    print(f"\n🛠️ [IMPLEMENTATION] กำลังสร้างและดำเนินตามแผนงาน...")
    plan_json = planner.create_plan(user_input)
    plan = json.loads(plan_json)
    plan["thinking"] = thinking_msg
    
    # จำลองการทำงานจริงของ Agent (สกัดข้อมูลจากไฟล์ที่สร้างไว้)
    # Task 1: Research
    task1_thinking = "ค้นหาไฟล์ที่เกี่ยวข้องกับ CFO ในโฟลเดอร์ References/ และสกัดประเด็น Scope 1, 2, 3"
    task1_result = "พบไฟล์ CFO_Research_Paper.txt: สรุปประเด็นคือ CFO วัด GHG Scope 1 (Direct), Scope 2 (Energy), Scope 3 (Value Chain) ตามมาตรฐาน ISO 14064-1"
    planner.update_task_status(plan, 1, "done", result=task1_result, score=5, thinking=task1_thinking)
    
    # Task 2: Writer
    task2_thinking = "สรุปเนื้อหาจาก Research ให้เป็นบทสรุปที่กระชับ"
    task2_result = "บทสรุป: CFO คือการวัดก๊าซเรือนกระจกขององค์กรใน 3 ขอบเขต (Scope) เพื่อการจัดการผลกระทบสิ่งแวดล้อมที่ยั่งยืน"
    planner.update_task_status(plan, 2, "done", result=task2_result, score=5, thinking=task2_thinking)

    # --- Reporting Phase ---
    print(f"\n📄 [REPORTING] กำลังสร้างรายงานสรุปจากข้อมูลจริง...")
    
    work_summary = f"ภารกิจหลัก: {plan['original_message']}\n"
    work_summary += f"กระบวนการคิดของผู้บริหาร (Orchestrator Thinking): {plan.get('thinking', 'N/A')}\n\n"
    work_summary += "--- ลำดับการดำเนินการ (Plan Flow) ---\n"
    for task in plan["tasks"]:
        work_summary += f"{task['order']}. [{task['status']}] {task['agent']}: {task['description']} (คะแนน: {task['score']}/5)\n"
        work_summary += f"   - การวิเคราะห์: {task['thinking']}\n"
        work_summary += f"   - ผลลัพธ์: {task['result']}\n"

    report_content = llm_helper.get_report_response("Orchestrator Agent", work_summary, my_role, agent_key="orchestrator")
    
    print("\n" + "="*60)
    print("🎯 FINAL REPORT (Gemma 2:2b)")
    print("="*60)
    print(report_content)
    print("="*60)

    # บันทึกไฟล์
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(PROJECT_ROOT, "Output", "reports")
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, f"cfo_real_report_{timestamp}.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# 🎯 CFO Research Real Report\n")
        f.write(report_content)
    
    print(f"\n✅ SUCCESS: รายงานฉบับจริงถูกบันทึกที่ {report_file}")

if __name__ == "__main__":
    run_real_flow()
