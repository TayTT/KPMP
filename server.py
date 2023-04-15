from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
import sqlite3
import pandas as pd

# create Flask app
app = Flask(__name__)
app.secret_key = "TopSecretAPIKey"

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///KPMP.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class KPMP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receive_time = db.Column(db.DateTime, nullable=False)
    temp = db.Column(db.Float, nullable=True)
    hum = db.Column(db.Float, nullable=True)
    acc_x = db.Column(db.Float, nullable=True)
    acc_y = db.Column(db.Float, nullable=True)
    acc_z = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "time": self.receive_time,
            "temperature": self.temp,
            "humidility": self.hum,
            "acc_x": self.acc_x,
            "acc_y": self.acc_y,
            "acc_z": self.acc_z
        }

with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/index')
def home():
    num_of_values = 5
    con = sqlite3.connect("instance/KPMP.db")
    df = pd.read_sql_query(f"SELECT * from KPMP ORDER BY id DESC LIMIT {num_of_values}", con)
    con.close()

    last_values = [df[column].values.tolist() for column in df.columns]

    return render_template("index.html",
                           date_year=datetime.date.today().year,
                           num_of_values=num_of_values,
                           num_of_elements=len(last_values),
                           headers=df.columns.values,
                           last_values=last_values)

@app.route("/last-24hours")
def plot_last_24hours():
    try:
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        con = sqlite3.connect("instance/KPMP.db")
        df = pd.read_sql_query(f"SELECT * from KPMP WHERE receive_time >= '{yesterday}'", con)
        con.close()
    except Exception as e:
        return f"Error! {e}"
    else:
        x_data = df[df.columns[1]].values.tolist()
        y_data = [df[df.columns[i]].values.tolist() for i in range(2, 9)]
        return render_template("data_plot_multiple.html",
                               date_year=datetime.date.today().year,
                               x_data=x_data,
                               y_data=y_data,
                               legend=[sensor.replace("_", " ") for sensor in df.columns[2:9].values.tolist()],
                               title="last 24 hours temperature data from all sensors",
                               x_label="time",
                               y_label="Temperature/Humidity")

@app.route("/temp-24hours")
def plot_temp_24hours():
    try:
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        con = sqlite3.connect("instance/KPMP.db")
        df = pd.read_sql_query(f"SELECT receive_time, temp, hum, acc_x, acc_y, acc_z from KPMP WHERE receive_time >= '{yesterday}'", con)
        
        con.close()
    except Exception as e:
        return f"Error! {e}"
    else:
        print(df.columns)
        x_data = df[df.columns[0]].values.tolist()
        y_data = [df[df.columns[i]].values.tolist() for i in range(1, 5)]
        return render_template("data_plot_multiple.html",
                               date_year=datetime.date.today().year,
                               x_data=x_data,
                               y_data=y_data,
                               legend=[sensor.replace("_", " ") for sensor in df.columns[1:5].values.tolist()],
                               title="last 24 hours data from all sensors",
                               x_label="time",
                               y_label="Temperature [\u2103]")


@app.route("/all", methods=["GET"])
def get_all_data():
    try:
        KPMP_datatable = db.session.query(KPMP).all()
    except Exception as e:
        print(e)
        return jsonify(response={"error": f"Reading KPMP data failed. Error description {e}"}), 404
    return jsonify(weathers=[data.to_dict() for data in KPMP_datatable])

@app.route("/last", methods=["GET"])
def get_last_data():
    try:
        KPMP_datatable = db.session.query(KPMP).order_by(KPMP.id.desc()).first()
    except Exception as e:
        print(e)
        return jsonify(response={"error": f"Reading KPMP data failed. Error description {e}"}), 404
    if KPMP_datatable is not None:
        return jsonify(weathers=KPMP.to_dict())
    else:
        return jsonify(responseget_last_data={"error": "No entries in database"}), 400

@app.route("/plot-data", methods=["GET"])
def plot_data():
    con = sqlite3.connect("instance/KPMP.db")
    df = pd.read_sql_query("SELECT * from KPMP ", con)

    con.close()

    x_data = df[df.columns[1]].values.tolist()
    y_data = df[df.columns[2]].values.tolist()

    return render_template("data_plot.html",
                           date_year=datetime.date.today().year,
                           x_data=x_data,
                           y_data=y_data,
                           x_label=df.columns[1],
                           y_label=df.columns[2])

@app.route("/plot-all")
def plot_all():
    try:
        con = sqlite3.connect("instance/KPMP.db")
        df = pd.read_sql_query("SELECT * from KPMP ", con)
        con.close()
    except Exception as e:
        return f"Error! {e}"
    else:
        x_data = df[df.columns[1]].values.tolist()
        y_data = [df[df.columns[i]].values.tolist() for i in range(2, 9)]
        return render_template("data_plot_multiple.html",
                               date_year=datetime.date.today().year,
                               x_data=x_data,
                               y_data=y_data,
                               legend=[sensor.replace("_", " ") for sensor in df.columns[2:9].values.tolist()],
                               title="Data from all sensors",
                               x_label="time",
                               y_label="Temperature/Humidity")

@app.route("/plot/<sensor_name>")
def plot_one(sensor_name):
    try:
        con = sqlite3.connect("instance/KPMP.db")
        df = pd.read_sql_query(f"SELECT receive_time, {sensor_name} from KPMP ", con)
        con.close()
    except Exception as e:
        return f"Error! {e}"
    else:
        x_data = df["receive_time"].values.tolist()
        y_data = df[sensor_name].values.tolist()

        return render_template("data_plot.html",
                               date_year=datetime.date.today().year,
                               x_data=x_data,
                               y_data=y_data,
                               x_label="time",
                               y_label="temperature [\u00B0C]")

# create record
@app.route('/KPMP-data', methods=["POST"])
def KPMP_data():
    if request.is_json:
        data = request.get_json()

        try:
            new_data = KPMP(receive_time=datetime.datetime.today(),
                               temp=data["temperature"],
                               hum=data["humidility"],
                               acc_x=data["acc_x"],
                               acc_y=data["acc_y"],
                               acc_z=data["acc_z"]
                               )

            db.session.add(new_data)
            db.session.commit()
        except Exception as e:
            print(e)
            return jsonify(response={"error": f"Adding KPMP data failed. Error description {e}"}), 404
        else:
            return jsonify(response={"success": "KPMP data added successfully"}), 200

@app.route('/KPMP_choice', methods=['POST', 'GET'])
def KPMP_choice():
    if request.method == 'POST':
        # jeśli pole jest puste
        if request.form.get('num') == '':
            return redirect(url_for('home'))
        # jeśli tych danych nie ma w bazie
        elif KPMP.query.filter_by(id=request.form.get('num')).first() is None:
            print("nie ma tego w bazie")
            return redirect(url_for('home'))
        # jak wszystko git
        else:
            return redirect(url_for('plot_data'))
    else:
        return redirect(url_for('plot_data'))

if __name__ == '__main__':
    # app.run(host='192.168.1.100', port=5000)
    app.run(debug=True)