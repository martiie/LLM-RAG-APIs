import faiss
import numpy as np

class FaissIndexer:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)

    def build_index(self, vectors):
        self.index.reset()
        self.index.add(vectors)

    def search(self, query_vector, top_k=3):
        distances, indices = self.index.search(query_vector, top_k)
        return distances, indices
