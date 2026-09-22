# -*- coding: utf-8 -*-
import time
import pandas as pd
import streamlit as st

from graph import app_graph
from database import (
    get_all_materials, 
    update_material, 
    delete_material
)
from utils import check_ollama_health, format_markdown_export, generate_pdf_export

# 1. 페이지 설정
st.set_page_config(
    page_title="교재 제작 자동화 멀티 에이전트 시스템",
    page_icon="📚",
    layout="wide"
)

# 💡 세션 상태 초기화 (생성된 결과가 화면에서 사라지는 현상 방지)
if "generated_content" not in st.session_state:
    st.session_state.generated_content = None
if "generated_title" not in st.session_state:
    st.session_state.generated_title = ""
if "generated_category" not in st.session_state:
    st.session_state.generated_category = ""
if "generated_level" not in st.session_state:
    st.session_state.generated_level = ""

# 2. 메인 타이틀 및 소개
st.title("📚 AI 교육 현장용 교재 제작 자동화 시스템")
st.markdown("""
최신 웹 서칭(Tavily API)과 분야별 전문 로컬 에이전트(`qwen2.5-coder`, `gemma4:12b`, `phi4-mini`)를 연동하여, 
프로그래밍 실습 교재부터 AI 리터러시 이론서까지 자동으로 기획하고 작성하는 **LangGraph 기반 온프레미스 프로덕트**입니다.
""")

st.divider()

# 💡 [사이드바 구성] 시스템 헬스체크 및 ChromaDB 로컬 아카이브 (CRUD + 재다운로드)
with st.sidebar:
    st.subheader("🔌 시스템 상태 점검")
    is_alive, msg = check_ollama_health()
    
    if is_alive:
        st.success(f"🟢 {msg}")
    else:
        st.error(f"🔴 {msg}")
        st.warning("⚠️ 백그라운드에서 Ollama 앱을 실행해 주세요!")
        
    st.divider()
    
    st.subheader("📂 제작된 교재 아카이브 (CRUD)")
    st.markdown("벡터 DB에 영구 저장된 교재 및 챕터를 관리하고 수정·삭제·재다운로드할 수 있습니다.")
    
    db_data = get_all_materials()
    ids = db_data.get('ids', [])
    
    if ids and len(ids) > 0:
        st.metric("누적 교재 아카이브", f"{len(ids)}건")
        
        metas = db_data.get('metadatas', [])
        docs = db_data.get('documents', [])
        
        df_history = pd.DataFrame(metas)
        df_history['id'] = ids
        df_history['content'] = docs
        
        # 전체 목록 미리보기 표
        st.dataframe(df_history[['timestamp', 'category', 'title', 'level']], height=200)
        
        st.divider()
        st.markdown("#### ⚙️ 개별 교재 관리 (수정/삭제/재다운로드)")
        
        selected_id = st.selectbox(
            "관리할 교재 선택 (고유 ID)", 
            options=df_history['id'].tolist()
        )
        
        if selected_id:
            target_row = df_history[df_history['id'] == selected_id].iloc[0]
            
            with st.expander("📝 선택된 교재 상세 관리"):
                edit_title = st.text_input("주제/제목 수정", value=target_row['title'], key=f"title_{selected_id}")
                edit_category = st.selectbox("카테고리 수정", ["프로그래밍 실습", "AI 리터러시 및 이론"], index=0 if "프로그래밍" in target_row['category'] else 1, key=f"cat_{selected_id}")
                edit_level = st.selectbox("난이도 수정", ["입문 (Beginner)", "중급 (Intermediate)", "고급 (Advanced)"], key=f"lvl_{selected_id}")
                edit_content = st.text_area("본문 내용 수정", value=target_row['content'], height=200, key=f"cont_{selected_id}")
                
                col_u, col_d = st.columns(2)
                with col_u:
                    if st.button("💾 변경 저장", use_container_width=True):
                        update_material(
                            doc_id=selected_id,
                            title=edit_title,
                            category=edit_category,
                            level=edit_level,
                            content=edit_content
                        )
                        st.success("수정 완료!")
                        st.rerun()
                        
                with col_d:
                    if st.button("🗑️ 교재 삭제", type="primary", use_container_width=True):
                        delete_material(selected_id)
                        st.warning("삭제되었습니다.")
                        st.rerun()
                
                st.divider()
                st.markdown("##### 📥 아카이브 파일 즉시 재다운로드")
                
                # 아카이브 항목 개별 마크다운 재다운로드 버튼
                hist_md = format_markdown_export(target_row['title'], target_row['category'], target_row['level'], target_row['content'])
                st.download_button(
                    label="📄 마크다운(.md) 재다운로드",
                    data=hist_md,
                    file_name=f"archive_{selected_id}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key=f"dl_md_{selected_id}"
                )
                
                # 아카이브 항목 개별 PDF 재다운로드 버튼
                hist_pdf = generate_pdf_export(target_row['title'], target_row['category'], target_row['level'], target_row['content'])
                st.download_button(
                    label="📕 PDF 문서 재다운로드",
                    data=hist_pdf,
                    file_name=f"archive_{selected_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"dl_pdf_{selected_id}"
                )
    else:
        st.info("아직 저장된 교재 아카이브가 없습니다. 새로운 교재를 생성해 보세요!")

