import os
import sys
import io
import glob
from typing import List, Dict
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
try:
    from gpt4all import Embed4All
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False

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
        if CHROMA_AVAILABLE:
            self.client = chromadb.PersistentClient(path=DB_DIR)
            self.collection = self.client.get_or_create_collection(
                name="research_papers",
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.client = None
            self.collection = None
            
        if GPT4ALL_AVAILABLE:
            self.embedder = Embed4All()
        else:
            self.embedder = None

    def extract_text(self, file_path: str) -> str:
        """สกัดข้อความจากไฟล์ .txt หรือ .pdf"""
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        try:
            if ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            elif ext == ".pdf":
                if PYPDF_AVAILABLE:
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                else:
                    text = f"(PDF reader not available for {file_path})"
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
        if not CHROMA_AVAILABLE or not GPT4ALL_AVAILABLE:
            print("⚠️ Indexing skipped: Dependencies missing.")
            return

        files = glob.glob(os.path.join(REFS_DIR, "*.*"))
        # ... rest of the code ...
        print("✅ Indexing complete.")

    def search(self, query: str, n_results: int = 3) -> str:
        """ค้นหาข้อมูลที่เกี่ยวข้อง"""
        if not CHROMA_AVAILABLE or not GPT4ALL_AVAILABLE:
            # Fallback: Simple string search in files
            context = ""
            files = glob.glob(os.path.join(REFS_DIR, "*.txt"))
            for f in files[:2]:
                with open(f, "r", encoding="utf-8") as file:
                    context += file.read()[:500] + "\n---\n"
            return context

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
