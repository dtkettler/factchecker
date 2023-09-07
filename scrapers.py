import requests
import sqlite3
from urllib.parse import urlparse
import tiktoken
from bs4 import BeautifulSoup


token_limit = 10000

snopes_ratings = {"/fact-check/rating/research-in-progress": "still being researched.",
                  "/fact-check/rating/mixture": "a mix of truth an falsehoods.",
                  "/fact-check/rating/unproven": "unproven.",
                  "/fact-check/rating/legend": "lacking in detail and unprovable.",
                  "/fact-check/rating/labeled-satire": "satire.",
                  "/fact-check/rating/lost-legend": "false.",
                  "/fact-check/rating/true": "true.",
                  "/fact-check/rating/mostly-false": "mostly false.",
                  "/fact-check/rating/unfounded": "unfounded.",
                  "/fact-check/rating/correct-attribution": "true.",
                  "/fact-check/rating/scam": "a scam.",
                  "/fact-check/rating/originated-as-satire": "originally satire.",
                  "/fact-check/rating/fake": "fake.",
                  "/fact-check/rating/mostly-true": "mostly true.",
                  "/fact-check/rating/false": "false.",
                  "/fact-check/rating/outdated": "outdated.",
                  "/fact-check/rating/misattributed": "misattributed.",
                  "/fact-check/rating/legit": "legit.",
                  "/fact-check/rating/recall": "a genuine recall."}

def scrape_politifact_url(url):
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

def scrape_snopes_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    outstring = ""

    found = False
    h3s = soup.findAll('h3')
    for h3 in h3s:
        if "class" in h3.attrs and h3["class"] and h3["class"][0] == "is-style-article-section":
            found = True
            tag = h3.next_sibling
            while tag:
                if tag.name == "p":
                    outstring += tag.text + "\n"
                tag = tag.next_sibling

    if not found:
        blockquotes = soup.findAll('blockquote')
        if blockquotes:
            found = True
            first = blockquotes[0]
            tag = first.next_sibling
            while tag:
                if tag.name == "p":
                    outstring += tag.text + "\n"
                tag = tag.next_sibling

    if not found:
        sections = soup.findAll('section')
        for section in sections:
            if "id" in section.attrs and section["id"] == "fact_check_rating_container":
                found = True
                tag = section.next_sibling
                while tag:
                    if tag.name == "p":
                        outstring += tag.text + "\n"
                    tag = tag.next_sibling

    outstring += "The claim that, \""

    divs = soup.findAll('div')
    for div in divs:
        if "class" in div.attrs and div["class"] and div["class"][0] == "claim_cont":
            outstring += div.text.strip() + "\" is "
            break

    links = soup.findAll('a')
    for link in links:
        if "class" in link.attrs and link["class"] and link["class"][0] == "rating_link_wrapper":
            rating_url = link['href']
            break

    outstring += snopes_ratings[rating_url]

    return outstring

def scrape_appropriate(url):
    con = sqlite3.connect("results.db")
    cur = con.cursor()

    res = cur.execute("SELECT text FROM articles where url = ?", (url,))
    row = res.fetchone()
    if row:
        return row[0]

    domain = urlparse(url).netloc

    output = ""
    if domain == "www.politifact.com":
        output = scrape_politifact_url(url)
    elif domain == "www.factcheck.org":
        output = scrape_factcheckorg_url(url)
    elif domain == "www.snopes.com":
        output = scrape_snopes_url(url)
    else:
        return "Invalid Domain"

    data = ({'url': url, 'text': output})
    cur.execute("INSERT INTO articles VALUES (:url, :text)", data)
    con.commit()

    return output

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

def get_snopes_categories(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    category_urls = []
    divs = soup.findAll('div')
    for div in divs:
        if "class" in div.attrs and div["class"] and div["class"][0] == "section_title_wrap":
            if div.span.span.text == "Fact Checks":
                section = div.next_sibling
                sub_divs = section.findAllNext('div')
                for sub_div in sub_divs:
                    if "class" in sub_div.attrs and sub_div["class"] and sub_div["class"][0] == "archive_section_item":
                        category_urls.append(sub_div.a["href"])

    return category_urls

def get_snopes_articles(url, article_urls=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    if not article_urls:
        article_urls = []

    links = soup.findAll('a')
    for link in links:
        if "class" in link.attrs and link["class"] and link["class"][0] == "outer_article_link_wrapper":
            article_urls.append(link["href"])

    # Now look for next button
    for link in links:
        if "class" in link.attrs and link["class"] and link["class"][0].strip() == "next-button":
            if len(link["class"]) > 1 and link["class"][1] == "disabled":
                return article_urls

            next_page = link["href"]
            return get_snopes_articles("https://www.snopes.com" + next_page, article_urls)

    return article_urls

def get_snopes_claim(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    divs = soup.findAll('div')
    for div in divs:
        if "class" in div.attrs and div["class"] and div["class"][0] == "claim_cont":
            return div.text.strip()

    return ""

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
#print(scrape_snopes_url("https://www.snopes.com/fact-check/senomyx-flavor-additive/"))
#print(scrape_snopes_url("https://www.snopes.com/fact-check/the-write-stuff/"))
#print(scrape_snopes_url("https://www.snopes.com/fact-check/maui-wildfires-caused-by-direct-energy-weapon/"))