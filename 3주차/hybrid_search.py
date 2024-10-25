import os
import re

from elasticsearch import Elasticsearch
from fastapi import FastAPI
from groq import Client
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

index_name = "product"

# elastic search setting
es_client = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "password"),
    verify_certs=False,
    ssl_show_warn=False
)

# embedding, pincone, groq setting
embedding_model = SentenceTransformer('./all-MiniLM-L12-v2-abo')
pinecone_api_key = os.environ['pinecone_api_key']
groq_api_key = os.environ['groq_api_key']
client = Client(api_key=groq_api_key)
pc = Pinecone(api_key=pinecone_api_key)

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )
pc_client = pc.Index(index_name)

# Execute fastAPI
app = FastAPI()


@app.get("/search")
async def search(q: str):
    if not is_alphanumeric(q):
        return 'Only English searches are supported.'

    if not valid_question(q):
        return 'Your question is not about a product. Please ask again.'

    results = hybrid_search(q, 60)

    if not results:
        return 'The requested item could not be found. Please try searching with different keywords.'

    return [r[0] for r in results]


def text_search(query, size=10):
    q = {
        "query": {
            "match": {
                "item_name": query
            }
        },
        "size": size
    }

    result = es_client.search(index=index_name, body=q)
    hits = result['hits']
    return [hit['_source'] for hit in hits['hits']]


def vector_search(query, topk=3):
    query_embedding = embedding_model.encode(query).tolist()

    results = pc_client.query(
        namespace="ns1",
        vector=query_embedding,
        top_k=topk,
        include_values=False,
        include_metadata=True
    )

    sorted_matches = sorted(results['matches'], key=lambda x: x['score'], reverse=True)
    return sorted_matches


def reciprocal_rank_fusion(results, K=60):
    docs = []
    rrf_score = []

    for ranked_doc in results:
        for rank, doc in enumerate(ranked_doc, 1):
            score = 1.0 / (rank + K)

            item_id_list = [d['item_id'] for d in docs]
            if doc['item_id'] in item_id_list:
                idx = item_id_list.index(doc['item_id'])
                rrf_score[idx] += score
                continue

            docs.append(doc)
            rrf_score.append(score)

    scored_docs = zip(docs, rrf_score)
    sorted_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)
    return sorted_docs


def hybrid_search(query, topk=3):
    vector_search_result = vector_search(query, topk)
    vector_search_result = [{'item_id': result['id'], 'item_name': result['metadata']['item_name']} for result in vector_search_result]


    results = [vector_search_result, text_search(query, topk)]
    ranked_results = reciprocal_rank_fusion(results)
    return [result for result in ranked_results if result[1] > 0.02]


def valid_question(query):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a bot designed to check if the input is related to a product search. Respond with 'True' or 'False'. For keywords, always respond with 'True'. Only check and respond for natural language sentences."
            },
            {
                "role": "user",
                "content": query,
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content == "True"


def is_alphanumeric(s):
    return bool(re.match(r'^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>\/?\s]*$', s))
