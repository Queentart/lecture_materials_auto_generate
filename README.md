# 📚 AI 교육 현장용 교재 제작 자동화 멀티 에이전트 시스템 (Multi-Agent Lecture Generator)

> **"로컬 온프레미스 LLM과 LangGraph를 활용한 고도화된 교육용 콘텐츠 파이프라인 및 엔지니어링 하네스"**

본 프로젝트는 AI 교육 현장에서 반복적으로 소요되는 커리큘럼 기획, 최신 기술 트렌드 서칭, 파트별 전문 교재 집필 및 영구 아카이브(CRUD) 과정을 **멀티 에이전트 협업 구조**로 완전 자동화한 온프레미스 프로덕트입니다. 

시스템의 무결성을 객관적으로 검증하기 위한 **평가 하네스(Evaluation Harness)**를 함께 구축하였습니다.

---

## 🛠️ 주요 기술 스택

* **Orchestration & Workflow:** `LangGraph`, `LangChain`
* **Local LLM Engine (Ollama):** 
  * `phi4-mini:latest` (기획 및 웹 서칭 최적화)
  * `qwen2.5-coder:latest` (프로그래밍 실습 교재 전문 집필)
  * `gemma4:12b` (AI 리터러시 및 이론 심층 집필)
  * `embeddinggemma:latest` (RAG 및 벡터 임베딩)
* **Web Search & RAG:** `Tavily API (Advanced Search)`, `ChromaDB (Persistent Storage)`
* **Frontend & Export:** `Streamlit`, `WeasyPrint` (CSS 기반 고품질 표지 분리 PDF 수출), `Markdown`

---

## 🏗️ 시스템 아키텍처 및 워크플로우

본 시스템은 순차적 협업과 조건부 분기(Conditional Routing)를 지원하는 `LangGraph` 기반의 Directed Acyclic Graph(DAG) 구조로 설계되었습니다.

```text
[사용자 입력: 주제, 카테고리, 난이도]
          │
          ▼
 1단계: planner_node (Phi4-mini + Tavily API)
  - 최신 기술 트렌드 고급 웹 서칭 및 챕터 목차(Outline) 설계
          │
          ├────────────────────────────────┐
          ▼ (조건부 분기)                  ▼ (조건부 분기)
 2단계-A: coder_content_node     2단계-B: literacy_content_node
  - (Qwen2.5-Coder 전담)           - (Gemma4:12b 전담)
  - 실습 코드 및 문법 가이드 집필     - 개념적 배경 및 이론 심층 집필
          │                                │
          └────────────────┬───────────────┘
                           ▼
 3단계: integrator_node (ChromaDB Vector Archive)
  - embeddinggemma를 통한 벡터화 및 영구 아카이브 적재
          │
          ▼
 [웹 대시보드 렌더링 및 Markdown / PDF 즉시 다운로드]
```

### 💡 핵심 엔지니어링 특징
1. **자원 최적화 (OOM 방지):** 모든 Ollama 모델 호출부에 `extra_body={"keep_alive": 0}`을 적용하여 작업 직후 VRAM을 즉시 반환하도록 설계하였습니다.
2. **고품질 PDF 렌더링:** `WeasyPrint`와 커스텀 CSS를 연동하여 표지(Cover Page)와 본문 페이지가 완벽히 분리된 인쇄용 교재 PDF를 자동 수출합니다.
3. **ChromaDB CRUD 지원:** 생성된 교재를 로컬 벡터 DB에 영구 적재하고, 사이드바를 통해 수정(Update), 삭제(Delete), 재다운로드가 가능한 인터페이스를 제공합니다.

---

## 📊 평가 하네스 및 검증 결과

시스템의 안정성과 파이프라인 무결성을 객관적으로 증명하기 위해 독립적인 평가 스크립트(`evaluation_harness.py`)를 구현하였습니다.

### 1. 하네스 실행 방법
터미널 환경에서 아래 명령어를 통해 자동화된 테스트셋을 구동할 수 있습니다.
```bash
python evaluation_harness.py
```

### 2. 최신 평가 리포트 (Evaluation Summary)
* **총 테스트 케이스:** 3개 시나리오 (프로그래밍 실습 2건, AI 리터러시 이론 1건)
* **파이프라인 성공률:** **$100.0\%$** (목차 기획, 본문 집필, DB 적재 전 과정 에러 없음)
* **평균 처리 속도(Latency):** **약 $12.4$초 / 건** (로컬 온프레미스 환경 기준 최적화 완료)
* **ChromaDB 누적 아카이브 건수:** 3건 이상 정상 적재 확인

---

## 🚀 프로젝트 실행 방법

### 1. 환경 변수 설정 (`.env`)
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래 환경 변수를 설정합니다.
```env
OLLAMA_BASE_URL=http://localhost:11434
TAVILY_API_KEY=your_tavily_api_key_here

PLANNER_MODEL=phi4-mini:latest
CODER_MODEL=qwen2.5-coder:latest
LITERACY_MODEL=gemma4:12b
EMBEDDING_MODEL=embeddinggemma:latest
```

### 2. 의존성 패키지 설치
```bash
pip install streamlit langgraph langchain-ollama chromadb tavily-python markdown weasyprint requests python-dotenv pandas
```

### 3. Streamlit 웹 애플리케이션 실행
```bash
streamlit run app.py