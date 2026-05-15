import markdown
import os

def create_html_thesis(md_path, html_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    
    # Convert MD to HTML
    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    
    # Add styling for Thai and Academic look
    html_content = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap');
            body {{
                font-family: 'Sarabun', sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px;
                text-align: justify;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
                text-align: center;
                margin-top: 40px;
            }}
            img {{
                max-width: 100%;
                height: auto;
                display: block;
                margin: 20px auto;
                border: 1px solid #ddd;
                border-radius: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .page-break {{
                page-break-after: always;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[*] HTML Thesis created: {html_path}")

if __name__ == "__main__":
    import sys
    in_md = sys.argv[1] if len(sys.argv) > 1 else "Output/thesis/Full_Thesis_Draft.md"
    out_html = sys.argv[2] if len(sys.argv) > 2 else "Output/thesis/Full_Thesis_Complete.html"
    create_html_thesis(in_md, out_html)
