from flask import Flask, render_template, request, redirect, session, url_for, escape, g
import sqlite3

app = Flask(__name__)
##########################################################
# Lists, dictionaries og variabler
activitys = {}
predefined_activitys = {}
time_minus = []
app.secret_key = 'BAD_SECRET_KEY'
##########################################################

##########################################################
# Forsiden (efter man er logget ind)
@app.route('/', methods=['POST', 'GET'])
def index():
    # Opretter forbindelse til databasen
    with sqlite3.connect("users.db") as db:
        try:
            # Sletter alt data i time_minus så den kan blive opdateret
            time_minus.clear()
            # Hvis at man ikke er logget ind, send brugeren tilbage til loginsiden
            if session.get('username') == None:
                return render_template("login.html")

            # Henter data omkring brugerens interesser og defineret timer pr. dag
            cursor = db.cursor()
            cursor.execute("select * from User_preferences where username = '" + session['username'] + "'")
            user_interests = cursor.fetchall()

            # Henter data omkring hvor mange timer brugeren bruger hver af dagene og indsætter dem ind i en liste
            day_search = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for x in day_search:
                cursor.execute("SELECT sum(time) FROM Activity WHERE day = ? AND user = ?", (x, session['username']))
                time_minus.append(cursor.fetchall())

            # Henter alle de predefineret aktiviteter og indsætter dem ind i et dictionary
            cursor.execute("SELECT * FROM Predefined_activity")
            predefined_activitys_list = cursor.fetchall()
            for pactivity in predefined_activitys_list:
                predefined_activitys[str(pactivity[0])] = [pactivity[0],pactivity[1],pactivity[2],pactivity[3],pactivity[4],pactivity[5]]

            # Henter alle brugerens aktiviteter og indsætter dem ind i et dictionary
            cursor.execute("SELECT * FROM Activity WHERE user = '" + session['username'] + "'")
            user_activitys = cursor.fetchall()
            for row in user_activitys:
                activitys[str(row[0])] = [row[0],row[1],row[2],row[3],row[4]]

            # Oprettelse af en aktivitet:
            # Hvis der bliver sendt noget data fra siden
            # Henter datene der er blevet indsat og indsætter dem ind i som brugerens aktiviteter
            if request.method == 'POST':
                activity = request.form.get('activity')
                time = request.form.get('time')
                day = request.form.get('day')
                description = request.form.get('description')

                cursor.execute("INSERT INTO Activity (activity, time, day, desc, user) VALUES (?,?,?,?,?)", (activity, time, day, description, session['username']))
                return redirect("/")
            
        # Hvis der er en fejl med sqlite3
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html", error=message, activitys=activitys, predefined_activitys=predefined_activitys, time_minus=time_minus)
    # Render siden index.html med alle lister og dictionaries
    return render_template("index.html", activitys=activitys, predefined_activitys=predefined_activitys, user_interests=user_interests, time_minus=time_minus)
##########################################################

##########################################################
# Profil siden
@app.route('/profile', methods=['POST', 'GET'])
def profile():
    # Opretter forbindelse til databasen
    with sqlite3.connect("users.db") as db:
        try:
            # Hvis at man ikke er logget ind, send brugeren tilbage til loginsiden
            if session.get('username') == None:
                return render_template("login.html")
            
            # Opdatering af interesser og timer pr. dag
            # Hvis der sendes noge data
            # Tag alt data som brugeren har indsat og indsæt det ind i daabasen
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
        # Hvis der er en fejl med sqlite3
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("profile.html", error=message)
    # Vis siden profile.html til brugeren
    return render_template("profile.html")
##########################################################

##########################################################
# Funktion til at slette en aktivitet i brugeren kalender
@app.route('/get', methods=['GET', 'POST'])
def get_item():
    # Opretter forbindelse til databasen
    with sqlite3.connect("users.db") as db:
        try:
            # Hvis der sendes noget data
            # Tager fat i variablen (id) af aktiviteten og sletter den fra databasen og dictionarien
            # Sender brugeren tilbage til forsiden
            if request.method == 'POST':
                val = request.get_json().get('val')
                cursor = db.cursor()
                cursor.execute("DELETE FROM Activity WHERE id = '" + val + "'")
                del activitys[str(val)]
                return redirect("/")
        # Hvis der er en fejl med sqlite3
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return redirect("/")
    # Sender brugeren tilbage til forsiden
    return redirect("/")
##########################################################

##########################################################
# Fra en af de predefineret aktiviteter til at det vises under brugerens kalender
@app.route('/pactivity_get', methods=['GET', 'POST'])
def pactivity_get():
    # Opretter forbindelse til databasen
    with sqlite3.connect("users.db") as db:
        try:
            # Hvis der sendes noget data
            # Tager fat i variablen og finder værdierne af nøglen i dictionarien
            # Indsætter alt data fra den predefineret aktvitet ind i activity tabellen
            if request.method == 'POST':
                val = request.get_json().get('val')
                get_activity = predefined_activitys.get(val)
                cursor = db.cursor()
                cursor.execute("INSERT INTO Activity (activity, time, day, desc, user) VALUES (?,?,?,?,?)", (get_activity[1], get_activity[2], get_activity[3], get_activity[4], session['username']))
                return redirect("/")
        # Hvis der er en fejl med sqlite3
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return redirect("/")
    # Sender brugeren tilbage til forsiden
    return redirect("/")
##########################################################

##########################################################
# Når brugeren skal logges ind
def log_the_user_in():
    # Send brugeren til forsiden
    return redirect("/")
##########################################################

##########################################################
# Login siden
@app.route('/login', methods=['POST', 'GET'])
def login():
    # Opretter forbindelse til databasen
    with sqlite3.connect("users.db") as db:
        try:
            error = None
            # Hvis der sendes noget data
            # Tjekker i databasen om der findes en bruger der har det username og password
            # der er indsat. Hvis det findes, køres funktionen log_the_user_in(), ellers sendes
            # der en fejl med at username eller password ikke findes
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
        # Hvis der er en fejl med sqlite3
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("login.html", error=message)
    # Sender brugeren til login siden
    return render_template('login.html', error=error)
##########################################################

##########################################################
# Registrer siden, hvor man kan oprette en bruger
@app.route('/register', methods=['POST', 'GET'])
def register():
    # Opretter forbindelse til databasen
    with sqlite3.connect("users.db") as db:
        try:
            error = None
            # Hvis der sendes noget data
            # Tjekker om en bruger med samme username og password findes.
            # Hvis det ikke gør oprettes der en bruger, hvor det indsættes ind i databasen User
            # Og der oprettes også en kolonne til brugeren i tabellen User_preferences. Efter sendes brugeren
            # til login siden. Hvis brugeren allerede eksisterer sendes beskden "konton eksisterer allerede" tilbage
            # til brugeren
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
        # Hvis der er en fejl med sqlite3
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("register.html", error=message)
    # Sender brugeren til register siden
    return render_template('register.html', error=error)
##########################################################

##########################################################
# Når brugeren logger ud
@app.route('/logout')
def logout():
    # Fjerner brugeren fra session og sender brugeren tilbage til login siden
    global activitys
    session.pop('username', default=None)
    return render_template('login.html')
##########################################################

app.run(host='0.0.0.0', port=81, debug=True)
