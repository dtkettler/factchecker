from flask import Flask, render_template, request, url_for, flash, redirect
from query import do_factcheck
from pinecone_db import PineconeDB
from gpt import GPT

app = Flask(__name__)

messages = [{'claim': 'Claim to fact check',
             'result': 'Fact check output',
             'url': "https://github.com/dtkettler/factchecker"}
            ]

pcdb = PineconeDB()
gpt_query = GPT()

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/ask/', methods=('GET', 'POST'))
def ask():
    if request.method == 'POST':
        question = request.form['question']

        if not question:
            flash('Question is required!')
        else:
            try:
                result, url = do_factcheck(question, pcdb, gpt_query)
                messages.insert(0, ({'claim': question, 'result': result, 'url': url}))
            except Exception as e:
                print("Exception: {}".format(e))

            return redirect(url_for('index'))

    return render_template('ask.html')

@app.route('/about/')
def about():
    return render_template('about.html', messages=messages)
