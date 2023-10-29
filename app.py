from flask import Flask, render_template, request, url_for, flash, redirect
from query import do_factcheck
from pinecone_db import PineconeDB
from gpt import GPT
import persistence

app = Flask(__name__)

pcdb = PineconeDB()
gpt_query = GPT()

@app.route('/')
def index():
    persist = persistence.get_persistence_layer()

    id = request.args.get('id')
    if id:
        messages = persist.get_messages(id)
    else:
        messages = persist.get_messages()

    return render_template('index.html', messages=messages)

@app.route('/ask/', methods=('GET', 'POST'))
def ask():
    if request.method == 'POST':
        persist = persistence.get_persistence_layer()

        question = request.form['question']

        if not question:
            flash('Question is required!')
        else:
            try:
                result, url = do_factcheck(question, pcdb, gpt_query)
                print(result)
                id = persist.put_message(question, result, url)

                print(id)
            except Exception as e:
                print("Exception: {}".format(e))

            return redirect(url_for('index') + "?id={}".format(id))

    return render_template('ask.html')

@app.route('/about/')
def about():
    return render_template('about.html')
