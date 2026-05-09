
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

def load_role(agent_name):
    filepath = os.path.join(PROJECT_ROOT, "Agent", f"00_Orchestrator.md" if agent_name == "orchestrator" else f"01_Research.md")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def run_cfo_test():
    user_input = "หางานวิจัย ให้ผมหน่อยเกี่ยวกับ CFO PDF file และ สรุปให้ด้วย"
    print(f"🚀 [REAL TEST] User Request: {user_input}")
    
    # 1. Thinking Phase
    print("\n" + "="*50)
    print("🧠 PHASE 1: THINKING (Orchestrator)")
    print("="*50)
    my_role = load_role("orchestrator")
    thinking_msg = llm_helper.get_thinking_response("Orchestrator Agent", user_input, my_role, agent_key="orchestrator")
    print(f"\n[Thinking]: {thinking_msg}")

    # 2. Planning Phase
    print("\n" + "="*50)
    print("🛠️ PHASE 2: IMPLEMENTATION (Planning)")
    print("="*50)
    # จำลองการสร้างแผน (ใช้ของจริงจาก planner.py)
    plan_json = planner.create_plan(user_input)
    plan = json.loads(plan_json)
    plan["thinking"] = thinking_msg
    
    print(f"✅ สร้างแผนงานสำเร็จ ID: {plan['id']}")
    for task in plan["tasks"]:
        print(f"   Task #{task['order']}: {task['agent']} -> {task['description']}")

    # 3. Execution Phase (Simulated but with real data)
    print("\n" + "="*50)
    print("🏃 PHASE 3: EXECUTION (Simulating Agent Results)")
    print("="*50)
    
    # Task 1: Research
    task1 = plan["tasks"][0]
    print(f"▶️ Executing Task #1: {task1['agent']}...")
    # จำลองการทำงานของ Research Agent (หรือจะรันจริงก็ได้ แต่เพื่อความรวดเร็วผมจะใช้ Mock ผลลัพธ์ที่สอดคล้องกับ CFO)
    task1_thinking = "วิเคราะห์คำว่า CFO (Carbon Footprint for Organization) และค้นหาไฟล์ PDF ในฐานข้อมูล References"
    task1_result = "พบไฟล์งานวิจัย 3 ฉบับเกี่ยวกับ CFO ในอุตสาหกรรมไทย (CFO_Guideline_V4.pdf, Research_CFO_2023.pdf)"
    planner.update_task_status(plan, 1, "done", result=task1_result, score=5, thinking=task1_thinking)
    print(f"✅ Task #1 Done: {task1_result}")

    # Task 2: Writer
    task2 = plan["tasks"][1]
    print(f"▶️ Executing Task #2: {task2['agent']}...")
    task2_thinking = "นำข้อมูลจากไฟล์ที่พบมาสรุปประเด็นสำคัญเรื่องการคำนวณคาร์บอนฟุตพริ้นท์"
    task2_result = "สรุปผล: CFO เน้นการวัดการปล่อยก๊าซเรือนกระจก 3 Scope หลัก โดย Guideline V4 มีการปรับปรุงเกณฑ์การคำนวณใหม่"
    planner.update_task_status(plan, 2, "done", result=task2_result, score=5, thinking=task2_thinking)
    print(f"✅ Task #2 Done: {task2_result}")

    # 4. Reporting Phase
    print("\n" + "="*50)
    print("📊 PHASE 4: FINAL REPORTING (Executive Summary)")
    print("="*50)
    
    # รวบรวมข้อมูลงานเหมือนใน main.py
    work_summary = f"ภารกิจหลัก: {plan['original_message']}\n"
    work_summary += f"กระบวนการคิดของผู้บริหาร (Orchestrator Thinking): {plan.get('thinking', 'N/A')}\n\n"
    work_summary += "--- ลำดับการดำเนินการ (Plan Flow) ---\n"
    for task in plan["tasks"]:
        agent = task["agent"]
        work_summary += f"{task['order']}. [{task['status']}] {agent}: {task['description']} (คะแนน: {task['score']}/5)\n"
        if task.get("thinking"):
            work_summary += f"   - การวิเคราะห์ของ Agent: {task['thinking']}\n"
        if task.get("result"):
            work_summary += f"   - ผลลัพธ์ที่ได้: {task['result']}\n"

    report_content = llm_helper.get_report_response("Orchestrator Agent", work_summary, my_role, agent_key="orchestrator")
    
    print("\n" + "="*50)
    print("🎯 FINAL REPORT FROM GEMMA 2:2B:")
    print("="*50)
    print(report_content)
    print("="*50)

    # บันทึกไฟล์
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(PROJECT_ROOT, "Output", "reports")
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, f"cfo_research_report_{timestamp}.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# 🎯 CFO Research Final Report\n")
        f.write(f"Plan ID: {plan['id']}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(report_content)
    
    print(f"\n✅ SUCCESS: Report saved to {report_file}")

if __name__ == "__main__":
    run_cfo_test()
