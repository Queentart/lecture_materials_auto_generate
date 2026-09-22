# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

# 환경 변수 로드 (.env 파일에서 모델명 및 엔드포인트 가져오기)
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# .env에 선언된 환경변수명으로부터 모델 이름을 가져옴
PLANNER_MODEL = os.getenv("PLANNER_MODEL", "phi4-mini:latest")
CODER_MODEL = os.getenv("CODER_MODEL", "qwen2.5-coder:latest")
LITERACY_MODEL = os.getenv("LITERACY_MODEL", "gemma4:12b")

# 1. [기획 및 웹 서칭 에이전트] 전체 목차 설계 및 Tavily 검색 결과 요약
planner_llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=PLANNER_MODEL,
    temperature=0.3,
    extra_body={"keep_alive": 0}  # 작업 직후 VRAM 즉시 반환
)

# 2. [프로그래밍 교육 에이전트] 파이썬, 도커, 실습 코드 및 기술 문서 작성 특화
coder_llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=CODER_MODEL,
    temperature=0.2,
    extra_body={"keep_alive": 0}  # 작업 직후 VRAM 즉시 반환
)

# 3. [AI 리터러시 & 이론 교육 에이전트] 개념적 심층 설명 메인 모델
literacy_llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=LITERACY_MODEL,
    temperature=0.4,
    extra_body={"keep_alive": 0}  # 작업 직후 VRAM 즉시 반환
)