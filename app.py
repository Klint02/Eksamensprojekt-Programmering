from flask import Flask, render_template, request, redirect, session, url_for, escape, g
import sqlite3
from activity import Activity

app = Flask(__name__)

activitys = {}

predefined_activitys = [Activity("Undefined", "Fodboldkamp (U21) - Herning vs Silkeborg", "2.5", "DATO", "En fodboldkamp mellem Herning og Silkeborg. Spilles på Herningvej 2")]

app.secret_key = 'BAD_SECRET_KEY'
@app.route('/', methods=['POST', 'GET'])
def index():
    with sqlite3.connect("users.db") as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
            cursor = db.cursor()
            cursor.execute("select * from Interests where username = '" + session['username'] + "'")
            user_interests = cursor.fetchall()

            cursor.execute("SELECT * FROM Activity WHERE user = '" + session['username'] + "'")
            user_activitys = cursor.fetchall()
            for row in user_activitys:
                activitys[str(row[0])] = [row[0],row[1],row[2],row[3],row[4]]
            if request.method == 'POST':
                activity = request.form.get('activity')
                time = request.form.get('time')
                day = request.form.get('day')
                description = request.form.get('description')

                cursor.execute("INSERT INTO Activity (activity, time, day, desc, user) VALUES (?,?,?,?,?)", (activity, time, day, description, session['username']))
                return redirect("/")
            

        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html", error=message, activitys=activitys)
    return render_template("index.html", activitys=activitys)

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    with sqlite3.connect("users.db") as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
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

def log_the_user_in():
    return redirect("/")
    

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
                    
                    return log_the_user_in()
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
                    cur.execute("INSERT INTO Interests VALUES (?,?,?,?)", (username, "Ikke oplyst", "Ikke oplyst", "Ikke oplyst"))
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
