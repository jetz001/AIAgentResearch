import sys
import os
import builtins
import io

# Mock input sequence
inputs = [
    # 1. User input in main menu
    "รบกวนให้ HR นัดอาจารย์ให้หน่อย จะส่งบทคัดย่อที่เพิ่งจัดรูปแบบให้ QA ตรวจก่อนส่ง",
    
    # 2. Approve plan [Y/E/N]
    "Y",
    
    # 3. Dispatch Task #1 (HR) [Y/N/skip]
    "Y",
    # Inside agent_hr.py it asks for TODO adding -> we just exit early or mock agent?
    # Wait! dispatch_to_agent uses os.system('python script.py "msg"') 
    # It spawns a NEW process. The new process will wait for input on stdin!
]

# We need to automate the subprocess too.
