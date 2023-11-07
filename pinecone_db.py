import configparser
import pinecone
import time
from embeddings import Embedder


class PineconeDB:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('keys.ini')

        pinecone.init(api_key=config['DEFAULT']['pinecone_key'], environment=config['DEFAULT']['pinecone_environment'])

        self.index = pinecone.Index("factdb")

        self.embedder = Embedder()

    def add_strings(self, strings, url, max_retries=10):
        payload = []
        for index, string in enumerate(strings):
            if len(string.strip()) == 0:
                continue
            embeddings = self.embedder.get_embedding(string)
            payload.append((url + str(index), embeddings.tolist(), {"url": url}))

        successful = False
        tries = 0
        while tries < max_retries and not successful:
            try:
                self.index.upsert(payload)
                successful = True
            except Exception as e:
                print("error connecting to Pinecone, retrying")
                print(e)
                time.sleep((tries + 1) * 2)

            tries += 1

        if not successful:
            print("Could not upload {} to Pinecone".format(url))

    def query(self, string):
        embeddings = self.embedder.get_embedding(string)

        #xc = self.index.query(embeddings.tolist(), top_k=5, include_metadata=True)
        xc = self.query_with_retries(embeddings=embeddings.tolist(), top_k=10, include_metadata=True)
        return xc

    def does_document_exit(self, url):
        #xc = self.index.query(id=url + "0", top_k=1, include_metadata=False)
        xc = self.query_with_retries(id=url + "0", top_k=1, include_metadata=False)

        if xc['matches']:
            return True
        else:
            return False

    def query_with_retries(self, top_k, include_metadata, id=None, embeddings=None, max_retries=10):
        successful = False
        tries = 0
        while tries < max_retries and not successful:
            try:
                if id:
                    xc = self.index.query(id=id, top_k=top_k, include_metadata=include_metadata)
                elif embeddings:
                    xc = self.index.query(embeddings, top_k=top_k, include_metadata=include_metadata)
                else:
                    print("Did not provide a valid id or embeddings")
                    return {"matches": []}

                successful = True
            except Exception as e:
                print("error connecting to Pinecone, retrying")
                print(e)
                time.sleep((tries + 1) * 2)
                xc = {"matches": []}

            tries += 1

        if not successful:
            print("Could not query Pinecone")

        return xc
