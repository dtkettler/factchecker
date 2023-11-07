import sys
from urllib.parse import urlparse
from pinecone_db import PineconeDB
from gpt import GPT
from scrapers import scrape_appropriate
import persistence


valid_domains = ["www.politifact.com", "www.factcheck.org", "www.snopes.com"]
threshold = 0.65

def do_factcheck(val, pcdb, gpt_query, persist):
    results = pcdb.query(val)

    for result in results['matches']:
        if result['score'] < threshold:
            continue

        print(result)
        print("Found potential match")

        url = result['metadata']['url']
        domain = urlparse(url).netloc

        if domain not in valid_domains:
            continue

        content = scrape_appropriate(url, gpt_query, persist)
        completion = gpt_query.get_factcheck(val, content)
        if not completion['choices'][0]['message']['content'] == "I don't know.":
            output = completion['choices'][0]['message']['content']
            #output += "\n<p>Find out more at <a href=\"{}\">{}</a></p>".format(url, url)

            return output, url

    # No good results found
    return "No results found.", ""

if __name__ == "__main__":
    pcdb = PineconeDB()
    gpt_query = GPT()
    if len(sys.argv) > 1:
        val = sys.argv[1]
    else:
        val = input("Enter statement you want to fact check: ")

    persist = persistence.get_persistence_layer()
    output, url = do_factcheck(val, pcdb, gpt_query, persist)

    print(output)
    print("Find out more at {}".format(url))


