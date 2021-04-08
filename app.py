from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
monday = {}
tuesday = {}
wednesday = {}
thursday = {}
friday = {}
saturday = {}
sunday = {}

@app.route('/', methods=['POST', 'GET'])
def index():
    with sqlite3.connect("db.db") as db:
        try:
            if request.method == 'POST':
                activity = request.form.get('activity')
                time = request.form.get('time')
                day = request.form.get('day')
            
                if day == "Monday":
                    monday[str(activity)] = [str(activity),time]
                    print(monday)
                if day == "Tuesday":
                    thursday[str(activity)] = [str(activity),time]
                    print(thursday)
                if day == "Wednesday":
                    wednesday[str(activity)] = [str(activity),time]
                    print(wednesday)
                if day == "Thursday":
                    thursday[str(activity)] = [str(activity),time]
                    print(thursday)
                if day == "Friday":
                    friday[str(activity)] = [str(activity),time]
                    print(friday)
                if day == "Saturday":
                    saturday[str(activity)] = [str(activity),time]
                    print(saturday)
                if day == "Sunday":
                    sunday[str(activity)] = [str(activity),time]
                    print(sunday)


        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html", error=message)
    return render_template("index.html")

app.run(host='0.0.0.0', port=81, debug=True)
