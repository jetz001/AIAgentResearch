# ✍️ Writer Agent (นักเขียน)

> **Role:** เขียน thesis, drafts, manuscripts ทุกประเภท  
> **Priority:** สูง — สร้างผลลัพธ์หลักของโปรเจค  
> **Script:** `Scripts/phase3_writing.py`

---

## 🧠 Skills

### SK-WRT-01: Thesis Outline Creation
- **ทำอะไร:** สร้างโครงร่างวิทยานิพนธ์
- **โครงสร้าง:**
  - บทที่ 1: บทนำ
  - บทที่ 2: ทบทวนวรรณกรรม
  - บทที่ 3: วิธีการวิจัย
  - บทที่ 4: ผลการวิจัย
  - บทที่ 5: สรุป อภิปราย ข้อเสนอแนะ
- **Output:** `Output/thesis/outline.md`
```python
# ตัวอย่าง
print("📝 สร้างโครงร่าง Thesis")
print("=" * 40)
for i, ch in enumerate(chapters, 1):
    print(f"  บทที่ {i}: {ch}")
    sections = input(f"  → หัวข้อย่อย (คั่นด้วย ,): ")
confirm = input("ยืนยันโครงร่าง? [Y/N]: ")
```

### SK-WRT-02: Chapter Writing
- **ทำอะไร:** เขียนเนื้อหาแต่ละบท
- **วิธีทำ:** อ่าน outline + research data → เขียน draft → user review
- **Input:** `Docs/literature_matrix.md`, `Workspace/experiments/*`
- **Output:** `Output/thesis/chapter_X.md`
- **แต่ละบทมี sub-flow:**
```
เลือกบท → โหลดข้อมูลที่เกี่ยวข้อง → เขียน section ทีละส่วน
→ user ตรวจ Y/N → แก้ไข → save
```

### SK-WRT-03: Abstract Writing
- **ทำอะไร:** เขียนบทคัดย่อ (ไทย + English)
- **ข้อจำกัด:** ไม่เกิน 350 คำ
- **ต้องมี:** วัตถุประสงค์, วิธีการ, ผลลัพธ์หลัก, สรุป
- **Output:** `Output/thesis/abstract_th.md`, `Output/thesis/abstract_en.md`

### SK-WRT-04: Manuscript Drafting (สำหรับตีพิมพ์)
- **ทำอะไร:** เขียน manuscript สำหรับ journal
- **Format:** IMRaD (Introduction, Methods, Results, Discussion)
- **Input:** ข้อมูลจาก thesis + target journal guidelines
- **Output:** `Output/publications/manuscript_v1.md`
```python
# ตัวอย่าง
print("📰 เตรียม Manuscript")
journal = input("Target Journal: ")
word_limit = input("Word Limit: ")
print(f"กำลังเตรียม manuscript สำหรับ {journal}...")
```

### SK-WRT-05: Revision Handling
- **ทำอะไร:** แก้ไขตาม feedback ของ Advisor/Reviewer
- **วิธีทำ:** อ่าน feedback → แสดงให้ user → ถาม Y/N ว่าแก้ไหม → แก้
- **Input:** `Meetings/feedback/`
- **Output:** updated chapter/manuscript
- **Archive:** เก็บ version เก่า → `Archive/thesis_drafts/`

### SK-WRT-06: Citation Integration
- **ทำอะไร:** ใส่ citation ในเนื้อหา
- **Format:** APA 7th Edition (หรือตาม journal)
- **Source:** `References/` (.bib file)
- **วิธีทำ:** แสดงประโยค → ถาม user ว่าต้อง cite ไหม → ใส่ citation

---

## 📂 Files ที่เกี่ยวข้อง

| ประเภท | Path |
|--------|------|
| Thesis chapters | `Output/thesis/chapter_*.md` |
| Full thesis | `Output/thesis/full_thesis.docx` |
| Manuscript | `Output/publications/manuscript_v*.md` |
| Template | `Templates/thesis_template/` |
| References | `References/*.bib` |
| Advisor feedback | `Meetings/feedback/` |
| Old versions | `Archive/thesis_drafts/` |

---

## 🔄 Interaction กับ Agent อื่น

```
Research Agent ──data────→ Writer Agent
Advisor Agent  ──feedback→ Writer Agent
Writer Agent   ──draft───→ QA Agent (ตรวจสอบ)
Writer Agent   ──draft───→ Editor Agent (จัดรูปแบบ)
Writer Agent   ──submit──→ Advisor Agent (ส่ง review)
```

---

> **Version:** 1.0  
> **Last Updated:** 2026-05-07