# 3. 레이아웃 구성 (좌측: 입력 / 우측: 결과 및 렌더링)
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📥 교재 제작 요청서 입력")
    
    topic_input = st.text_input(
        "교재 주제 또는 핵심 학습 내용",
        placeholder="예: Docker 컨테이너 기반 LangGraph 멀티 에이전트 구축 실습"
    )
    
    category_select = st.radio(
        "교육 파트 선택 (에이전트 자동 분기)",
        ["프로그래밍 실습 (Qwen-Coder 전담)", "AI 리터러시 및 이론 (Gemma4 전담)"]
    )
    
    level_select = st.selectbox(
        "타겟 수강생 난이도",
        ["입문 (Beginner)", "중급 (Intermediate)", "고급 (Advanced)"]
    )
    
    run_btn = st.button("🚀 멀티 에이전트 교재 자동 제작 시작", type="primary", use_container_width=True)

with col2:
    st.subheader("📖 생성된 교재 미리보기 및 내보내기")
    
    if run_btn:
        if not topic_input.strip():
            st.warning("⚠️ 교재 주제를 입력해주세요!")
        else:
            # 💡 st.status를 도입하여 각 에이전트의 구동 단계를 실시간 로그로 표시
            with st.status("🤖 멀티 에이전트 교재 제작 파이프라인 가동 중...", expanded=True) as status:
                try:
                    st.write("1️⃣ [기획/서칭 에이전트 (Phi4)] Tavily 고급 웹 서칭 및 목차 설계 중...")
                    
                    initial_state = {
                        "topic": topic_input,
                        "category": category_select,
                        "level": level_select,
                        "web_research_data": "",
                        "outline": "",
                        "draft_content": "",
                        "saved_id": ""
                    }
                    
                    # LangGraph 실행 (순차 협업)
                    result = app_graph.invoke(initial_state)
                    
                    st.write(f"2️⃣ [전문 에이전트 ({category_select.split()[0]})] 교재 본문 심층 집필 완료!")
                    st.write("3️⃣ [통합 에이전트] ChromaDB 영구 아카이브 적재 완료!")
                    
                    draft_content = result.get("draft_content", "내용이 생성되지 않았습니다.")
                    
                    # 💡 세션 상태에 결과 저장 (사라짐 방지 및 유지)
                    st.session_state.generated_content = draft_content
                    st.session_state.generated_title = topic_input
                    st.session_state.generated_category = category_select
                    st.session_state.generated_level = level_select
                    
                    status.update(label="🎉 교재 자동 제작이 성공적으로 완료되었습니다!", state="complete", expanded=False)
                    st.rerun()
                    
                except Exception as e:
                    status.update(label="❌ 에러 발생", state="error")
                    st.error(f"에러 내용: {str(e)}")

    # 💡 세션 상태에 내용이 존재할 경우 우측 화면에 유지 및 렌더링
    if st.session_state.generated_content:
        m1, m2, m3 = st.columns(3)
        m1.metric("선택 카테고리", st.session_state.generated_category.split()[0])
        m2.metric("타겟 난이도", st.session_state.generated_level.split()[0])
        m3.metric("상태", "아카이브 저장 완료")
        
        st.divider()
        st.markdown("##### 📄 교재 본문 미리보기")
        st.markdown(st.session_state.generated_content)
        
        st.divider()
        
        # 다운로드 버튼 영역 (마크다운 & PDF)
        dl_col1, dl_col2 = st.columns(2)
        
        with dl_col1:
            md_bytes = format_markdown_export(
                st.session_state.generated_title, 
                st.session_state.generated_category, 
                st.session_state.generated_level, 
                st.session_state.generated_content
            )
            st.download_button(
                label="📥 마크다운(.md) 다운로드",
                data=md_bytes,
                file_name=f"lecture_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True
            )
            
        with dl_col2:
            pdf_bytes = generate_pdf_export(
                st.session_state.generated_title, 
                st.session_state.generated_category, 
                st.session_state.generated_level, 
                st.session_state.generated_content
            )
            st.download_button(
                label="📥 PDF 문서 다운로드",
                data=pdf_bytes,
                file_name=f"lecture_{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("👈 왼쪽에서 교재 주제와 옵션을 설정하고 **[멀티 에이전트 교재 자동 제작 시작]** 버튼을 눌러주세요.")

st.divider()

# 4. 하단 아키텍처 요약
with st.expander("💡 [System Architecture] 멀티 에이전트 교재 제작 시스템 요약"):
    st.markdown("""
    - **핵심 기술 스택:** Python, Streamlit, LangGraph, Ollama (`embeddinggemma`, `phi4-mini`, `qwen2.5-coder`, `gemma4:12b`), ChromaDB, Tavily API (`search_depth="advanced"`), **WeasyPrint (CSS 기반 고품질 표지 분리 PDF 수출)**
    - **멀티 에이전트 워크플로우:**
      1. **기획/서칭 파트 (`phi4-mini` + Tavily):** 최신 웹 트렌드를 고급 검색한 뒤 전체 챕터 목차 설계
      2. **콘텐츠 생성 파트 (분기):** 코딩 주제는 `qwen2.5-coder`, 이론/리터러시는 `gemma4:12b`가 전문적으로 집필
      3. **영구 아카이브 파트 (`embeddinggemma` + ChromaDB):** 생성된 교재를 벡터화하여 안전하게 저장, 수정, 삭제 및 재다운로드 관리
    - **하드웨어 자원 최적화:** 모든 에이전트 호출부에 `extra_body={"keep_alive": 0}`을 적용하여 작업 직후 VRAM을 즉시 해제함으로써 OOM 방지
    """)