import time
import os
from pinecone_db import PineconeDB
from scrapers import get_politifact_articles, get_politifact_claim


os.chdir("..")

index_urls = [#"https://www.politifact.com/factchecks/list/?ruling=true",
              "https://www.politifact.com/factchecks/list/?ruling=mostly-true",
              "https://www.politifact.com/factchecks/list/?ruling=half-true",
              "https://www.politifact.com/factchecks/list/?ruling=barely-true",
              "https://www.politifact.com/factchecks/list/?ruling=false",
              "https://www.politifact.com/factchecks/list/?ruling=pants-fire"]

pcdb = PineconeDB()

for index_url in index_urls:
    articles = get_politifact_articles(index_url)

    print(articles)

    for article in articles:
        if pcdb.does_document_exit(article):
            continue

        claims = get_politifact_claim(article)
        print(claims)

        if claims and (claims[0] or claims[1]):
            pcdb.add_strings(claims, article)

        time.sleep(1)
