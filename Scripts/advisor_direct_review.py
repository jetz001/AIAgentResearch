import llm_helper
import os

def direct_advisor_review(thesis_path, output_path):
    print(f"[*] Advisor is reading: {thesis_path}")
    with open(thesis_path, "r", encoding="utf-8") as f:
        thesis_text = f.read()
    
    # ดึงบทบาทที่ปรึกษา
    role_path = "Agent/03_Advisor.md"
    role_content = ""
    if os.path.exists(role_path):
        with open(role_path, "r", encoding="utf-8") as f:
            role_content = f.read()
    
    prompt = f"""ในฐานะที่ปรึกษาวิทยานิพนธ์ (Advisor) โปรดตรวจสอบไฟล์วิทยานิพนธ์ฉบับสมบูรณ์ด้านล่างนี้ 
เน้นความถูกต้องของข้อมูล (ต้องเกี่ยวกับอุตสาหกรรมกล่องกระดาษลูกฟูก), ความต่อเนื่อง (Consistency), 
และการวิเคราะห์ช่องว่างงานวิจัย (Research Gaps)

วิทยานิพนธ์:
{thesis_text[:10000]}... (ตัดมาเฉพาะส่วนต้นเพื่อวิเคราะห์)

โปรดระบุ Feedback แบ่งเป็น:
1. Critical Issues (สิ่งที่ต้องแก้ทันที)
2. Major Issues (ประเด็นสำคัญ)
3. Minor Issues (จุดย่อย)
4. Suggestions for Future Research (ข้อเสนอแนะ)

เขียนเป็นภาษาไทยวิชาการ 100% ห้ามมีอังกฤษปน"""

    print("[*] Generating Academic Feedback...")
    feedback = llm_helper.call_llm(prompt, role_content, agent_key="advisor")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 👨‍🏫 Academic Feedback Report\n\n")
        f.write(feedback)
    
    print(f"[+] Feedback saved to: {output_path}")

if __name__ == "__main__":
    direct_advisor_review("Output/thesis/Full_Thesis_Draft.md", "Meetings/feedback/feedback_final.md")
