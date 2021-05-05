from flask import Flask, render_template, request, redirect, session, url_for, escape, g
import sqlite3
from activity import Activity
import pickle

app = Flask(__name__)

activitys = []

predefined_activitys = [Activity("Undefined", "Fodboldkamp (U21) - Herning vs Silkeborg", "2.5", "DATO", "En fodboldkamp mellem Herning og Silkeborg. Spilles på Herningvej 2")]

app.secret_key = 'BAD_SECRET_KEY'
@app.route('/', methods=['POST', 'GET'])
def index():
    with sqlite3.connect("users.db") as db:
        try:
            print(session['username'])
            cursor = db.cursor()
            cursor.execute("select * from Interests where username = '" + session['username'] + "'")
            print(cursor.fetchall())
            if session.get('username') == None:
                return render_template("login.html")
            if request.method == 'POST':
                global activitys
                activity = request.form.get('activity')
                time = request.form.get('time')
                day = request.form.get('day')
                description = request.form.get('description')

                activitys.append(Activity(day,str(activity), str(time) ,"DATO",str(description)))
                print(activitys)

            

        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html", error=message, activitys=activitys)
    return render_template("index.html", activitys=activitys)

@app.route('/save', methods=['POST', 'GET'])
def save():
    with sqlite3.connect("users.db") as db:
        try:
            # Hvis der postes noget data
            if request.method == "POST":
                with open(f"datafiles/{session['username']}", 'wb') as file:
                    pickle.dump(activitys, file)
                return redirect("/")
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html", error=message)

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    with sqlite3.connect("users.db") as db:
        try:
            if request.method == 'POST':
                primary_interest = request.form.get('primary_interest')
                secondary_interest = request.form.get('secondary_interest')
                tertiary_interest = request.form.get('tertiary_interest')



                cursor = db.cursor()
                cursor.execute("UPDATE Interests SET [primary] = ?, secondary = ?, tertiary = ? WHERE username = ?", (primary_interest, secondary_interest, tertiary_interest, session['username']))
                print(primary_interest,secondary_interest,tertiary_interest)
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("profile.html", error=message)
    return render_template("profile.html")

def log_the_user_in(username):
    try:
        with open(f"datafiles/{session['username']}", 'rb') as file2:
            global activitys
            saved_data = pickle.load(file2)
            #activitys.append(saved_data)
            activitys = saved_data
            print(activitys)
            #return render_template('index.html', activitys=activitys, username=username)
            return redirect("/")
    # Hvis personen ikke har fået oprettet en fil, opret en der er tom
    except FileNotFoundError:
        with open(f"datafiles/{session['username']}", 'wb') as file:
            activitys = ""
            pickle.dump(activitys, file)
            with sqlite3.connect("users.db") as db:
                try:
                    cursor = db.cursor()
                    cursor.execute("INSERT INTO Interests VALUES (?,?,?,?)", (session['username'], "Ikke oplyst", "Ikke oplyst", "Ikke oplyst"))
                    return render_template('index.html', activitys=activitys, username=username)
                except sqlite3.Error:
                    message = "There was a problem executing the SQL statement"
                    return render_template("login.html", error=message)
    

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
    global activitys
    session.pop('username', default=None)
    #activitys.clear()
    return render_template('login.html')

app.run(host='0.0.0.0', port=81, debug=True)
