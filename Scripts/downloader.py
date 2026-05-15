import os
import sys
import requests
from urllib.parse import urlparse

def download_file(url, target_folder="References"):
    """ดาวน์โหลดไฟล์จาก URL ลงในโฟลเดอร์ที่กำหนด"""
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        
    try:
        # แยกชื่อไฟล์จาก URL
        a = urlparse(url)
        filename = os.path.basename(a.path)
        if not filename:
            filename = "downloaded_file.pdf" # Default
            
        target_path = os.path.join(target_folder, filename)
        
        print(f"[*] Downloading: {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print(f"✅ Downloaded successfully: {target_path}")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url_to_load = sys.argv[1]
        download_file(url_to_load)
    else:
        print("Usage: python downloader.py <URL>")
