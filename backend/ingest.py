import os
import faiss
import numpy as np
import re
from sentence_transformers import SentenceTransformer

# ---- PATH ----
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.normpath(os.path.join(base_dir, "..", "data", "raw", "info.txt"))

print("Reading file from:", file_path)

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

print("File loaded successfully!")

# ---- Q/A LEVEL CHUNKING ----
chunks = re.split(r'(?=Q:)', text)
chunks = [c.strip() for c in chunks if c.strip()]

print("Chunks created:", len(chunks))

# ---- EMBEDDINGS ----
model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(
    chunks,
    convert_to_numpy=True,
    normalize_embeddings=True   # 🔥 IMPORTANT
)

# ---- FAISS (COSINE SIMILARITY) ----
dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings)

# ---- SAVE ----
index_path = os.path.join(base_dir, "..", "data", "index.faiss")
chunk_path = os.path.join(base_dir, "..", "data", "chunks.npy")

faiss.write_index(index, index_path)
np.save(chunk_path, chunks)

print("Data processed and stored successfully!")