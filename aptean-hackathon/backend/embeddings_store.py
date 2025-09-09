# embeddings_store.py
from sentence_transformers import SentenceTransformer
from pathlib import Path
import numpy as np
import pickle

MODEL_NAME = "all-MiniLM-L6-v2"

class EmbeddingStore:
    def __init__(self, path="kb_store"):
        self.model = SentenceTransformer(MODEL_NAME)
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.path / "faiss.index"
        self.meta_file = self.path / "meta.pkl"
        # Try faiss, else fallback to sklearn KNN
        self.use_faiss = False
        try:
            import faiss
            self.faiss = faiss
            self.use_faiss = True
        except Exception:
            self.faiss = None
        self._load()

    def _load(self):
        if self.use_faiss:
            if self.index_file.exists() and self.meta_file.exists():
                self.index = self.faiss.read_index(str(self.index_file))
                with open(self.meta_file, "rb") as f:
                    self.meta = pickle.load(f)
            else:
                d = self.model.get_sentence_embedding_dimension()
                self.index = self.faiss.IndexFlatIP(d)
                self.meta = []
        else:
            # sklearn fallback
            from sklearn.neighbors import NearestNeighbors
            if self.meta_file.exists():
                with open(self.meta_file, "rb") as f:
                    stored = pickle.load(f)
                self.embs = stored.get("embs", np.empty((0, self.model.get_sentence_embedding_dimension())))
                self.meta = stored.get("meta", [])
            else:
                self.embs = np.empty((0, self.model.get_sentence_embedding_dimension()))
                self.meta = []
            self.nn = None
            if len(self.embs):
                self._rebuild_nn()

    def add(self, texts, metadatas=None):
        embs = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        if self.use_faiss:
            self.index.add(embs)
            if metadatas is None:
                metadatas = [{}]*len(texts)
            self.meta.extend(metadatas)
            self._save()
        else:
            self.embs = np.vstack([self.embs, embs]) if self.embs.size else embs
            if metadatas is None:
                metadatas = [{}]*len(texts)
            self.meta.extend(metadatas)
            self._rebuild_nn()
            self._save()

    def _rebuild_nn(self):
        from sklearn.neighbors import NearestNeighbors
        self.nn = NearestNeighbors(n_neighbors=min(10, max(1, len(self.embs))), metric='cosine').fit(self.embs)

    def search(self, query, k=5):
        q_emb = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        results = []
        if self.use_faiss:
            D, I = self.index.search(q_emb, k)
            for score, idx in zip(D[0], I[0]):
                if idx == -1 or idx >= len(self.meta): continue
                results.append((float(score), self.meta[idx]))
        else:
            if self.nn is None:
                return []
            dists, inds = self.nn.kneighbors(q_emb, n_neighbors=min(k, len(self.embs)))
            for dist, idx in zip(dists[0], inds[0]):
                score = 1 - float(dist)  # cosine -> similarity
                results.append((score, self.meta[idx]))
        return results

    def _save(self):
        if self.use_faiss:
            self.faiss.write_index(self.index, str(self.index_file))
            with open(self.meta_file, "wb") as f:
                pickle.dump(self.meta, f)
        else:
            with open(self.meta_file, "wb") as f:
                pickle.dump({"embs": self.embs, "meta": self.meta}, f)
