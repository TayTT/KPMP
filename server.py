from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
import sqlite3
import pandas as pd
import numpy as np
from peaks import find_peaks_magn

# create Flask app
app = Flask(__name__)
app.secret_key = "TopSecretAPIKey"

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///KPMP.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class KPMP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pack_id = db.Column(db.Text, nullable=False)
    receive_time = db.Column(db.DateTime, nullable=False)
    mag_diff = db.Column(db.Float, nullable=True)
    temp = db.Column(db.Float, nullable=True)
    hum = db.Column(db.Float, nullable=True)
    courier_id = db.Column(db.Text, nullable=False)
    def to_dict(self):
        return {
            "time": self.receive_time,
            "pack_id": self.pack_id,
            "mag_diff": self.mag_diff,
            "temp": self.temp,
            "hum": self.hum,
            "courier_id": self.courier_id
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


@app.route("/plot-data/<num>", methods=["GET"])
def plot_data(num):
    con = sqlite3.connect("instance/KPMP.db")
    df = pd.read_sql_query(f"SELECT * from KPMP WHERE pack_id = {num}", con)
    con.close()
    peaks_idx = find_peaks_magn(df)

    x_data = df[df.columns[3]].values.tolist()
    y_data_temp = df["temp"].values.tolist()
    y_data_hum = df["hum"].values.tolist()
    y_data_magn = [df["mag_diff"].values.tolist(), df["mag_diff"].iloc[peaks_idx].values.tolist()]
    new_list = [x_data[peak] for peak in peaks_idx]
    print(x_data)
    x_data_magn = [x_data, new_list]

    return render_template("data_plot.html",
                           date_year=datetime.date.today().year,
                           x_data=x_data,
                           x_data_magn =x_data_magn,
                           y_data_magn=y_data_magn,
                           legend_magn=["magnituda", "wykryty rzut"],
                           y_data_temp=y_data_temp, 
                           legend_temp="temperatura",
                           y_data_hum=y_data_hum,
                           legend_hum="wilgotność",
                           x_label=df.columns[1],
                           y_label_magn="[j.u.]",
                           y_label_temp="[*C]",
                           y_label_hum="[%]")

# create record
@app.route('/KPMP-data', methods=["POST"])
def KPMP_data():
    if request.is_json:
        data = request.get_json()

        try:
            new_data = KPMP(receive_time=datetime.datetime.today(),
                            pack_id=data["pack_id"],
                            mag_diff = data["mag_diff"],
                            temp = data["temp"],
                            hum = data["hum"],
                            courier_id = data["courier_id"]
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
        elif KPMP.query.filter_by(pack_id=request.form.get('num')).first() is None:
            print("nie ma tego w bazie")
            return redirect(url_for('home'))
        # jak wszystko git
        else:
            return redirect(url_for('plot_data', num=request.form.get('num')))
    else:
        return redirect(url_for('plot_data'))

if __name__ == '__main__':
    # app.run(host='192.168.1.100', port=5000)
    app.run(debug=True)