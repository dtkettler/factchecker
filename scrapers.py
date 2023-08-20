import requests
from urllib.parse import urlparse
import tiktoken
from bs4 import BeautifulSoup


token_limit = 10000

def scrape_politifact_url(url):
    #print("Checking {}".format(url))
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    bodies = soup.findAll('body')
    paragraphs = bodies[1].findAll('p')

    outstring = ""
    for paragraph in paragraphs:
        outstring += paragraph.text + "\n"

    return trim_tokens(outstring)

def scrape_factcheckorg_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    outstring = ""
    divs = soup.findAll('div')
    for div in divs:
        if 'id' in div.attrs and div['id'] == "dpsp-content-top":
            tag = div.next_sibling
            while tag and tag.name != "hr":
                if tag.name == "p":
                    outstring += tag.text + "\n"
                tag = tag.next_sibling
            break

    return trim_tokens(outstring)

def scrape_appropriate(url):
    domain = urlparse(url).netloc

    if domain == "www.politifact.com":
        return scrape_politifact_url(url)
    elif domain == "www.factcheck.org":
        return scrape_factcheckorg_url(url)
    else:
        return "Invalid Domain"

def get_factcheck_articles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    article_urls = []
    articles = soup.findAll('article')
    for article in articles:
        article_url = article.h3.a['href']
        article_urls.append(article_url)

    return article_urls

def get_factcheck_months(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    month_urls = []
    headers = soup.findAll('h3')
    for header in headers:
        if header.text == "Browse by Month:":
            for li in header.findNext('ul').findAll('li'):
                url = li.a['href']
                month_urls.append(url)

    return month_urls

def trim_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    token_count = len(encoding.encode(text))
    while token_count > token_limit:
        text = "\n".join(text.split("\n")[1:])
        token_count = len(encoding.encode(text))

    return text


#scrape_politifact_url("https://www.politifact.com/factchecks/2019/may/21/facebook-posts/no-nasa-did-not-spend-over-165-million-space-pen-w/")
#print(scrape_factcheckorg_url("https://www.factcheck.org/2023/08/biden-cherry-picks-unemployment-record/"))
#print(scrape_factcheckorg_url("https://www.factcheck.org/2023/08/scicheck-rfk-jr-s-covid-19-deceptions/"))
#print(scrape_factcheckorg_url("https://www.factcheck.org/2023/07/bidens-numbers-july-2023-update/"))
#print(scrape_factcheckorg_url("https://www.factcheck.org/2023/05/factchecking-ron-desantis-presidential-announcement/"))
