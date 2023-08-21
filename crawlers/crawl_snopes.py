import time
from pinecone_db import PineconeDB
from scrapers import get_snopes_categories, get_snopes_articles, get_snopes_claim


index_url = "https://www.snopes.com/sitemap/"
categories = get_snopes_categories(index_url)

pcdb = PineconeDB()

print(categories)
for category in categories:
    articles = get_snopes_articles(category)
    print(articles)

    for article in articles:
        if pcdb.does_document_exit(article):
            continue

        claim = get_snopes_claim(article)
        print(claim)

        if claim:
            pcdb.add_strings([claim], article)

        time.sleep(1)
