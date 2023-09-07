import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from query import do_factcheck
from pinecone_db import PineconeDB
from gpt import GPT

app = Flask(__name__)

pcdb = PineconeDB()
gpt_query = GPT()

def get_messages(id=None):
    con = sqlite3.connect("results.db")
    cur = con.cursor()

    if id:
        try:
            intid = int(id)
            res = cur.execute("SELECT rowid, claim, result, url FROM results where rowid = {}".format(intid))
        except:
            print("Not a valid ID")
            return []
    else:
        res = cur.execute("SELECT rowid, claim, result, url FROM results ORDER BY rowid DESC LIMIT 20")

    messages = []
    for row in res.fetchall():
        messages.append({'id': row[0],
                         'claim': row[1],
                         'result': row[2],
                         'url': row[3]})

    return messages

@app.route('/')
def index():
    id = request.args.get('id')
    if id:
        messages = get_messages(id)
    else:
        messages = get_messages()

    return render_template('index.html', messages=messages)

@app.route('/ask/', methods=('GET', 'POST'))
def ask():
    if request.method == 'POST':
        con = sqlite3.connect("results.db")
        cur = con.cursor()

        question = request.form['question']

        if not question:
            flash('Question is required!')
        else:
            try:
                result, url = do_factcheck(question, pcdb, gpt_query)
                print(result)
                #messages.insert(0, ({'claim': question, 'result': result, 'url': url}))
                data = ({'claim': question, 'result': result, 'url': url})
                cur.execute("INSERT INTO results VALUES (:claim, :result, :url)", data)
                con.commit()
                res = cur.execute("SELECT last_insert_rowid()")
                id = res.fetchall()[0][0]
                print(id)
            except Exception as e:
                print("Exception: {}".format(e))

            return redirect(url_for('index') + "?id={}".format(id))

    return render_template('ask.html')

@app.route('/about/')
def about():
    return render_template('about.html')
