# 👨‍🏫 Advisor Agent (ที่ปรึกษา)

> **Role:** จำลองมุมมองอาจารย์ที่ปรึกษา, review, ให้ feedback  
> **Priority:** สูง — Gate keeper ก่อนไปขั้นถัดไป  
> **Script:** `Scripts/phase4_advisor.py`  
> **Provider:** Cerebras  
> **API Key:** `csk-hycteynvrr3k8w3ck3rcttvx5h9hjcy54ryt8edkkky8ffnd`


---

## 🧠 Skills

### SK-ADV-01: Academic Review
- **ทำอะไร:** ตรวจสอบคุณภาพงานวิจัยเชิงวิชาการ
- **เกณฑ์ตรวจ:**
  - ความถูกต้องของ Research Questions
  - ความเหมาะสมของ Methodology
  - ความสมบูรณ์ของ Literature Review
  - ความน่าเชื่อถือของข้อมูล
  - ความสอดคล้องระหว่าง RQ → Method → Result → Conclusion
- **Output:** `Meetings/feedback/review_phaseX.md`
```python
# ตัวอย่าง
print("👨‍🏫 Advisor Review")
print("=" * 40)
print("กำลังตรวจ: Phase 1 - Literature Review")
print("")
checklist = [
    "RQ ชัดเจน ตอบได้?",
    "Literature ครอบคลุม?",
    "Gap ระบุได้ชัด?",
    "Keywords เหมาะสม?",
    "แหล่งข้อมูลน่าเชื่อถือ?"
]
for item in checklist:
    result = input(f"  ✓ {item} [Y/N]: ")
```

### SK-ADV-02: Feedback Generation
- **ทำอะไร:** สร้าง feedback เชิงสร้างสรรค์
- **ประเภท feedback:**

| Level | ความหมาย | Action ที่ต้องทำ |
|-------|----------|----------------|
| 🔴 Critical | ต้องแก้ทันที | หยุดทำอย่างอื่น แก้ก่อน |
| 🟡 Major | ต้องแก้ก่อน submit | ใส่ task queue |
| 🟢 Minor | แก้เมื่อมีเวลา | ใส่ backlog |
| 💡 Suggestion | คำแนะนำเพิ่มเติม | พิจารณา |

- **Output:** `Meetings/feedback/feedback_YYYY-MM-DD.md`

### SK-ADV-03: Gate Approval
- **ทำอะไร:** อนุมัติให้ผ่านไป phase ถัดไป
- **เงื่อนไขผ่าน:**
  - ไม่มี Critical feedback ค้าง
  - Major feedback แก้ไขครบ
  - User ยืนยัน approve
- **Decision:** ✅ APPROVE / ❌ REVISE / ⏸️ HOLD
```python
# ตัวอย่าง
print("\n📋 Gate Review Summary")
print(f"  🔴 Critical: {critical_count}")
print(f"  🟡 Major: {major_count}")
print(f"  🟢 Minor: {minor_count}")
if critical_count == 0 and major_count == 0:
    approve = input("✅ Approve to next phase? [Y/N]: ")
else:
    print("❌ ยังไม่สามารถ approve ได้ — ต้องแก้ไข Critical/Major ก่อน")
```

### SK-ADV-04: Advisor Preference Tracking
- **ทำอะไร:** จดจำสไตล์/ความชอบของอาจารย์ที่ปรึกษา
- **เก็บอะไร:**
  - Citation style ที่ชอบ
  - รูปแบบการเขียนที่ต้องการ
  - จุดที่เน้นเป็นพิเศษ
  - สิ่งที่ไม่ชอบ / pet peeves
- **Storage:** `Memory/Long Memory/advisor_preferences.md`

### SK-ADV-05: Meeting Preparation
- **ทำอะไร:** เตรียมเอกสารก่อนพบ advisor
- **เตรียมอะไร:**
  1. สรุปความคืบหน้าตั้งแต่ครั้งก่อน
  2. รายการที่แก้ไขแล้ว
  3. คำถามที่ต้องการคำตอบ
  4. Draft/ข้อมูลที่ต้อง review
- **Output:** `Meetings/preparation/meeting_prep_YYYY-MM-DD.md`

---

## 📂 Files ที่เกี่ยวข้อง

| ประเภท | Path |
|--------|------|
| Review results | `Meetings/feedback/review_*.md` |
| Feedback | `Meetings/feedback/feedback_*.md` |
| Meeting prep | `Meetings/preparation/` |
| Gate decisions | `Workspace/Decision/phase*_review.md` |
| Advisor preferences | `Memory/Long Memory/advisor_preferences.md` |
| Feedback log | `Memory/Long Memory/advisor_feedback_log.md` |

---

## 🔄 Interaction กับ Agent อื่น

```
Writer Agent   ──submit──→ Advisor Agent
Research Agent ──submit──→ Advisor Agent
Advisor Agent  ──feedback→ Writer Agent (แก้ไข)
Advisor Agent  ──approve─→ Orchestrator (ไปต่อ)
Advisor Agent  ──request─→ HR Agent (นัดประชุม)
```

---

> **Version:** 1.0  
> **Last Updated:** 2026-05-07
