# 📊 Thesis Automation System: Main Workflow

```mermaid
graph TD
    Start["1. รับโจทย์ (User Input)"] --> Planner["2. วางแผนงาน (Planning Agent)"]
    Planner --> WritePlan["3. บันทึกแผนงานลงไฟล์ (Plan JSON)"]
    WritePlan --> CheckLoop{"4. ตรวจสอบลำดับงาน (Execution Loop)"}
    
    CheckLoop -- "แผนไม่ถูกต้อง/ไม่ตรงโจทย์" --> Planner
    CheckLoop -- "แผนถูกต้อง" --> Dispatch["5. จ่ายงานให้ลูกน้อง (Agent Dispatcher)"]
    
    Dispatch --> Research["Research: ค้นข้อมูล"]
    Dispatch --> Writer["Writer: ร่างเนื้อหา"]
    Dispatch --> QA["QA: ตรวจสอบคุณภาพ"]
    
    Research --> SharedData["6. เก็บข้อมูลกองกลาง (Shared Context)"]
    Writer --> SharedData
    QA --> SharedData
    
    SharedData --> Gatekeeper{"7. ด่านตรวจสอบ (QA Gatekeeper)"}
    
    Gatekeeper -- "ต้องแก้ไข" --> Writer
    Gatekeeper -- "อนุมัติผ่าน" --> Combine["8. รวบรวมเนื้อหา (Combine Thesis)"]
    
    Combine --> ExportWord["9. สร้างไฟล์ Word (.docx)"]
    Combine --> ExportHTML["10. สร้างไฟล์ HTML/PDF"]
    
    ExportWord --> ExecReview{"11. ผู้บริหาร (Orchestrator) ตรวจสอบ"}
    ExportHTML --> ExecReview
    
    ExecReview -- "ไม่ผ่าน (ต้องรื้อแผน)" --> Planner
    ExecReview -- "ผ่าน" --> AdvisorFinal["12. ที่ปรึกษา (Advisor) ตรวจสอบ"]
    
    AdvisorFinal -- "ผ่าน" --> Editor["13. Editor Agent ตรวจสอบ"]
    AdvisorFinal -- "ไม่ผ่าน" --> ExecReview
    
    Editor -- "ไม่ผ่าน" --> ExecReview
    Editor -- "ผ่าน" --> OrchestratorReport["14. ผู้บริหาร (Orchestrator) สรุปรายงาน"]
    
    OrchestratorReport --> CEOFinish["15. รายงานผลต่อ CEO (จบบริบูรณ์)"]

    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style CEOFinish fill:#f9f,stroke:#333,stroke-width:2px
    style Gatekeeper fill:#ffcc00,stroke:#333,stroke-width:2px
    style Dispatch fill:#00ccff,stroke:#333,stroke-width:2px
    style QA fill:#ffcc00,stroke:#333,stroke-width:2px
    style ExecReview fill:#00ff00,stroke:#333,stroke-width:2px
    style AdvisorFinal fill:#ffcc00,stroke:#333,stroke-width:2px
    style Editor fill:#00ffff,stroke:#333,stroke-width:2px
```

---

## 👨‍💼 รายละเอียดขั้นตอน (Executive Summary)

### 1. การวางแผน (Planning Phase)
*   **Planning Agent:** วางแผนงานตามโจทย์ที่ได้รับจาก CEO ผ่าน Orchestrator

### 2. การคุมคุณภาพและขัดเกลา (QC & Polishing)
*   **QA & Advisor:** ตรวจสอบความถูกต้องทางเทคนิคและวิชาการ
*   **Editor Agent:** ขัดเกลาภาษาให้สละสลวยในด่านสุดท้าย

### 3. การรายงานผลระดับสูง (Executive Reporting)
*   **Orchestrator Summary:** ผู้บริหารรวบรวมความสำเร็จและตรวจสอบความเรียบร้อยทั้งหมด
*   **CEO Delivery:** ส่งมอบผลงานที่สมบูรณ์แบบที่สุดถึงมือ CEO เพื่อปิดโครงการอย่างเป็นทางการ (จบบริบูรณ์)
