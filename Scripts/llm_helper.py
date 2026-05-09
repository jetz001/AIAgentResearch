import os
import requests
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env():
    # ตรวจสอบทั้งที่ root และในโฟลเดอร์ Config
    paths = [
        os.path.join(PROJECT_ROOT, ".env"),
        os.path.join(PROJECT_ROOT, "Config", ".env")
    ]
    for env_path in paths:
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()

load_env()

# --- Configuration ---
# สามารถปรับเปลี่ยนผ่าน Environment Variables ได้
DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower() # ollama, openai, gemini, groq

# Ollama Settings
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma")

# Online API Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

def call_ollama(prompt: str, system_prompt: str = "") -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=300)
    response.raise_for_status()
    return response.json().get("response", "")

def call_openai_compatible(prompt: str, system_prompt: str, api_key: str, model: str, url: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def call_gemini(prompt: str, system_prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": f"SYSTEM: {system_prompt}\n\nUSER: {prompt}"}]
        }]
    }
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

def call_llm(prompt: str, system_prompt: str = "", provider: str = None) -> str:
    """
    เรียกใช้ LLM ตาม Provider ที่เลือก
    """
    provider = provider or DEFAULT_PROVIDER
    
    try:
        if provider == "ollama":
            return call_ollama(prompt, system_prompt)
        
        elif provider == "openai":
            if not OPENAI_API_KEY: return "❌ Missing OPENAI_API_KEY"
            return call_openai_compatible(prompt, system_prompt, OPENAI_API_KEY, OPENAI_MODEL, "https://api.openai.com/v1/chat/completions")
            
        elif provider == "groq":
            if not GROQ_API_KEY: return "❌ Missing GROQ_API_KEY"
            return call_openai_compatible(prompt, system_prompt, GROQ_API_KEY, GROQ_MODEL, "https://api.groq.com/openai/v1/chat/completions")
            
        elif provider == "gemini":
            if not GEMINI_API_KEY: return "❌ Missing GEMINI_API_KEY"
            return call_gemini(prompt, system_prompt)
            
        else:
            return f"❌ Unknown Provider: {provider}"
            
    except Exception as e:
        return f"⚠️ LLM Error ({provider}): {str(e)}"

def get_roleplay_response(agent_name_display: str, task_description: str, role_content: str, agent_key: str = None) -> str:
    """
    ขอการโต้ตอบแบบ Roleplay จาก LLM ตามบทบาทของ Agent
    - agent_key: คีย์ของ agent เช่น 'research', 'writer', 'orchestrator'
    """
    # 1. ตรวจสอบว่าเอเจ้นท์ตัวนี้มี Provider เฉพาะหรือไม่ (เช่น RESEARCH_PROVIDER)
    provider = None
    if agent_key:
        env_key = f"{agent_key.upper()}_PROVIDER"
        provider = os.getenv(env_key)
    
    # ถ้าไม่มี ให้ใช้ DEFAULT_PROVIDER
    provider = provider or DEFAULT_PROVIDER
    
    system_prompt = f"""
คุณคือ {agent_name_display} หนึ่งในทีม Multi-Agent Research System.
นี่คือรายละเอียดบทบาทของคุณ (Role Definition):
{role_content}

คำสั่ง: ให้คุณสวมบทบาท (Roleplay) ตอบกลับผู้บริหารที่เพิ่งมอบหมายงานให้คุณ
- ใช้ภาษาทางการแต่มีความเป็นกันเองในทีม
- แสดงความกระตือรือร้นและระบุขั้นตอนเบื้องต้นที่คุณจะทำ
- ตอบเป็นภาษาไทย
- ความยาวประมาณ 2-4 ประโยค
"""
    
    user_prompt = f"ผู้บริหารมอบหมายงานให้คุณดังนี้: {task_description}\n\nกรุณาตอบกลับในฐานะ {agent_name_display}:"
    
    return call_llm(user_prompt, system_prompt, provider=provider)

