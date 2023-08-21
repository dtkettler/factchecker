from urllib.parse import urlparse
from pinecone_db import PineconeDB
from gpt import GPT


valid_domains = ["www.politifact.com", "www.factcheck.org", "www.snopes.com"]
threshold = 0.5

def do_factcheck(val, pcdb, gpt_query):
    results = pcdb.query(val)

    for result in results['matches']:
        print(result)
        if result['score'] < threshold:
            continue

        print("Found potential match")

        url = result['metadata']['url']
        domain = urlparse(url).netloc

        if domain not in valid_domains:
            continue

        completion = gpt_query.get_factcheck(val, url)
        if not completion['choices'][0]['message']['content'] == "I don't know.":
            output = completion['choices'][0]['message']['content']
            #output += "\n<p>Find out more at <a href=\"{}\">{}</a></p>".format(url, url)

            return output, url

    # No good results found
    return "No results found.", ""

if __name__ == "__main__":
    pcdb = PineconeDB()
    gpt_query = GPT()
    val = input("Enter statement you want to fact check: ")

    output, url = do_factcheck(val, pcdb, gpt_query)

    print(output)
    print("Find out more at {}".format(url))


