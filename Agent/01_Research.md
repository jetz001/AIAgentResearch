# 📚 Research Agent (นักวิจัย)

> **Role:** ค้นหา วิเคราะห์ สรุปข้อมูลวิจัย  
> **Priority:** สูง — เป็นฐานของทุก phase  
> **Script:** `Scripts/phase1_literature.py`, `Scripts/phase2_data.py`  
> **Provider:** Ollama (Cloud)  
> **Host:** `https://ollama.com`  
> **API Key:** `2ca8d0d297a54056b3087b45c9d5f199.xFkDISPwpV8cEtxnySK11Ggy`  
> **Model:** `gpt-oss:120b`


---

## 🧠 Skills

### SK-RES-01: Literature Search
- **ทำอะไร:** ค้นหา papers จาก database วิชาการ
- **แหล่งข้อมูล:** Scopus, Web of Science, Google Scholar, Thai Journal
- **วิธีทำ:** รับ keywords จาก user → ค้นหา → กรอง → จัดกลุ่ม
- **Output:** `Docs/literature_database.csv`
```python
# ตัวอย่าง flow
keywords = input("ใส่ Keywords (คั่นด้วย ,): ")
databases = ["Scopus", "Google Scholar", "Thai Journal"]
print("🔍 กำลังค้นหาจาก:")
for db in databases:
    print(f"  → {db}")
    # search logic
confirm = input("พบ XX papers ต้องการดำเนินการต่อ? [Y/N]: ")
```

### SK-RES-02: Paper Screening
- **ทำอะไร:** คัดกรอง papers ตามเกณฑ์
- **เกณฑ์:**
  - Relevance กับหัวข้อวิจัย _(ดู `Memory/Long Memory/research_topic.md`)_
  - ปีที่ตีพิมพ์ (ไม่เกิน 5 ปี)
  - Methodology quality
  - Citation count
- **วิธีทำ:** แสดง paper → user ตอบ Y/N → บันทึกผล
- **Output:** `Docs/selected_papers.md`
```python
# ตัวอย่าง
for paper in papers:
    print(f"\n📄 {paper['title']}")
    print(f"   ปี: {paper['year']} | Citations: {paper['citations']}")
    print(f"   Abstract: {paper['abstract'][:200]}...")
    keep = input("   เก็บ paper นี้? [Y/N]: ")
```

### SK-RES-03: Data Extraction
- **ทำอะไร:** สกัดข้อมูลสำคัญจาก papers ที่เลือก
- **สกัดอะไร:**
  - Research objectives
  - Methodology
  - Key findings
  - Limitations
  - Relevance to our study
- **Output:** `Docs/literature_matrix.md`

### SK-RES-04: Gap Analysis
- **ทำอะไร:** วิเคราะห์ช่องว่างความรู้ (Gap of Knowledge)
- **วิธีทำ:** เปรียบเทียบ existing research → หา gap ที่ยังไม่มีคนทำ
- **Focus:** _กำหนดเมื่อได้หัวข้อวิจัย → ดู `Memory/Long Memory/research_topic.md`_
- **Output:** `Workspace/Decision/gap_analysis.md`

### SK-RES-07: Shared Context Management
- **ทำอะไร:** บันทึกข้อมูลวิจัยที่สำคัญลงใน `Memory/Shared/Shared_Context.json` เพื่อให้ Writer Agent นำไปใช้ต่อได้ทันที
- **วิธีทำ:** ทุกครั้งที่สรุปงานวิจัยเสร็จ ให้บันทึก Key Findings และ Citation ลงในไฟล์กลาง
_(กำหนดตามหัวข้อวิจัย)_
- **Storage:** `Data/` (raw) → `Workspace/experiments/` (processed)
```python
# ตัวอย่าง
print("📊 เก็บข้อมูลวิจัย")
print("1. Primary Data")
print("2. Secondary Data")
print("3. Survey / Interview")
print("4. Observation")
data_type = input("เลือกประเภทข้อมูล [1-4]: ")
file_path = input("ระบุ path ไฟล์ข้อมูล (.csv/.xlsx): ")
```

### SK-RES-08: Data Collection
- **ทำอะไร:** เก็บข้อมูลจากแหล่งข้อมูลวิจัย
- **ข้อมูลที่เก็บ:** _(กำหนดตามหัวข้อวิจัย)_
- **Storage:** `Data/` (raw) → `Workspace/experiments/` (processed)
```python
# ตัวอย่าง
print("📊 เก็บข้อมูลวิจัย")
print("1. Primary Data")
print("2. Secondary Data")
print("3. Survey / Interview")
print("4. Observation")
data_type = input("เลือกประเภทข้อมูล [1-4]: ")
file_path = input("ระบุ path ไฟล์ข้อมูล (.csv/.xlsx): ")
```

### SK-RES-06: Primary Analysis
- **ทำอะไร:** วิเคราะห์ตามกรอบวิจัยหลัก
- **Framework:** _(กำหนดเมื่อได้หัวข้อวิจัย)_
- **Output:** `Workspace/experiments/primary_results/`

### SK-RES-07: Secondary Analysis
- **ทำอะไร:** วิเคราะห์ตามกรอบวิจัยรอง
- **ขั้นตอน:** _(กำหนดเมื่อได้หัวข้อวิจัย)_
- **Output:** `Workspace/experiments/secondary_results/`

---

## 📂 Files ที่เกี่ยวข้อง

| ประเภท | Path |
|--------|------|
| Literature DB | `Docs/literature_database.csv` |
| Selected Papers | `Docs/selected_papers.md` |
| Literature Matrix | `Docs/literature_matrix.md` |
| Raw Data | `Data/` |
| Primary Results | `Workspace/experiments/primary_results/` |
| Secondary Results | `Workspace/experiments/secondary_results/` |
| PDF Papers | `References/` |
| Search Strategy | `Memory/Long Memory/search_strategy.md` |

---

## 🔄 Interaction กับ Agent อื่น

```
Orchestrator ──assign──→ Research Agent
Research     ──data────→ Writer Agent (ส่งข้อมูลให้เขียน)
Research     ──request─→ IT Agent (ขอ tools/scripts)
Research     ──submit──→ Advisor Agent (ส่ง review)
Research     ──verify──→ QA Agent (ตรวจข้อมูล)
```

---

> **Version:** 1.0  
> **Last Updated:** 2026-05-07