def get_thinking_response(agent_name_display: str, task_description: str, role_content: str, agent_key: str = None) -> str:
    """
    ขอการวิเคราะห์ (Thinking) ก่อนเริ่มทำงาน
    """
    provider = None
    if agent_key:
        provider = os.getenv(f"{agent_key.upper()}_PROVIDER")
    provider = provider or DEFAULT_PROVIDER
    
    system_prompt = f"""
คุณคือ {agent_name_display} ทีม Multi-Agent Research System.
นี่คือรายละเอียดบทบาทของคุณ:
{role_content}

คำสั่ง: ให้คุณ "คิด" (Thinking) เกี่ยวกับงานที่ได้รับ
- วิเคราะห์ว่าต้องใช้ Skill ไหน
- วางแผนขั้นตอน 1, 2, 3
- ระบุความเสี่ยงหรือสิ่งที่ต้องระวัง
- ตอบเป็นภาษาไทย
- ความยาวปานกลาง (เน้นเนื้อหาการวางแผน)
"""
    user_prompt = f"งานที่คุณได้รับ: {task_description}\n\nกรุณาแสดงกระบวนการคิด (Thinking Process):"
    return call_llm(user_prompt, system_prompt, provider=provider)

def get_report_response(agent_name_display: str, work_details: str, role_content: str, agent_key: str = None) -> str:
    """
    ขอสรุปรายงานผลการทำงาน (Report) เพื่อส่งให้ผู้บริหาร
    """
    provider = None
    if agent_key:
        provider = os.getenv(f"{agent_key.upper()}_PROVIDER")
    provider = provider or DEFAULT_PROVIDER
    
    system_prompt = f"""
คุณคือ {agent_name_display} ทีม Multi-Agent Research System.
นี่คือรายละเอียดบทบาทของคุณ:
{role_content}

คำสั่ง: สรุปรายงานผลการทำงาน (Executive Summary Report) เพื่อส่งให้ Orchestrator (ผู้บริหาร)
- ส่วนที่ 1: วัตถุประสงค์ (Objective) และสรุปกระบวนการคิด (Thinking Process) ของทีม
- ส่วนที่ 2: ลำดับขั้นตอนการทำงาน (Plan Flow) และผลการดำเนินการของแต่ละ Agent
- ส่วนที่ 3: ผลลัพธ์สุดท้ายที่ได้ (Final Output) - ต้องสอดคล้องกับคำสั่งเริ่มต้น
- ส่วนที่ 4: ข้อสังเกตและข้อเสนอแนะ
- รูปแบบ: ใช้ Markdown ที่สวยงาม, เป็นทางการ, แบ่งหัวข้อชัดเจน
- ตอบเป็นภาษาไทย
"""
    user_prompt = f"รายละเอียดงานที่ทำเสร็จ: {work_details}\n\nกรุณาสร้างรายงานสรุป (Report):"
    return call_llm(user_prompt, system_prompt, provider=provider)

def get_expanded_instruction(user_message: str, agent_name: str, keywords: str) -> str:
    """
    ขยายความคำสั่งจาก User ให้เป็นคำสั่งที่ละเอียดและเป็นมืออาชีพสำหรับ Agent รายตัว
    """
    system_prompt = """
คุณคือ Orchestrator (ผู้บริหาร) ของทีม AI Research.
หน้าที่ของคุณคือรับคำสั่งจาก User และขยายความให้เป็น "คำสั่งที่ชัดเจนและมีเป้าหมาย" สำหรับลูกน้อง (Agent)

กฎการขยายความ:
1. รักษาความต้องการหลักของ User ไว้ครบถ้วน
2. อธิบายรายละเอียดว่าต้องการให้ Agent ทำอะไร (เช่น ค้นหาจากที่ไหน, สรุปเน้นประเด็นอะไร)
3. ใช้ภาษาที่เป็นทางการและเป็นมืออาชีพในฐานะผู้บริหาร
4. ตอบเป็นภาษาไทย
5. สั้นแต่ได้ใจความ (1-2 ประโยคที่ชัดเจน)
"""
    user_prompt = f"ข้อความจาก User: {user_message}\nAgent ที่รับงาน: {agent_name}\nKeyword สำคัญ: {keywords}\n\nกรุณาเขียนคำสั่งขยายความให้ลูกน้อง:"
    return call_llm(user_prompt, system_prompt)
