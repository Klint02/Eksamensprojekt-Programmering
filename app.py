from flask import Flask, render_template, request, redirect, session, url_for, escape, g
import sqlite3
from activity import Activity
import pickle

app = Flask(__name__)

activitys = []

app.secret_key = 'BAD_SECRET_KEY'
@app.route('/', methods=['POST', 'GET'])
def index():
    with sqlite3.connect("db.db") as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
            elif request.method == 'POST':
                activity = request.form.get('activity')
                time = request.form.get('time')
                day = request.form.get('day')
                description = request.form.get('description')

                activitys.append(Activity(day,str(activity), str(time) ,"DATO",str(description)))
                print(activitys)

                cursor = db.cursor()
            
                #cursor.execute("UPDATE person SET Calender = (?) WHERE person = 'test'", (activitys))
                cursor.execute("INSERT INTO person (Person, Calender) VALUES ('test', ?)", ())

                #return render_template("index.html", activitys=activitys)
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html", error=message, activitys=activitys)
    return render_template("index.html", activitys=activitys)

@app.route('/save', methods=['POST', 'GET'])
def save():
    with sqlite3.connect("db.db") as db:
        try:
            # Hvis der postes noget data
            if request.method == "POST":
                with open(f"datafiles/{session['username']}", 'wb') as file:
                    pickle.dump(activitys, file)
                return redirect("/")
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html", error=message)

def log_the_user_in(username):
    try:
        with open(f"datafiles/{session['username']}", 'rb') as file2:
            saved_data = pickle.load(file2)
            activitys = saved_data
            return render_template('index.html', activitys=activitys, username=username)
    # Hvis personen ikke har fået oprettet en fil, opret en der er tom
    except FileNotFoundError:
        with open(f"datafiles/{session['username']}", 'wb') as file:
            activitys = ""
            pickle.dump(activitys, file)
            return render_template('index.html', activitys=activitys, username=username)
    

@app.route('/login', methods=['POST', 'GET'])
def login():
    with sqlite3.connect("users.db") as db:
        try:
            error = None
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')

                cursor = db.cursor()
                cursor.execute('select * from User where username = ? and password = ?', (username,password))
                valid_login = cursor.fetchall()

                if valid_login != []:
                    session['username'] = request.form['username']
                    
                    return log_the_user_in(request.form['username'])
                else:
                    error = 'Invalid username/password'
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("login.html", error=message)

    return render_template('login.html', error=error)

@app.route('/register', methods=['POST', 'GET'])
def register():
    with sqlite3.connect("users.db") as db:
        try:
            error = None
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')

                cursor = db.cursor()
                cursor.execute('select * from User where username = ? and password = ?', (username,password))
                print(cursor.fetchall())
                valid_login = cursor.fetchall()
                
                if valid_login == []:
                    #cursor = db.cursor()
                    print("test")
                    cur = db.cursor()
                    cur.execute("INSERT INTO User(username, password) values (?,?)", (username,password))
                    print(cur.fetchall())
                    
                    render_template('login.html', error=error)
                else:
                    error = 'Kontoen eksiterer allerede'
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("register.html", error=message)
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', default=None)
    return '<h1>Logged out!</h1>'

app.run(host='0.0.0.0', port=81, debug=True)
