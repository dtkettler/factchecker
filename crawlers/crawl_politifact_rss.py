import feedparser
from pinecone_db import PineconeDB


feed = feedparser.parse("https://www.politifact.com/rss/factchecks/")

entries = feed.entries

#print(entries)

pcdb = PineconeDB()
for entry in entries:
    summary = entry['summary']
    link = entry['link']

    if pcdb.does_document_exit(link):
        continue

    text = " - ".join(summary.split(" - ")[1:])
    print(text)

    pcdb.add_strings([summary], link)
