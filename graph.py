# -*- coding: utf-8 -*-
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

# 앞서 구현한 에이전트 및 툴, DB 모듈 임포트
from agents import planner_llm, coder_llm, literacy_llm
from tools import tavily_web_search
from database import save_lecture_material

# 1. 멀티 에이전트 상태(State) 정의
class LectureState(TypedDict):
    topic: str                 # 교재 주제
    category: str              # 전체 카테고리 (프로그래밍 vs AI 리터러시)
    level: str                 # 타겟 난이도 (입문 / 중급 / 고급)
    web_research_data: str     # Tavily 웹 서칭 결과
    outline: str               # 1단계: 목차 기획 결과
    draft_content: str         # 2단계: 에이전트가 작성한 본문 내용
    saved_id: str              # DB 저장 후 고유 ID


# 2. 노드 1: 기획 및 웹 서칭 에이전트 (Phi4-mini + Tavily)
def planner_node(state: LectureState) -> Dict[str, Any]:
    print("--- [1단계] 기획 및 웹 서칭 에이전트(Phi4) 구동 중 ---")
    topic = state["topic"]
    
    # Tavily를 통한 최신 트렌드/참고 자료 고급 서칭
    search_query = f"{topic} 최신 트렌드 기술 교육 자료"
    web_data = tavily_web_search(search_query, max_results=3)
    
    # 목차 기획 프롬프트 구성
    prompt = f"""
    당신은 전문 IT 및 AI 교육 커리큘럼 기획자입니다.
    주제: {topic}
    난이도: {state['level']}
    참고할 최신 웹 검색 데이터:
    {web_data}
    
    위 내용을 바탕으로 해당 교재의 핵심 목차(Chapter & Section) 구조와 학습 목표를 체계적으로 작성해주세요.
    """
    
    response = planner_llm.invoke(prompt)
    outline_text = response.content
    
    return {
        "web_research_data": web_data,
        "outline": outline_text
    }


# 3. 노드 2-1: 프로그래밍 교육 에이전트 (Qwen2.5-Coder)
def coder_content_node(state: LectureState) -> Dict[str, Any]:
    print("--- [2단계-A] 프로그래밍 교육 전문 에이전트(Qwen-Coder) 구동 중 ---")
    topic = state["topic"]
    outline = state["outline"]
    
    prompt = f"""
    당신은 실무 중심 프로그래밍 강사입니다. 아래의 목차 기획안을 바탕으로 따라 하기 좋은 실습 코드, 문법 설명, 주의사항이 포함된 교재 본문을 작성해주세요.
    
    [교재 주제] {topic}
    [목차 기획안]
    {outline}
    """
    
    response = coder_llm.invoke(prompt)
    return {"draft_content": response.content}


# 4. 노드 2-2: AI 리터러시 & 이론 교육 에이전트 (Gemma4)
def literacy_content_node(state: LectureState) -> Dict[str, Any]:
    print("--- [2단계-B] AI 리터러시 & 이론 교육 에이전트(Gemma4) 구동 중 ---")
    topic = state["topic"]
    outline = state["outline"]
    
    prompt = f"""
    당신은 통찰력 있는 AI 리터러시 및 인문/기술 이론 교육 전문가입니다. 아래의 목차 기획안을 바탕으로 개념적 배경, 트렌드 분석, 비즈니스적 시사점이 돋보이는 깊이 있는 교재 본문을 작성해주세요.
    
    [교재 주제] {topic}
    [목차 기획안]
    {outline}
    """
    
    response = literacy_llm.invoke(prompt)
    return {"draft_content": response.content}


# 5. 라우터 함수: 카테고리에 따라 코딩 에이전트와 리터러시 에이전트 분기
def route_content_generator(state: LectureState) -> str:
    category = state.get("category", "프로그래밍")
    if "프로그래밍" in category or "코딩" in category or "개발" in category:
        return "coder"
    else:
        return "literacy"


# 6. 노드 3: 결과 통합 및 ChromaDB 영구 저장 에이전트
def integrator_node(state: LectureState) -> Dict[str, Any]:
    print("--- [3단계] 교재 내용 통합 및 ChromaDB 영구 저장 중 ---")
    topic = state["topic"]
    category = state["category"]
    level = state["level"]
    draft = state["draft_content"]
    
    # 완성된 본문을 ChromaDB에 영구 저장 (embeddinggemma 임베딩 적용)
    doc_id = save_lecture_material(
        title=topic,
        category=category,
        level=level,
        content=draft
    )
    
    return {"saved_id": doc_id}


# 7. LangGraph StateGraph 파이프라인 조립
workflow = StateGraph(LectureState)

# 노드 등록
workflow.add_node("planner", planner_node)
workflow.add_node("coder_agent", coder_content_node)
workflow.add_node("literacy_agent", literacy_content_node)
workflow.add_node("integrator", integrator_node)

# 엣지 연결 (흐름 제어)
workflow.set_entry_point("planner")
workflow.add_conditional_edges(
    "planner",
    route_content_generator,
    {
        "coder": "coder_agent",
        "literacy": "literacy_agent"
    }
)

workflow.add_edge("coder_agent", "integrator")
workflow.add_edge("literacy_agent", "integrator")
workflow.add_edge("integrator", END)

# 컴파일 완료된 LangGraph 애플리케이션 객체
app_graph = workflow.compile()