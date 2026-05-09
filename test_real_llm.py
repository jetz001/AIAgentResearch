import os
import sys
import io
import time
from datetime import datetime

# Fix Windows encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

from Scripts import llm_helper

def print_box(title, content, color_code="36"):
    print(f"\n\033[{color_code}m┌" + "─" * 68 + "┐")
    print(f"│ {title:<66} │")
    print("├" + "─" * 68 + "┤")
    for line in content.split('\n'):
        while len(line) > 66:
            print(f"│ {line[:66]:<66} │")
            line = line[66:]
        print(f"│ {line:<66} │")
    print("└" + "─" * 68 + "┘\033[0m")

def get_role(name):
    path = os.path.join(PROJECT_ROOT, "Agent", name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f: return f.read()
    return ""

def run_test():
    print("\n" + "="*70)
    print("  🚀 STARTING FULL SYSTEM TEST (Local Ollama: gemma2:2b)")
    print("="*70)

    topic = "การประเมินคาร์บอนฟุตพริ้นท์ในอุตสาหกรรมกล่องกระดาษด้วย MFCA"
    print(f"\n🔹 หัวข้อวิจัย: {topic}")
    
    # 1. Orchestrator
    print("\n[SYSTEM] Orchestrator กำลังวางแผน...")
    orc_role = get_role("00_Orchestrator.md")
    orc_msg = llm_helper.get_roleplay_response("Orchestrator", f"เริ่มโปรเจคใหม่หัวข้อ: {topic}", orc_role, agent_key="orchestrator")
    print_box("👔 ORCHESTRATOR", orc_msg, "36")
    time.sleep(1)

    # 2. Research Agent
    print("\n[SYSTEM] ส่งงานต่อให้ Research Agent...")
    res_role = get_role("01_Research.md")
    res_msg = llm_helper.get_roleplay_response("Research Agent", f"หาข้อมูลพื้นฐานและ Paper ที่เกี่ยวข้องกับ {topic}", res_role, agent_key="research")
    print_box("🎭 ROLEPLAY: 📚 Research Agent", res_msg, "34")
    time.sleep(1)

    # 3. Writer Agent
    print("\n[SYSTEM] ส่งงานต่อให้ Writer Agent...")
    wrt_role = get_role("02_Writer.md")
    wrt_msg = llm_helper.get_roleplay_response("Writer Agent", f"ร่างโครงสร้างบทนำจากข้อมูลที่ Research หามา", wrt_role, agent_key="writer")
    print_box("🎭 ROLEPLAY: ✍️ Writer Agent", wrt_msg, "35")
    
    print("\n" + "="*70)
    print("  ✅ TEST COMPLETE: All agents are responding with Local LLM!")
    print("="*70)

if __name__ == "__main__":
    run_test()
