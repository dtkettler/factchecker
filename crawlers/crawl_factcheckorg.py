import time
from pinecone_db import PineconeDB
from scrapers import scrape_factcheckorg_url, get_factcheck_articles, get_factcheck_months
from gpt import GPT


index_url = "https://www.factcheck.org/archives/"
months = get_factcheck_months(index_url)

gpt_query = GPT()
pcdb = PineconeDB()

for month_url in months:
    articles = get_factcheck_articles(month_url)
    print(articles)

    for article in articles:
        if pcdb.does_document_exit(article):
            continue

        try:
            text = scrape_factcheckorg_url(article)
            summary = gpt_query.get_summary(text)

            summary_text = summary['choices'][0]["message"]["content"]
            print(summary_text)
            break

            pcdb.add_strings(summary_text.split("\n"), article)

            print("{} added, sleeping for a bit".format(article))
        except Exception as e:
            print(e)
            print("Error in {}".format(article))

        time.sleep(30)
