# 🎯 Main Workflow — Master's Thesis Research Project

> **Project:** _(ยังไม่ได้กำหนด — ดูที่ `Memory/Long Memory/research_topic.md`)_  
> **Organization:** _(ยังไม่ได้กำหนด)_  
> **Degree:** Master's (ปริญญาโท)  
> **System:** Multi-Agent AI Research Assistant  

---

## 📋 สารบัญ (Table of Contents)

1. [ภาพรวมระบบ (System Overview)](#1-ภาพรวมระบบ-system-overview)
2. [Agent Roles & Responsibilities](#2-agent-roles--responsibilities)
3. [Phase 1: Research & Literature Review](#3-phase-1-research--literature-review)
4. [Phase 2: Data Collection & Analysis](#4-phase-2-data-collection--analysis)
5. [Phase 3: Thesis Writing & Drafting](#5-phase-3-thesis-writing--drafting)
6. [Phase 4: Advisor Management](#6-phase-4-advisor-management)
7. [Phase 5: Publication & Editorial](#7-phase-5-publication--editorial)
8. [Phase 6: IT Operations](#8-phase-6-it-operations)
9. [Phase 7: HR & Team Coordination](#9-phase-7-hr--team-coordination)
10. [Workflow State Machine](#10-workflow-state-machine)
11. [Memory Management](#11-memory-management)
12. [Error Handling & Escalation](#12-error-handling--escalation)

---

## 1. ภาพรวมระบบ (System Overview)

```
┌─────────────────────────────────────────────────────────────────┐
│                    🧠 ORCHESTRATOR AGENT                        │
│              (Main Controller / Project Manager)                │
├────────┬────────┬────────┬────────┬────────┬────────┬──────────┤
│Research│ Writer │Advisor │ Editor │  IT    │  HR    │ QA       │
│ Agent  │ Agent  │ Agent  │ Agent  │ Agent  │ Agent  │ Agent    │
└────────┴────────┴────────┴────────┴────────┴────────┴──────────┘
     │        │        │        │        │        │        │
     ▼        ▼        ▼        ▼        ▼        ▼        ▼
 ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌─────────┐┌──────┐
 │ Docs ││Output││Memory││ Logs ││Scripts││Workspace││ Test │
 └──────┘└──┬───┘└──────┘└──────┘└──────┘└─────────┘└──────┘
            │
    ┌───────┼────────┬──────────┐
    ▼       ▼        ▼          ▼
 ┌──────┐┌──────┐┌──────┐┌─────────┐
 │thesis││pubs  ││ book ││ reports │
 └──────┘└──────┘└──────┘└─────────┘

 ┌──────────┐┌──────┐┌──────────┐┌──────┐┌──────┐┌──────┐
 │References││Config││ Templates││ Data ││Meetin││Archiv│
 └──────────┘└──────┘└──────────┘└──────┘└──────┘└──────┘
```

### Directory Mapping

| โฟลเดอร์ | หน้าที่ | ใช้โดย Agent |
|----------|---------|-------------|
| `Agent/` | Agent config, roles, prompts | Orchestrator |
| `Config/` | ⭐ API keys, `.env`, model settings, system config | IT Agent, Orchestrator |
| `Data/` | ⭐ ข้อมูลวิจัยดิบ (raw data จากแหล่งข้อมูล) | Research Agent |
| `Docs/` | เอกสารวิจัยที่สร้างขึ้น (summaries, analysis) | Research, Writer |
| `Logs/` | Activity logs, audit trail | ทุก Agent |
| `Memory/Long Memory/` | ความรู้ถาวร, decisions สำคัญ | Orchestrator |
| `Memory/Short memory/` | Context ปัจจุบัน, WIP data | Active Agent |
| `Meetings/` | ⭐ บันทึกประชุม advisor, minutes, action items | HR Agent, Advisor Agent |
| `Output/thesis/` | ⭐ ไฟล์วิทยานิพนธ์ (chapters, full draft) | Writer Agent |
| `Output/publications/` | ⭐ Manuscripts, journal papers | Writer, Editor |
| `Output/book/` | ⭐ หนังสือตีพิมพ์ (ต้นฉบับ, ปก, layout) | Editor Agent |
| `Output/reports/` | ⭐ Progress reports, weekly summaries | HR Agent |
| `PromptTemplates/` | Prompt templates สำหรับ AI Agent | ทุก Agent |
| `References/` | ⭐ PDF papers, citation database (.bib), แหล่งอ้างอิง | Research Agent |
| `Scripts/` | Automation scripts | IT Agent |
| `Templates/` | ⭐ แม่แบบเอกสาร (thesis template, paper template, ปกหนังสือ) | Writer, Editor |
| `Test/` | Test cases, validation | QA Agent |
| `Archive/` | ⭐ เก็บ versions เก่า, drafts ที่ไม่ใช้แล้ว | IT Agent |
| `Workflow/Mainworkflow/` | Main workflow definitions | Orchestrator |
| `Workflow/Subworkflow/` | Sub-task workflows | Task Agents |
| `Workspace/Decision/` | Decision logs & rationale | Orchestrator, Advisor |
| `Workspace/experiments/` | การทดลองวิเคราะห์ตามกรอบวิจัย | Research Agent |
| `Workspace/Tools/` | Utility tools & scripts | IT Agent |
| `Workspace/Sandbox/` | ⭐ พื้นที่ทดสอบ Agent ก่อนรันจริง | IT Agent, QA Agent |

---

## 2. Agent Roles & Responsibilities

### 🎯 Orchestrator Agent (หัวหน้าทีม)
- **หน้าที่:** ควบคุม workflow ทั้งหมด, จัดลำดับงาน, ตัดสินใจ
- **Input:** User request, Agent status reports
- **Output:** Task assignments, workflow transitions
- **Trigger:** ทุกครั้งที่มี task ใหม่ หรือ task เสร็จ

### 📚 Research Agent (นักวิจัย)
- **หน้าที่:** ค้นหา literature, วิเคราะห์ papers, สรุป findings
- **Tools:** Web search, PDF reader, citation manager
- **Output:** Literature review, research summaries → `Docs/`
- **Storage:** PDF papers, citations → `References/`
- **Raw Data:** ข้อมูลดิบจากแหล่งข้อมูล → `Data/`

### ✍️ Writer Agent (นักเขียน)
- **หน้าที่:** เขียน thesis chapters, drafts, abstracts
- **Input:** Research findings, outline, advisor feedback
- **Output:** Thesis documents → `Output/`

### 👨‍🏫 Advisor Agent (ที่ปรึกษา)
- **หน้าที่:** จำลองมุมมองอาจารย์ที่ปรึกษา, review, ให้ feedback
- **Input:** Drafts, research questions
- **Output:** Feedback, revision requests → `Workspace/Decision/`

### 📰 Editor Agent (บรรณาธิการ)
- **หน้าที่:** ตรวจสอบคุณภาพ, จัดรูปแบบ, เตรียม manuscript สำหรับตีพิมพ์
- **Input:** Final drafts
- **Output:** Publication-ready manuscripts → `Output/publications/`
- **Templates:** ใช้ journal/book templates จาก `Templates/`

### 💻 IT Agent (ไอที)
- **หน้าที่:** จัดการระบบ, automation, environment setup
- **Tools:** Scripts, CI/CD, backup
- **Output:** System reports, automated scripts → `Scripts/`
- **Config:** จัดการ API keys, environment → `Config/`
- **Archive:** จัดเก็บ versions เก่า → `Archive/`
- **Sandbox:** ทดสอบ agent → `Workspace/Sandbox/`

### 👥 HR Agent (ทรัพยากรบุคคล)
- **หน้าที่:** จัดการทีม, ประสานงาน, ติดตามกำหนดการ
- **Output:** Timeline, meeting schedules → `Meetings/`
- **Reports:** Progress reports → `Output/reports/`

### ✅ QA Agent (ควบคุมคุณภาพ)
- **หน้าที่:** ตรวจสอบความถูกต้อง, consistency, plagiarism check
- **Output:** QA reports → `Test/`

---

## 3. Phase 1: Research & Literature Review

```
START → [1.1] Define Research Questions
      → [1.2] Systematic Literature Search
      → [1.3] Screen & Filter Papers
      → [1.4] Extract & Summarize
      → [1.5] Gap Analysis
      → [1.6] Advisor Review (Gate)
      → NEXT PHASE or REVISE
```

### 1.1 Define Research Questions
| Item | Detail |
|------|--------|
| Agent | Orchestrator + Research |
| Input | หัวข้อวิจัย, ขอบเขต |
| Process | กำหนด RQ หลัก, RQ ย่อย, Keywords |
| Output | `Docs/research_questions.md` |
| Subworkflow | `Subworkflow/define_rq.md` |

### 1.2 Systematic Literature Search
| Item | Detail |
|------|--------|
| Agent | Research Agent |
| Input | Keywords, databases (Scopus, WoS, Google Scholar) |
| Process | ค้นหา, กรอง duplicates, จัดกลุ่ม |
| Output | `Docs/literature_database.csv` |
| Memory | บันทึก search strategy → `Memory/Long Memory/` |

### 1.3 Screen & Filter Papers
| Item | Detail |
|------|--------|
| Agent | Research Agent |
| Process | Title/Abstract screening → Full-text review |
| Criteria | Relevance, recency (5 yrs), methodology quality |
| Output | `Docs/selected_papers.md` |

### 1.4 Extract & Summarize
| Item | Detail |
|------|--------|
| Agent | Research Agent + Writer Agent |
| Process | สกัดข้อมูลสำคัญ, สร้าง summary table |
| Output | `Docs/literature_matrix.md` |

### 1.5 Gap Analysis
| Item | Detail |
|------|--------|
| Agent | Research Agent |
| Process | ระบุ Gap of Knowledge ตามหัวข้อวิจัย |
| Output | `Workspace/Decision/gap_analysis.md` |

### 1.6 Advisor Review Gate
| Item | Detail |
|------|--------|
| Agent | Advisor Agent |
| Process | ตรวจสอบ, ให้ feedback, approve/revise |
| Decision | ✅ Approve → Phase 2 / ❌ Revise → กลับ 1.x |
| Output | `Workspace/Decision/phase1_review.md` |

---

## 4. Phase 2: Data Collection & Analysis

```
[2.1] Design Methodology
→ [2.2] Prepare Data Collection Tools
→ [2.3] Collect Data (จากแหล่งข้อมูล)
→ [2.4] Primary Analysis (ตามกรอบวิจัยหลัก)
→ [2.5] Secondary Analysis (ตามกรอบวิจัยรอง)
→ [2.6] Integration & Cross-Analysis
→ [2.7] Advisor Review (Gate)
```

### 2.1 Design Methodology
| Item | Detail |
|------|--------|
| Agent | Research + Orchestrator |
| Process | เลือก research design, sampling, tools |
| Output | `Docs/methodology.md` |

### 2.2 Prepare Data Collection Tools
| Item | Detail |
|------|--------|
| Agent | IT Agent + Research Agent |
| Process | สร้างแบบฟอร์ม, spreadsheets, scripts |
| Output | `Workspace/Tools/data_collection/` |

### 2.3 Collect Data
| Item | Detail |
|------|--------|
| Agent | Research Agent (with human support) |
| Source | _(กำหนดเมื่อได้หัวข้อวิจัย)_ |
| Data | _(กำหนดเมื่อได้หัวข้อวิจัย)_ |
| Raw Storage | `Data/` (ข้อมูลดิบ) |
| Output | `Workspace/experiments/raw_data/` (ข้อมูลที่จัดรูปแบบแล้ว) |

### 2.4 Primary Analysis
| Item | Detail |
|------|--------|
| Agent | Research Agent |
| Process | _(กำหนดเมื่อได้หัวข้อวิจัย)_ |
| Framework | _(กำหนดเมื่อได้หัวข้อวิจัย)_ |
| Output | `Workspace/experiments/primary_results/` |

### 2.5 Secondary Analysis
| Item | Detail |
|------|--------|
| Agent | Research Agent |
| Process | _(กำหนดเมื่อได้หัวข้อวิจัย)_ |
| Output | `Workspace/experiments/secondary_results/` |

### 2.6 Integration & Cross-Analysis
| Item | Detail |
|------|--------|
| Agent | Research + QA Agent |
| Process | เชื่อมผลวิเคราะห์หลัก + รอง, หา correlation |
| Output | `Workspace/experiments/integrated_analysis/` |

### 2.7 Advisor Review Gate
| Item | Detail |
|------|--------|
| Agent | Advisor Agent |
| Decision | ✅ Approve → Phase 3 / ❌ Revise |
| Output | `Workspace/Decision/phase2_review.md` |

---

## 5. Phase 3: Thesis Writing & Drafting

```
[3.1] Create Outline
→ [3.2] Write Chapter 1 (Introduction)
→ [3.3] Write Chapter 2 (Literature Review)
→ [3.4] Write Chapter 3 (Methodology)
→ [3.5] Write Chapter 4 (Results)
→ [3.6] Write Chapter 5 (Discussion & Conclusion)
→ [3.7] Compile & Format
→ [3.8] QA Check
→ [3.9] Advisor Review (Gate)
```

### Writing Process (per chapter)

| Item | Detail |
|------|--------|
| Agent | Writer Agent (primary), Research Agent (support) |
| Input | Research data, literature, advisor feedback |
| Process | Draft → Self-review → QA → Advisor review → Revise |
| Output | `Output/thesis/chapter_X.md` |
| Quality | QA Agent ตรวจ: consistency, citation, formatting |

### 3.7 Compile & Format
| Item | Detail |
|------|--------|
| Agent | Writer + IT Agent |
| Process | รวม chapters, จัดรูปแบบตามมาตรฐานมหาวิทยาลัย |
| Template | ใช้ template จาก `Templates/thesis_template/` |
| Output | `Output/thesis/full_thesis.docx` |
| Archive | เก็บ draft เก่า → `Archive/thesis_drafts/` |

### 3.8 QA Check
| Item | Detail |
|------|--------|
| Agent | QA Agent |
| Checks | Plagiarism, citation accuracy, formatting, coherence |
| Output | `Test/thesis_qa_report.md` |

---

## 6. Phase 4: Advisor Management

```
[4.1] Schedule Meeting
→ [4.2] Prepare Meeting Materials
→ [4.3] Conduct Meeting (Record feedback)
→ [4.4] Process Feedback
→ [4.5] Update Plan & Documents
→ [4.6] Follow-up & Report
```

> 📁 **Primary Storage:** `Meetings/` — บันทึกการประชุมทั้งหมดกับ advisor

### Advisor Interaction Protocol

| สถานการณ์ | Action | Agent | Storage |
|-----------|--------|-------|----------|
| ส่งงานให้ review | สร้าง summary + draft → ส่ง | Writer + HR | `Meetings/` |
| รับ feedback | บันทึก → วิเคราะห์ → สร้าง action items | Advisor + Orchestrator | `Meetings/feedback/` |
| ขอนัดพบ | เตรียมวาระ, สรุปความคืบหน้า | HR Agent | `Meetings/schedules/` |
| Conflict/ไม่เห็นด้วย | บันทึกเหตุผลทั้งสองฝ่าย → Decision log | Orchestrator | `Workspace/Decision/` |

### Feedback Processing Pipeline
```
Advisor Feedback
    │
    ├── Critical (ต้องแก้ทันที) → Priority Task Queue
    ├── Major (ต้องแก้ก่อน submit) → Normal Task Queue
    └── Minor (แก้ได้ภายหลัง) → Backlog
    │
    ▼
Memory/Long Memory/advisor_feedback_log.md
```

---

## 7. Phase 5: Publication & Editorial

```
[5.1] Select Target Journal/Conference
→ [5.2] Prepare Manuscript
→ [5.3] Internal Review & Edit
→ [5.4] Format per Journal Guidelines
→ [5.5] Submit
→ [5.6] Handle Reviewer Feedback
→ [5.7] Revise & Resubmit
→ [5.8] Acceptance & Proofing
```

### 5.1 Select Target Journal
| Item | Detail |
|------|--------|
| Agent | Research + Advisor Agent |
| Criteria | Impact factor, scope fit, review timeline, OA options |
| Output | `Workspace/Decision/target_journal.md` |

### 5.2–5.3 Manuscript Preparation
| Item | Detail |
|------|--------|
| Agent | Writer + Editor Agent |
| Process | Extract key findings → Draft paper → Internal review |
| Format | IMRaD (Introduction, Methods, Results, Discussion) |
| Output | `Output/publications/manuscript_v1.md` |

### 5.4 Journal Formatting
| Item | Detail |
|------|--------|
| Agent | Editor Agent + IT Agent |
| Process | Apply journal template, citation style, word limit |
| Template | ใช้ journal template จาก `Templates/journal_templates/` |
| References | อ้างอิงจาก `References/` |
| Output | `Output/publications/manuscript_formatted.docx` |

### 5.5–5.8 Submission & Review Cycle
| Item | Detail |
|------|--------|
| Agent | Editor (primary), Writer (revisions) |
| Process | Submit → Track status → Respond to reviewers |
| Log | `Logs/publication_tracker.md` |

### Book Publishing (ตีพิมพ์หนังสือ)
| Item | Detail |
|------|--------|
| Agent | Editor Agent (บรรณาธิการ) |
| Process | Content curation → Chapter organization → Proofreading → Layout → ISBN |
| Checklist | ✅ ต้นฉบับ ✅ ปก ✅ สารบัญ ✅ บรรณานุกรม ✅ ดัชนี |
| Output | `Output/book/` |

---

## 8. Phase 6: IT Operations

```
[6.1] Environment Setup & Maintenance
[6.2] Data Pipeline & Automation
[6.3] Backup & Version Control
[6.4] Tool Development
[6.5] System Monitoring
```

### IT Responsibilities

| Task | Detail | Schedule | Storage |
|------|--------|----------|----------|
| Environment setup | Python, CrewAI, dependencies | เริ่มโปรเจค | `Config/` |
| Config management | API keys, `.env`, model settings | ต่อเนื่อง | `Config/` |
| Backup | ข้อมูลวิจัย, thesis drafts → cloud | ทุกวัน | `Archive/` |
| Version control | Git commits, branching strategy | ทุก change | `Archive/` |
| Automation scripts | Data processing, report generation | ตามต้องการ | `Scripts/` |
| System health | ตรวจสอบ API keys, disk space, logs | รายสัปดาห์ | `Logs/` |
| Security | API key rotation, access control | รายเดือน | `Config/` |
| Sandbox testing | ทดสอบ Agent ก่อนรันจริง | ก่อน deploy | `Workspace/Sandbox/` |

### Automation Scripts (`Scripts/`)

| Script | หน้าที่ |
|--------|---------|
| `backup.py` | Automated backup to cloud |
| `data_pipeline.py` | Raw data → cleaned data → analysis |
| `report_generator.py` | สร้างรายงานความคืบหน้าอัตโนมัติ |
| `citation_formatter.py` | จัดรูปแบบ citation ตาม style |
| `health_check.py` | ตรวจสอบสถานะระบบ |

---

## 9. Phase 7: HR & Team Coordination

```
[7.1] Timeline & Milestone Management
[7.2] Meeting Coordination
[7.3] Progress Tracking
[7.4] Resource Allocation
[7.5] Risk Management
```

### Master Timeline

| Phase | ระยะเวลา | Milestone | Status |
|-------|----------|-----------|--------|
| Phase 1: Literature Review | เดือน 1–2 | Literature matrix complete | ⬜ |
| Phase 2: Data Collection | เดือน 2–4 | Data collected & analyzed | ⬜ |
| Phase 3: Thesis Writing | เดือน 4–6 | Full draft complete | ⬜ |
| Phase 4: Advisor Review | ต่อเนื่อง | All feedback addressed | ⬜ |
| Phase 5: Publication | เดือน 5–8 | Paper submitted/accepted | ⬜ |
| Defense | เดือน 7–8 | Thesis defended | ⬜ |

### Progress Report Template
```
📊 Weekly Progress Report
─────────────────────────
📅 สัปดาห์: [W##]
✅ สำเร็จ: [completed items]
🔄 กำลังทำ: [in progress items]
⚠️ ปัญหา/อุปสรรค: [blockers]
📅 แผนสัปดาห์หน้า: [next week plan]
📈 Overall Progress: [##%]
```

### Risk Register

| Risk | ผลกระทบ | โอกาส | Mitigation |
|------|---------|-------|------------|
| Advisor ไม่ว่าง | สูง | กลาง | นัดล่วงหน้า, เตรียม async review |
| ข้อมูลไม่ครบ | สูง | กลาง | เก็บข้อมูลเผื่อ, secondary sources |
| API/System ล่ม | กลาง | ต่ำ | Backup provider, local fallback |
| Deadline พลาด | สูง | ต่ำ | Buffer time, weekly tracking |
| Paper ถูก reject | กลาง | กลาง | เตรียม journal สำรอง |

---

## 10. Workflow State Machine

```
                    ┌──────────────┐
                    │   IDLE       │
                    └──────┬───────┘
                           │ new_task
                           ▼
                    ┌──────────────┐
              ┌─────│  PLANNING    │─────┐
              │     └──────┬───────┘     │
              │            │ approved    │ need_info
              │            ▼             ▼
              │     ┌──────────────┐  ┌──────────┐
              │     │  EXECUTING   │  │ RESEARCH │
              │     └──────┬───────┘  └────┬─────┘
              │            │ done          │ found
              │            ▼               │
              │     ┌──────────────┐       │
              │     │  REVIEWING   │◄──────┘
              │     └──────┬───────┘
              │         │       │
              │    approved   revision_needed
              │         │       │
              │         ▼       ▼
              │  ┌──────────┐ ┌──────────┐
              │  │COMPLETED │ │ REVISING │──┐
              │  └──────────┘ └──────────┘  │
              │                     ▲       │
              │                     └───────┘
              │ blocked
              ▼
       ┌──────────────┐
       │   BLOCKED    │──── resolved ───► PLANNING
       └──────────────┘
```

### State Transitions

| From | To | Trigger | Agent |
|------|----|---------|-------|
| IDLE | PLANNING | new_task received | Orchestrator |
| PLANNING | EXECUTING | plan approved | Orchestrator |
| PLANNING | RESEARCH | need more info | Research |
| EXECUTING | REVIEWING | task done | QA / Advisor |
| REVIEWING | COMPLETED | approved | Orchestrator |
| REVIEWING | REVISING | needs revision | Writer / Research |
| REVISING | REVIEWING | revision done | QA |
| Any | BLOCKED | blocker found | Any |
| BLOCKED | PLANNING | blocker resolved | Orchestrator |

---

## 11. Memory Management

### Long Memory (`Memory/Long Memory/`)
- **เก็บอะไร:** Decisions, approved strategies, key findings, advisor preferences
- **Format:** Structured markdown with timestamps
- **Retention:** ตลอดโปรเจค
- **Example files:**
  - `research_decisions.md` — การตัดสินใจสำคัญด้านงานวิจัย
  - `advisor_preferences.md` — สไตล์และความชอบของอาจารย์ที่ปรึกษา
  - `methodology_choices.md` — เหตุผลในการเลือก methodology

### Short Memory (`Memory/Short memory/`)
- **เก็บอะไร:** Current task context, WIP data, session state
- **Format:** JSON / Markdown
- **Retention:** ระหว่าง task execution → clear เมื่อ task เสร็จ
- **Example files:**
  - `current_task.json` — task ที่กำลังทำอยู่
  - `session_context.md` — context ของ session ปัจจุบัน

---

## 12. Error Handling & Escalation

### Escalation Matrix

| Level | สถานการณ์ | Action | ใครจัดการ |
|-------|-----------|--------|----------|
| L1 | Minor error (typo, format) | Auto-fix | QA Agent |
| L2 | Task failure (API error) | Retry + log | IT Agent |
| L3 | Decision conflict | บันทึก + ขอ input | Orchestrator |
| L4 | Blocker (advisor unavailable) | Escalate to human | HR Agent |
| L5 | Critical (data loss, deadline) | 🚨 Alert human immediately | Orchestrator |

### Retry Policy
```
Max retries: 3
Backoff: exponential (1s → 2s → 4s)
On failure: log to Logs/ → escalate to next level
```

### Logging Standard
```
[TIMESTAMP] [AGENT] [LEVEL] [PHASE] Message
─────────────────────────────────────────────
[2026-05-07 11:00] [Research] [INFO] [Phase1] Started literature search
[2026-05-07 11:05] [Research] [WARN] [Phase1] API rate limit hit, retrying...
[2026-05-07 11:06] [IT]       [ERROR][Phase1] Backup failed: disk full
```

---

## 🔄 Quick Reference: Daily Operation Flow

```
Morning Standup (Auto)
    │
    ├── HR Agent: สรุปงานวันนี้, deadlines
    ├── QA Agent: ผลตรวจสอบจากเมื่อวาน
    └── Orchestrator: จัดลำดับงานวันนี้
    │
    ▼
Execute Tasks (ตามลำดับ priority)
    │
    ├── Research / Writer / Editor ทำงานตาม queue
    ├── IT Agent: monitor & support
    └── Advisor Agent: review เมื่อมี draft
    │
    ▼
Evening Wrap-up (Auto)
    │
    ├── Orchestrator: สรุปผลงานวันนี้
    ├── IT Agent: backup
    └── HR Agent: update timeline & progress
    │
    ▼
Log to Memory + Logs/
```

---

> **Last Updated:** 2026-05-07  
> **Version:** 1.1 — เพิ่ม 8 folders ใหม่ (Config, Data, Archive, Templates, Meetings, References, Output subfolders, Workspace/Sandbox)  
> **Maintained by:** Orchestrator Agent
