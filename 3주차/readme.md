### 3주차 과제 진행
* Elasticsearch, Django, LLM, Pinecone 을 이용해서 검색 API 구축
* Text 정보 Elasticsearch에 인덱스, text vector 정보는 Pinecone에 인덱스
* Fast API로 hybrid 검색 API 구현

기능 요구사항
* 키워드와 자연어 검색기능 지원
---
세부사항
* 로컬환경에서 작동되는 API를 구축합니다.
* 영문 검색만 지원합니다.
* 임베딩 모델은 lab에서 쓴 모델 혹은 MTEB Leaderboard에서 찾아서 써도 괜찮습니다.

지원하는 검색어
* 키워드 (e.g. ‘chair’, ‘vitamin’, ‘desk’)
* 자연어 문장 (e.g. ‘is there a dining table made with oak?’)
* 존재하지 않은 제품이거나 서비스와 관계없는 질문은 답변 생략.
