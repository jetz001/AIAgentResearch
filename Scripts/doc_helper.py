import os
import sys
import io
import glob
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from pypdf import PdfReader
from gpt4all import Embed4All

# ── Fix Windows encoding ──
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS_DIR = os.path.join(PROJECT_ROOT, "References")
DB_DIR = os.path.join(PROJECT_ROOT, "Memory", "VectorDB")

os.makedirs(DB_DIR, exist_ok=True)

class DocHelper:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_DIR)
        self.embedder = Embed4All()
        self.collection = self.client.get_or_create_collection(
            name="research_papers",
            metadata={"hnsw:space": "cosine"}
        )

    def extract_text(self, file_path: str) -> str:
        """สกัดข้อความจากไฟล์ .txt หรือ .pdf"""
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        try:
            if ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            elif ext == ".pdf":
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"⚠️ Error extracting {file_path}: {e}")
        return text

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """แบ่งข้อความเป็นก้อนเล็กๆ"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def index_references(self):
        """Index ไฟล์ทั้งหมดในโฟลเดอร์ References"""
        files = glob.glob(os.path.join(REFS_DIR, "*.*"))
        print(f"[*] Found {len(files)} files in References/")
        
        for file_path in files:
            file_name = os.path.basename(file_path)
            # ตรวจสอบว่าเคย index หรือยัง (ใช้ metadata หรือ id)
            # เพื่อความง่าย รอบนี้จะลบแล้วสร้างใหม่ หรือเพิ่มเฉพาะที่ยังไม่มี
            text = self.extract_text(file_path)
            if not text:
                continue
            
            chunks = self.chunk_text(text)
            print(f"[-] Indexing {file_name} ({len(chunks)} chunks)...")
            
            ids = [f"{file_name}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": file_name, "chunk": i} for i in range(len(chunks))]
            
            # GPT4All Embeddings
            embeddings = [self.embedder.embed(chunk) for chunk in chunks]
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )
        print("✅ Indexing complete.")

    def search(self, query: str, n_results: int = 3) -> str:
        """ค้นหาข้อมูลที่เกี่ยวข้อง"""
        query_embedding = self.embedder.embed(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # รวมผลลัพธ์เป็นเนื้อหาเดียว
        context = ""
        if results and results['documents']:
            for doc in results['documents'][0]:
                context += doc + "\n---\n"
        return context

if __name__ == "__main__":
    # Test
    helper = DocHelper()
    helper.index_references()
    res = helper.search("MFCA คืออะไร?")
    print("\n[Search Result]:")
    print(res)
