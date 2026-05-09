import llm_helper
import sys
import io

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

print("Testing Expanded Instruction...")
msg = "หางานวิจัย ให้ผมหน่อยเกี่ยวกับ CFO PDF file และ สรุปให้ด้วย"
agent = "📚 Research"
kws = "วิจัย, ค้นหา, ข้อมูล"

expanded = llm_helper.get_expanded_instruction(msg, agent, kws)
print(f"Result: {expanded}")
