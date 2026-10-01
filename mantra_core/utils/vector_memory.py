import faiss
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

class VectorMemory:
    """
    Handles semantic storage and retrieval using FAISS and Sentence Transformers.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = [] # Stores original text/objects corresponding to vectors
        self.model = None
        self.backend = "hashed"

        if SentenceTransformer is not None:
            try:
                # Avoid network dependency during local/offline runs.
                self.model = SentenceTransformer(model_name, local_files_only=True)
                self.backend = "sentence-transformer"
            except Exception:
                self.model = None

    def _encode(self, text):
        """
        Produces a stable embedding vector. Falls back to a local hashed encoder
        when the transformer model is unavailable.
        """
        if self.model is not None:
            return np.array(self.model.encode([text]), dtype="float32")

        vector = np.zeros((1, self.dimension), dtype="float32")
        for token in text.lower().split():
            vector[0, hash(token) % self.dimension] += 1.0

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector /= norm
        return vector

    def store(self, text, data_obj):
        """
        Embeds text and stores it in the vector index with associated metadata.
        """
        vector = self._encode(text)
        self.index.add(vector.astype('float32'))
        self.metadata.append(data_obj)

    def retrieve(self, query, top_k=3):
        """
        Performs similarity search and returns the top_k most relevant past memories.
        """
        if self.index.ntotal == 0:
            return []

        query_vector = self._encode(query)
        distances, indices = self.index.search(query_vector.astype('float32'), top_k)
        
        results = []
        for i in indices[0]:
            if i != -1 and i < len(self.metadata):
                results.append(self.metadata[i])
        
        return results

if __name__ == "__main__":
    # Quick Test
    vm = VectorMemory()
    vm.store("I want to play music on Spotify", {"action": "play_music", "app": "spotify"})
    vm.store("Open YouTube for lofi", {"action": "open_app", "app": "youtube"})
    
    related = vm.retrieve("play some songs")
    print(f"Retrieved: {related}")
