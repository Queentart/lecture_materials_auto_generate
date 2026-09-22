# -*- coding: utf-8 -*-
import os
import requests
from dotenv import load_dotenv
import markdown
from weasyprint import HTML

load_dotenv()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def check_ollama_health() -> tuple[bool, str]:
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/", timeout=3)
        if response.status_code == 200:
            return True, f"Ollama 로컬 서버 연결됨 ({OLLAMA_BASE_URL})"
        else:
            return False, f"서버 응답 비정상 (Status Code: {response.status_code})"
    except requests.exceptions.ConnectionError:
        return False, "Ollama 로컬 서버와 연결할 수 없습니다."
    except Exception as e:
        return False, f"헬스체크 중 에러 발생: {str(e)}"

def format_markdown_export(title: str, category: str, level: str, content: str) -> bytes:
    markdown_text = f"""# 📚 [교재] {title}

- **카테고리:** {category}
- **타겟 난이도:** {level}

---

{content}
"""
    return markdown_text.encode('utf-8-sig')

def generate_pdf_export(title: str, category: str, level: str, content: str) -> bytes:
    """
    Markdown과 WeasyPrint를 조합하여 전문적인 표지 페이지(Cover Page)가 분리된 고품질 PDF를 생성합니다.
    """
    # 💡 1페이지(표지 전용 섹션)와 2페이지 이후(본문 섹션)를 HTML 수준에서 명확히 분리
    html_body = markdown.markdown(content, extensions=['fenced_code', 'tables'])
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @font-face {{
                font-family: 'Malgun Gothic';
                src: local('Malgun Gothic');
            }}
            body {{
                font-family: 'Malgun Gothic', sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #2c3e50;
            }}
            /* 표지(Cover Page) 스타일 설정 */
            .cover-page {{
                page-break-after: always;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                padding-top: 150px;
            }}
            .cover-title {{
                font-size: 26pt;
                font-weight: bold;
                color: #1a252f;
                margin-bottom: 20px;
                line-height: 1.3;
            }}
            .cover-meta {{
                font-size: 13pt;
                color: #7f8c8d;
                margin-bottom: 40px;
            }}
            .cover-badge {{
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border-radius: 20px;
                font-size: 11pt;
                font-weight: bold;
            }}
            /* 본문 페이지 스타일 설정 */
            .content-page {{
                padding: 20px;
            }}
            h1, h2, h3 {{
                color: #2980b9;
                margin-top: 25px;
            }}
            code {{
                background-color: #f8f9fa;
                color: #e74c3c;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 10pt;
            }}
            pre {{
                background-color: #f1f2f6;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #dcdde1;
                overflow-x: auto;
            }}
            pre code {{
                color: #2f3640;
                background-color: transparent;
                padding: 0;
            }}
            hr {{
                border: none;
                border-top: 1px solid #bdc3c7;
                margin: 20px 0;
            }}
            ul, ol {{
                padding-left: 20px;
            }}
        </style>
    </head>
    <body>
        <!-- 독립된 표지 페이지 -->
        <div class="cover-page">
            <div class="cover-badge">AI 교육 현장용 공식 교재</div>
            <div class="cover-title" style="margin-top: 30px;">{title}</div>
            <div class="cover-meta">
                카테고리: {category}<br>
                타겟 난이도: {level}
            </div>
            <hr style="width: 100px; border-top: 3px solid #3498db; margin: 0 auto;">
        </div>

        <!-- 2페이지부터 시작되는 본문 페이지 -->
        <div class="content-page">
            {html_body}
        </div>
    </body>
    </html>
    """
    
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes