from flask import Flask, render_template, request, redirect, session, url_for, escape, g
import sqlite3
from activity import Activity

app = Flask(__name__)

activitys = []

# https://www.youtube.com/watch?v=cvPnRmOs9io

# Spørgsmål
# Database hvor den gemmer kalender for hver person
# Kalender over flere uger


@app.route('/', methods=['POST', 'GET'])
def index():
    with sqlite3.connect("db.db") as db:
        try:
            if request.method == 'POST':
                activity = request.form.get('activity')
                time = request.form.get('time')
                day = request.form.get('day')
                description = request.form.get('description')

                activitys.append(Activity(day,str(activity), str(time) ,"DATO",str(description)))
                print(activitys)

                return render_template("index.html", activitys=activitys)
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html", error=message, activitys=activitys)
    return render_template("index.html")

DATABASE = 'users.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def valid_login(username, password):
    user = query_db('select * from User where username = ? and password = ?', [username, password], one=True)
    if user is None:
        return False
    else:
        return True


def log_the_user_in(username):
    return render_template('profile.html', username=username)

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'

    return render_template('login.html', error=error)

app.run(host='0.0.0.0', port=81, debug=True)
