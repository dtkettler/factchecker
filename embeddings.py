from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        self.model = model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    def get_embedding(self, strings):
        embedding = self.model.encode(strings)

        return embedding