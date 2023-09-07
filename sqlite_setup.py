import sqlite3


con = sqlite3.connect("results.db")
cur = con.cursor()

cur.execute("CREATE TABLE articles(url, text)")
cur.execute("CREATE TABLE results(claim, result, url)")

