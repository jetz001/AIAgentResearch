
import os
import sys
import io
from datetime import datetime
import json

# --- Setup ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "Scripts"))
import llm_helper

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

def mock_plan_v2(message):
    return {
        "id": "TEST_PLAN_V2_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "original_message": message,
        "status": "done",
        "thinking": "วิเคราะห์แล้วว่างานนี้ต้องการความกระชับและตรงประเด็น โดยต้องให้ Agent สรุปข้อมูลสำคัญออกมาในรูปแบบที่สั้นที่สุด",
        "tasks": [
            {
                "order": 1, 
                "agent": "research", 
                "description": "วิเคราะห์และเลือกคำสรุป 3 คำ", 
                "status": "done", 
                "thinking": "คัดเลือกคำจากบริบทงานวิจัยที่สำคัญที่สุด 3 อย่าง คือ: วิจัย, นวัตกรรม, ยั่งยืน",
                "result": "คำที่เลือกคือ: วิจัย, นวัตกรรม, ยั่งยืน", 
                "score": 5
            },
            {
                "order": 2, 
                "agent": "writer", 
                "description": "จัดรูปแบบคำสรุป", 
                "status": "done", 
                "thinking": "นำคำที่เลือกมาจัดเรียงให้สวยงามและเป็นทางการ",
                "result": "สรุป 3 คำ: [วิจัย • นวัตกรรม • ยั่งยืน]", 
                "score": 5
            }
        ]
    }

AGENT_DISPLAY = {
    "research": "📚 Research",
    "writer":   "✍️  Writer",
}

def test_reporting_flow_v2():
    print("🚀 [TEST V2] Starting REAL Reporting Flow with Thinking & Plan Flow...")
    plan = mock_plan_v2("สรุปคำสั้นๆ 3 คำ")
    
    # Simulate the Reporting phase from main.py (v2)
    orchestrator_role = load_role("orchestrator")
    
    # รวบรวมข้อมูลงานแบบใหม่
    work_summary = f"ภารกิจหลัก: {plan['original_message']}\n"
    work_summary += f"กระบวนการคิดของผู้บริหาร (Orchestrator Thinking): {plan.get('thinking', 'N/A')}\n\n"
    work_summary += "--- ลำดับการดำเนินการ (Plan Flow) ---\n"
    for task in plan["tasks"]:
        status = task["status"]
        agent = AGENT_DISPLAY.get(task["agent"], task["agent"])
        score = f" (คะแนน: {task.get('score', 0)}/5)" if status == "done" else ""
        work_summary += f"{task['order']}. [{status}] {agent}: {task['description']}{score}\n"
        if task.get("thinking"):
            work_summary += f"   - การวิเคราะห์ของ Agent (Thinking): {task['thinking']}\n"
        if task.get("result"):
            work_summary += f"   - ผลลัพธ์ที่ได้ (Implementation Result): {task['result']}\n"

    print(f"\n🧠 [THINKING] วิเคราะห์งานที่เสร็จสิ้นเพื่อสร้างรายงาน...")
    
    print(f"\n📄 [REPORTING] กำลังสร้างรายงานสรุปผ่าน Gemma2:2b...")
    report_content = llm_helper.get_report_response("Orchestrator Agent", work_summary, orchestrator_role, agent_key="orchestrator")
    
    print("\n" + "="*50)
    print("🎯 FINAL REPORT RESULT (V2):")
    print("="*50)
    print(report_content)
    print("="*50)

    # บันทึกไฟล์
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(PROJECT_ROOT, "Output", "reports")
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, f"test_final_report_v2_{timestamp}.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# 🎯 Orchestrator Final Report (V2)\n")
        f.write(f"Plan ID: {plan['id']}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(report_content)
    
    print(f"\n✅ SUCCESS: Report saved to {report_file}")

if __name__ == "__main__":
    test_reporting_flow_v2()
