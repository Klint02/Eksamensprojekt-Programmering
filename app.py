from flask import Flask, render_template, request, redirect, session, url_for, escape, g
import sqlite3
from activity import Activity

app = Flask(__name__)

activitys = {}
predefined_activitys = {}
time_minus = []
app.secret_key = 'BAD_SECRET_KEY'
@app.route('/', methods=['POST', 'GET'])
def index():
    with sqlite3.connect("users.db") as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
            cursor = db.cursor()
            cursor.execute("select * from User_preferences where username = '" + session['username'] + "'")
            user_interests = cursor.fetchall()

            day_search = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for x in day_search:
                cursor.execute("SELECT sum(time) FROM Activity WHERE day = ? AND user = ?", (x, session['username']))
                time_minus.append(cursor.fetchall())
            print(time_minus[0][0][0])


            cursor.execute("SELECT * FROM Predefined_activity")
            predefined_activitys_list = cursor.fetchall()
            for pactivity in predefined_activitys_list:
                predefined_activitys[str(pactivity[0])] = [pactivity[0],pactivity[1],pactivity[2],pactivity[3],pactivity[4],pactivity[5]]

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
            return render_template("index.html", error=message, activitys=activitys, predefined_activitys=predefined_activitys, time_minus=time_minus)
    return render_template("index.html", activitys=activitys, predefined_activitys=predefined_activitys, user_interests=user_interests, time_minus=time_minus)

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
                freetime_monday = request.form.get('freetime_monday')
                freetime_tuesday = request.form.get('freetime_tuesday')
                freetime_wednesday = request.form.get('freetime_wednesday')
                freetime_thursday = request.form.get('freetime_thursday')
                freetime_friday = request.form.get('freetime_friday')
                freetime_saturday = request.form.get('freetime_saturday')
                freetime_sunday = request.form.get('freetime_sunday')
                cursor = db.cursor()
                cursor.execute("UPDATE User_preferences SET [primary] = ?, secondary = ?, tertiary = ?, time_monday = ?, time_tuesday = ?, time_wednesday = ?, time_thursday = ?, time_friday = ?, time_saturday = ?, time_sunday = ? WHERE username = ?", (primary_interest, secondary_interest, tertiary_interest, freetime_monday, freetime_tuesday, freetime_wednesday, freetime_thursday, freetime_friday, freetime_saturday, freetime_sunday, session['username']))
                print(primary_interest,secondary_interest,tertiary_interest)
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("profile.html", error=message)
    return render_template("profile.html")

@app.route('/get', methods=['GET', 'POST'])
def get_item():
    with sqlite3.connect("users.db") as db:
        try:
            if request.method == 'POST':
                val = request.get_json().get('val')
                print(val)
                cursor = db.cursor()
                cursor.execute("DELETE FROM Activity WHERE id = '" + val + "'")
                del activitys[str(val)]
                return redirect("/")
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return redirect("/")
    return redirect("/")

@app.route('/pactivity_get', methods=['GET', 'POST'])
def pactivity_get():
    with sqlite3.connect("users.db") as db:
        try:
            if request.method == 'POST':
                val = request.get_json().get('val')
                print(val)
                get_activity = predefined_activitys.get(val)
                print(get_activity[3])
                cursor = db.cursor()
                cursor.execute("INSERT INTO Activity (activity, time, day, desc, user) VALUES (?,?,?,?,?)", (get_activity[1], get_activity[2], get_activity[3], get_activity[4], session['username']))
                #del activitys[str(val)]
                return redirect("/")
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return redirect("/")
    return redirect("/")

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
                    cur.execute("INSERT INTO User_preferences(username, [primary],secondary,tertiary) VALUES (?,?,?,?)", (username, "Ikke oplyst", "Ikke oplyst", "Ikke oplyst"))
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

    return render_template('login.html')

app.run(host='0.0.0.0', port=81, debug=True)
