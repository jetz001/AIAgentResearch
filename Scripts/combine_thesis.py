import os

def combine_markdowns(output_path):
    files = [
        "Output/thesis/chapter1_draft.md",
        "Output/thesis/chapter2_draft.md",
        "Output/thesis/chapter3_draft.md",
        "Output/thesis/chapter4_draft.md",
        "Output/thesis/chapter5_draft.md",
        "Output/thesis/chapterappendix_draft.md"
    ]
    
    combined_content = "# วิทยานิพนธ์ฉบับสมบูรณ์\n\n## การประเมินคาร์บอนฟุตพริ้นท์ของอุตสาหกรรมกล่องกระดาษลูกฟูก\n\n---\n\n"
    
    for f_path in files:
        if os.path.exists(f_path):
            with open(f_path, "r", encoding="utf-8") as f:
                content = f.read()
                combined_content += content + "\n\n<p style='page-break-after: always;'></p>\n\n"
        else:
            print(f"⚠️ Warning: File not found {f_path}")
            
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(combined_content)
    print(f"[*] Combined all chapters into: {output_path}")

if __name__ == "__main__":
    combine_markdowns("Output/thesis/Full_Thesis_Draft.md")
