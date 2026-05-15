import llm_helper
import os

def revise_thesis_v2(feedback_path, draft_path, output_path):
    print(f"[*] Reading Advisor Feedback: {feedback_path}")
    with open(feedback_path, "r", encoding="utf-8") as f:
        feedback = f.read()
        
    print(f"[*] Reading Current Draft: {draft_path}")
    with open(draft_path, "r", encoding="utf-8") as f:
        draft = f.read()

    # สั่ง Writer แก้เนื้อหา
    print("[*] Writer Agent is revising the entire thesis (v2)...")
    prompt = f"""จงแก้ไขวิทยานิพนธ์ฉบับสมบูรณ์นี้ตาม Feedback ของที่ปรึกษาอย่างเคร่งครัด
ประเด็นที่ต้องแก้:
{feedback}

กฎเหล็ก:
- เน้นบริบทอุตสาหกรรม "กล่องกระดาษลูกฟูก" (Corrugated Box) 100% เท่านั้น
- ใส่รายละเอียดกระบวนการผลิต: การตัด, การพับ, การเคลือบกันชื้น
- ปรับค่า EF ให้ตรงตามมาตรฐานอุตสาหกรรมกระดาษ
- อ้างอิงแบบ APA 7th (ภาษาไทย) ให้สมบูรณ์และสอดคล้องทั้งเล่ม
- ห้ามมีภาษาอังกฤษปนเด็ดขาด

เนื้อหาเดิม:
{draft[:8000]}... (แก้ไขเฉพาะส่วนเนื้อหาหลัก)
"""

    sys_prompt = "คุณคือ PhD Writer ผู้เชี่ยวชาญการเขียนวิทยานิพนธ์ภาษาไทยวิชาการ"
    revised_content = llm_helper.call_llm(prompt, sys_prompt, agent_key="writer")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(revised_content)
        
    print(f"[+] Revised Thesis saved to: {output_path}")

if __name__ == "__main__":
    revise_thesis_v2("Meetings/feedback/feedback_final.md", "Output/thesis/Full_Thesis_Draft.md", "Output/thesis/Full_Thesis_Revised_v2.md")
