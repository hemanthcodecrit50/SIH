import os
import faiss
import json
from transformers import AutoTokenizer, AutoModel
import torch

STATIC_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "static_db")
INDEX_FILE = os.path.join(STATIC_DB_DIR, "faiss.index")
DOCS_FILE = os.path.join(STATIC_DB_DIR, "docs.jsonl")
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
encoder = AutoModel.from_pretrained(MODEL_NAME)

def embed(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = encoder(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.cpu().numpy()

def build_index():
    docs = []
    vectors = []
    with open(DOCS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            docs.append(doc)
            vectors.append(embed(doc["text"])[0])
    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(np.array(vectors).astype("float32"))
    faiss.write_index(index, INDEX_FILE)
    with open(os.path.join(STATIC_DB_DIR, "docs_cache.json"), "w", encoding="utf-8") as f:
        json.dump(docs, f)

def retrieve_static_info(intent):
    # Load docs and FAISS index
    import numpy as np
    if not os.path.exists(INDEX_FILE):
        build_index()
    index = faiss.read_index(INDEX_FILE)
    with open(os.path.join(STATIC_DB_DIR, "docs_cache.json"), "r", encoding="utf-8") as f:
        docs = json.load(f)
    query_vec = embed(intent)
    D, I = index.search(query_vec, k=1)
    doc = docs[I[0][0]]
    return doc["text"]