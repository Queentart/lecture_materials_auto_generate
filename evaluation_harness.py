# -*- coding: utf-8 -*-
import time
from graph import app_graph
from database import get_all_materials

# 1. 교재 제작 테스트용 데이터셋 (프로그래밍 실습 및 AI 리터러시 시나리오)
TEST_DATASET = [
    {
        "id": "LECTURE-01",
        "topic": "Docker 컨테이너 기반 LangGraph 멀티 에이전트 구축 실습",
        "category": "프로그래밍 실습 (Qwen-Coder 전담)",
        "level": "중급 (Intermediate)"
    },
    {
        "id": "LECTURE-02",
        "topic": "생성형 AI 시대의 저작권 이슈와 오픈소스 라이선스 이해",
        "category": "AI 리터러시 및 이론 (Gemma4 전담)",
        "level": "입문 (Beginner)"
    },
    {
        "id": "LECTURE-03",
        "topic": "FastAPI와 ChromaDB를 활용한 RAG 백엔드 파이프라인 구현",
        "category": "프로그래밍 실습 (Qwen-Coder 전담)",
        "level": "고급 (Advanced)"
    }
]

def run_evaluation():
    print("=" * 65)
    print("🚀 교재 제작 자동화 멀티 에이전트 시스템 평가 하네스(Evaluation Harness)")
    print("=" * 65)
    
    total_tests = len(TEST_DATASET)
    success_count = 0
    total_latency = 0.0

    for idx, test_case in enumerate(TEST_DATASET, 1):
        test_id = test_case["id"]
        topic = test_case["topic"]
        category = test_case["category"]
        level = test_case["level"]

        print(f"\n[테스트 {idx}/{total_tests}] ID: {test_id}")
        print(f"주제: {topic}")
        print(f"카테고리: {category} | 난이도: {level}")
        
        # 초기 상태 정의
        initial_state = {
            "topic": topic,
            "category": category,
            "level": level,
            "web_research_data": "",
            "outline": "",
            "draft_content": "",
            "saved_id": ""
        }
        
        start_time = time.time()
        
        try:
            # LangGraph 파이프라인 실행
            result = app_graph.invoke(initial_state)
            
            elapsed_time = time.time() - start_time
            total_latency += elapsed_time
            
            outline = result.get("outline", "")
            draft = result.get("draft_content", "")
            saved_id = result.get("saved_id", "")
            
            print(f"⏱️ 처리 소요 시간: {elapsed_time:.2f}초")
            print(f"📌 목차 기획 생성 여부: {'성공' if len(outline) > 50 else '실패'} (글자수: {len(outline)})")
            print(f"📝 본문 집필 완료 여부: {'성공' if len(draft) > 100 else '실패'} (글자수: {len(draft)})")
            print(f"💾 ChromaDB 영구 저장 ID: {saved_id if saved_id else '저장 실패'}바이")
            
            # 검증 조건: 목차, 본문, 저장 ID가 모두 정상 존재할 경우 성공
            if len(outline) > 50 and len(draft) > 100 and saved_id:
                success_count += 1
                print(f"✅ [TEST {test_id}] 결과: PASSED")
            else:
                print(f"❌ [TEST {test_id}] 결과: FAILED (출력 결과 미흡)")
                
        except Exception as e:
            print(f"❌ [TEST {test_id}] 에러 발생: {str(e)}")

    # 최종 DB 저장 건수 확인
    db_data = get_all_materials()
    db_count = len(db_data.get('ids', []))

    print("\n" + "=" * 65)
    print("📊 최종 교재 자동화 시스템 평가 리포트 (Evaluation Summary)")
    print("=" * 65)
    print(f"- 총 테스트 케이스: {total_tests}개")
    print(f"- 파이프라인 성공률: {(success_count / total_tests) * 100:.1f}%")
    print(f"- 평균 처리 속도(Latency): {total_latency / total_tests:.2f}초 / 건")
    print(f"- ChromaDB 누적 아카이브 건수: {db_count}건")
    print("=" * 65)
    print("💡 이 하네스 결과는 로컬 LLM 에이전트의 안정성과 RAG 파이프라인 무결성 증빙 자료로 활용됩니다.")

if __name__ == "__main__":
    run_evaluation()