
import os
import sys
import io
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "Scripts"))
import llm_helper

# ── Fix Windows encoding ──
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def test_ollama():
    print("🤖 Testing Ollama connectivity with Gemma2:2b...")
    try:
        response = llm_helper.get_roleplay_response("TestAgent", "สวัสดีครับ ทดสอบระบบ", "You are a helpful assistant.", agent_key="orchestrator")
        print("\n✅ Ollama Responded:")
        print("-" * 30)
        print(response)
        print("-" * 30)
    except Exception as e:
        print(f"\n❌ Error connecting to Ollama: {e}")

if __name__ == "__main__":
    test_ollama()
