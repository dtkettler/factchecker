import configparser
import pinecone
from embeddings import Embedder


class PineconeDB:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('keys.ini')

        pinecone.init(api_key=config['DEFAULT']['pinecone_key'], environment=config['DEFAULT']['pinecone_environment'])

        self.index = pinecone.Index("factdb")

        self.embedder = Embedder()

    def add_strings(self, strings, url):
        payload = []
        for index, string in enumerate(strings):
            embeddings = self.embedder.get_embedding(string)
            payload.append((url + str(index), embeddings.tolist(), {"url": url}))

        #self.index.upsert([(id, embeddings.tolist())])
        self.index.upsert(payload)

    def query(self, string):
        embeddings = self.embedder.get_embedding(string)

        xc = self.index.query(embeddings.tolist(), top_k=5, include_metadata=True)
        return xc

    def does_document_exit(self, url):
        xc = self.index.query(id=url + "0", top_k=1, include_metadata=False)

        if xc['matches']:
            return True
        else:
            return False
