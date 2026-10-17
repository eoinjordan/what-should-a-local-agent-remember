"""Load the course data into the Pi's MongoDB. Mirrors the course's data.py.

Differences from the course:
  * the two Hugging Face datasets are read through the datasets-server JSON API
    (20 full pages, 107 chunks), so the heavy `datasets`/pyarrow packages are not needed;
  * chunks are embedded with the model chosen in embeddings.py (local by default);
  * the vector search index is created only if the server has search (mongot) attached;
    on plain mongod the tool in main.py falls back to an exact cosine scan, which for
    107 vectors is instant and gives the same top-5.
Run once:  .venv/bin/python data.py
"""
import requests
from pymongo import MongoClient
import key_param
from embeddings import embed, MODEL_NAME, DIMENSIONS

DB_NAME, FULL_COLLECTION_NAME, VS_COLLECTION_NAME, VS_INDEX_NAME = "ai_agents", "full_docs", "chunked_docs", "vector_index"
API = "https://datasets-server.huggingface.co/rows"


def rows(dataset):
    out, offset = [], 0
    while True:
        r = requests.get(API, params={"dataset": dataset, "config": "default", "split": "train", "offset": offset, "length": 100}, timeout=60)
        r.raise_for_status()
        batch = [x["row"] for x in r.json()["rows"]]
        out += batch
        if len(batch) < 100:
            return out
        offset += 100


client = MongoClient(key_param.mongodb_uri)
db = client[DB_NAME]
vs_collection, full_collection = db[VS_COLLECTION_NAME], db[FULL_COLLECTION_NAME]
vs_collection.drop(); full_collection.drop()

docs = rows("MongoDB/mongodb-docs")
full_collection.insert_many(docs)
print(f"full_docs: {full_collection.count_documents({})} pages")

chunks = rows("MongoDB/mongodb-docs-embedded")
for i, chunk in enumerate(chunks, 1):
    chunk["embedding"] = embed(chunk["body"], input_type="document")   # replaces the dataset's embedding with ours
    vs_collection.insert_one(chunk)
    if i % 20 == 0 or i == len(chunks):
        print(f"chunked_docs: {i}/{len(chunks)} embedded with {MODEL_NAME} ({DIMENSIONS} dims)")

full_collection.create_index("title")

model = {"name": VS_INDEX_NAME, "type": "vectorSearch",
         "definition": {"fields": [{"type": "vector", "path": "embedding", "numDimensions": DIMENSIONS, "similarity": "cosine"}]}}
try:
    vs_collection.create_search_index(model=model)
    print(f"vector search index '{VS_INDEX_NAME}' created (search is attached to this deployment)")
except Exception as e:  # plain mongod without mongot
    print(f"no search index: {type(e).__name__} - main.py will use the exact cosine fallback instead of $vectorSearch")
