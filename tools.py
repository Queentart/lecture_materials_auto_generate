# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from tavily import TavilyClient

# 환경 변수 로드
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Tavily 클라이언트 초기화
tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

def tavily_web_search(query: str, max_results: int = 3) -> str:
    """
    Tavily API를 사용하여 최신 기술 트렌드 및 참고 자료를 고급 검색(advanced search_depth)합니다.
    교재 제작 시 정확하고 신뢰성 높은 최신 정보를 수집하는 데 활용됩니다.
    """
    if not tavily_client:
        return "⚠️ Tavily API 키가 설정되지 않았습니다. .env 파일을 확인해주세요."
    
    try:
        # 💡 search_depth="advanced"를 명시하여 깊이 있는 고품질 웹 서칭 보장
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
        
        results = response.get("results", [])
        formatted_results = []
        
        for r in results:
            title = r.get("title", "제목 없음")
            url = r.get("url", "URL 없음")
            content = r.get("content", "내용 없음")
            formatted_results.append(f"📌 제목: {title}\n🔗 출처: {url}\n📝 내용: {content}\n")
            
        return "\n---\n".join(formatted_results) if formatted_results else "검색된 웹 결과가 없습니다."
        
    except Exception as e:
        return f"❌ Tavily 웹 서칭 중 오류 발생: {str(e)}"