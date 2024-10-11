### 1주차 과제 진행
* client.ipynb는 카프카에 요청 위한 코드
* 테스트 시 server.ipynb 실행, client.ipynb 실행 후 색인 진행

1. 제품 listing 전체를 Elasticsearch에 인덱스
2. 제품 인덱스의 ”item_keywords” 와 “product_description”를 업데이트 할 수 있는 API
3. item_keyword와 product_description 정보로 제품을 검색
---
세부사항
Kafka
Elasticsearch
- 로컬환경에서 작동되는 인프라를 구축합니다.(텍스트 전처리는 python의 nltk를 씁니다: https://www.nltk.org/)
- 다량의 업데이트를 지원할 수 있는 시스템 구축을 가정합니다. (Flink: https://nightlies.apache.org/flink/flink-docs-release-1.20/docs/dev/python/overview/)
- language_tag가 en_US 로 된 제품만 인덱스 합니다. (Kafka: https://docs.confluent.io/kafka-clients/python/current/overview.html)