import openai
import configparser
import tiktoken
from scrapers import *


class GPT:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('keys.ini')

        self.api_key = config['DEFAULT']['openai_key']

        self.model = "gpt-3.5-turbo"
        self.long_model = "gpt-3.5-turbo-16k"
        self.lower_token_count = 3500

    def get_factcheck(self, query, url):
        content = scrape_appropriate(url)

        openai.api_key = self.api_key
        completion = openai.ChatCompletion.create(
            model=self.get_model(content),
            messages=[
                #{"role": "system", "content": "Answer whether or not \"{}\" is factual given the content.".format(query)},
                {"role": "system",
                 #"content": "Answer whether or not \"{}\" is factual given the content or say \"I don't know\" if you can't tell.".format(query)},
                 "content": "Based on the content first answer whether \"{}\" is true, false, mostly true, or mostly false and then give a short summary. If you can't tell then just say \"I don't know.\"".format(query)},
                {"role": "user", "content": content}
            ]
        )

        #print(completion)
        return completion

    def get_summary(self, text):
        openai.api_key = self.api_key
        completion = openai.ChatCompletion.create(
            model=self.get_model(text),
            messages=[
                #{"role": "system", "content": "Summarize the content in a single sentence."},
                #{"role": "system", "content": "Summarize the most significant factual claims in the content and output a list with one claim per sentence and one sentence per line."},
                {"role": "system",
                 "content": "Summarize the most significant claims in the content and output a list with complete sentences, one claim per sentence, and one sentence per line."},
                {"role": "user", "content": text}
            ]
        )

        return completion

    def get_model(self, text):
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        token_count = len(encoding.encode(text))

        if token_count > self.lower_token_count:
            return self.long_model
        else:
            return self.model
