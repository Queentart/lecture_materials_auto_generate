# -*- coding: utf-8 -*-
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
import chromadb
from langchain_ollama import OllamaEmbeddings  # 💡 최신 langchain_ollama 패키지로 임베딩 모듈 변경

# 환경 변수 로드
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embeddinggemma:latest")

# 1. ChromaDB 영구 저장소 클라이언트 및 임베딩 모델 초기화
DB_PATH = "./chroma_lecture_db"
client = chromadb.PersistentClient(path=DB_PATH)

# LangChain 기반 Ollama 임베딩 객체 생성 (embeddinggemma 활용)
embeddings = OllamaEmbeddings(
    base_url=OLLAMA_BASE_URL,
    model=EMBEDDING_MODEL
)

# 컬렉션 생성 또는 로드 (교재 및 참고 자료 아카이브 전용)
collection_name = "lecture_materials_archive"
try:
    chroma_collection = client.get_collection(name=collection_name)
except Exception:
    chroma_collection = client.create_collection(name=collection_name)


# 2. 교재 및 컨텐츠 저장 기능 (Create)
def save_lecture_material(title: str, category: str, level: str, content: str):
    """
    생성된 교재 챕터 또는 자료를 ChromaDB에 영구 저장합니다.
    내부적으로 embeddinggemma를 통해 문서를 벡터화합니다.
    """
    doc_id = f"mat_{uuid.uuid4().hex[:10]}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 텍스트 벡터화 수행
    vector = embeddings.embed_query(content)
    
    chroma_collection.add(
        ids=[doc_id],
        embeddings=[vector],
        documents=[content],
        metadatas=[{
            "timestamp": timestamp,
            "title": title,
            "category": category,
            "level": level
        }]
    )
    return doc_id


# 3. 의미 기반 벡터 검색 및 RAG (Semantic Search & Retrieval)
def search_relevant_materials(query: str, n_results: int = 3):
    """
    입력된 쿼리(주제 또는 질문)와 의미적으로 가장 유사한 기존 교재 및 참고 자료를 벡터 검색합니다.
    """
    if chroma_collection.count() == 0:
        return []
    
    query_vector = embeddings.embed_query(query)
    results = chroma_collection.query(
        query_embeddings=[query_vector],
        n_results=min(n_results, chroma_collection.count())
    )
    
    retrieved_items = []
    if results and 'documents' in results and len(results['documents']) > 0:
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        for doc, meta in zip(docs, metas):
            retrieved_items.append({
                "content": doc,
                "title": meta.get("title"),
                "category": meta.get("category"),
                "level": meta.get("level"),
                "timestamp": meta.get("timestamp")
            })
            
    return retrieved_items


# 4. 전체 히스토리 조회 기능 (Read - Get All History)
def get_all_materials():
    """
    저장된 모든 교재 및 챕터 기록을 시간순(또는 등록순)으로 조회합니다.
    """
    try:
        data = chroma_collection.get(include=["documents", "metadatas", "embeddings"])
        return data
    except Exception as e:
        print(f"조회 중 에러 발생: {e}")
        return {"ids": [], "documents": [], "metadatas": []}


# 5. 개별 기록 수정 기능 (Update)
def update_material(doc_id: str, title: str, category: str, level: str, content: str):
    """
    특정 고유 ID(doc_id)를 가진 교재 기록의 내용을 수정하고 벡터를 재생성합니다.
    """
    new_vector = embeddings.embed_query(content)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    chroma_collection.update(
        ids=[doc_id],
        embeddings=[new_vector],
        documents=[content],
        metadatas=[{
            "timestamp": timestamp,
            "title": title,
            "category": category,
            "level": level
        }]
    )


# 6. 개별 기록 삭제 기능 (Delete)
def delete_material(doc_id: str):
    """
    특정 고유 ID(doc_id)를 가진 교재 기록을 아카이브에서 삭제합니다.
    """
    chroma_collection.delete(ids=[doc_id])