
import os
import sys
import io
from datetime import datetime

# --- Setup ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Fix Windows encoding ──
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

def mock_get_report_response(agent_name, work_summary, role, agent_key=None):
    return f"""
# 📋 รายงานสรุปผลการดำเนินงาน (MOCK)
เรียน ผู้ใช้,

ตามที่คุณมอบหมายภารกิจ: "ช่วยหาเปเปอร์เรื่อง AI และเขียนสรุป" 
บัดนี้ทีม Agent ได้ดำเนินการเสร็จสิ้นแล้ว โดยมีสรุปดังนี้:

1. **📚 Research Agent**: ค้นหาเปเปอร์ AI สำเร็จ (คะแนน: 5/5)
   - ผลลัพธ์: พบเปเปอร์ 5 ฉบับเกี่ยวกับ Deep Learning
2. **✍️  Writer Agent**: เขียนสรุปเรียบร้อย (คะแนน: 4/5)
   - ผลลัพธ์: สรุปเนื้อหาเปเปอร์เรียบร้อยแล้ว

**ความเห็นจากผู้บริหาร**: การดำเนินงานเป็นไปตามแผนและมีคุณภาพดี พร้อมสำหรับการส่งมอบงาน
"""

def test_reporting_flow_mock():
    print("🚀 [TEST-MOCK] Starting Reporting Flow Test...")
    plan = {
        "id": "TEST_PLAN_MOCK_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "original_message": "ช่วยหาเปเปอร์เรื่อง AI และเขียนสรุป",
        "tasks": [
            {"order": 1, "agent": "research", "description": "ค้นหาเปเปอร์ AI", "status": "done", "result": "พบเปเปอร์ 5 ฉบับเกี่ยวกับ Deep Learning", "score": 5},
            {"order": 2, "agent": "writer", "description": "เขียนสรุป", "status": "done", "result": "สรุปเนื้อหาเปเปอร์เรียบร้อยแล้ว", "score": 4}
        ]
    }
    
    # Simulate logic from main.py
    work_summary = f"แผนงาน ID: {plan['id']}\n"
    work_summary += f"ภารกิจหลัก: {plan['original_message']}\n\n"
    for task in plan["tasks"]:
        status = task["status"]
        agent = task["agent"]
        score = f" (คะแนน: {task.get('score', 0)}/5)" if status == "done" else ""
        work_summary += f"- [{status}] {agent}: {task['description']}{score}\n"
        if task.get("result"):
            work_summary += f"  ผลลัพธ์: {task['result']}\n"

    print(f"\n📄 [REPORTING] กำลังสร้างรายงานสรุป (Mocking LLM Response)...")
    report_content = mock_get_report_response("Orchestrator Agent", work_summary, "Executive Role")
    
    print("\n" + "="*50)
    print("🎯 FINAL REPORT RESULT (MOCK):")
    print("="*50)
    print(report_content)
    print("="*50)

    # บันทึกไฟล์ตาม Logic ใน main.py
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(PROJECT_ROOT, "Output", "reports")
    os.makedirs(output_dir, exist_ok=True)
    report_file = os.path.join(output_dir, f"orchestrator_final_report_{timestamp}.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# 🎯 Orchestrator Final Report\n")
        f.write(f"Plan ID: {plan['id']}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(report_content)
    
    print(f"\n✅ SUCCESS: Report saved to {report_file}")
    return report_file

if __name__ == "__main__":
    test_reporting_flow_mock()
