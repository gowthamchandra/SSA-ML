from flask import Flask, request, jsonify, render_template
import requests
import pickle
import warnings
import datetime
import json
from base64 import b64encode

app = Flask(__name__, static_folder='static', template_folder='templates')

# Load the model
model = pickle.load(open('K4_IC10/model.pkl', 'rb'))

# API credentials
API_URL = "https://hindalco-belagavi.covacsis.com/api/third-party/raw-param/facts/dynamic-query"
API_USER = "report"
PASSWORD = "ipf@2014"  # Replace with the actual password

# Function to convert human-readable date to epoch in milliseconds
def convert_to_epoch(date_string):
    dt = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M")
    return int(dt.timestamp() * 1000)

@app.route('/')
def home():
    return render_template('index7.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    try:
        warnings.filterwarnings("ignore")
        data = request.get_json()
        From = data.get('From')
        To = data.get('To')

        min_date = convert_to_epoch(From)
        max_date = convert_to_epoch(To)

        auth_token = b64encode(f"{API_USER}:{PASSWORD}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_token}",
            "Content-Type": "application/json"
        }

        parameter_dict = {
            "NG": 286, "FGT": 287, "HZT": 288, "Stack": 289, "Feed": 974,
            "RPM": 1049, "Cooler": 550, "CO": 291, "EIT": 554,
            "EOT": 553, "EIP": 555, "PAP": 560, "O2":292
        }
        results = {}

        for param_name, param_id in parameter_dict.items():
            payload = [{
                "machineId": 35,
                "parameterId": param_id,
                "maxDate": max_date,
                "minDate": min_date
            }]
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                mean_value = data[0].get("meanValue", "N/A") if data else "N/A"
                results[param_name] = round(mean_value, 3) if isinstance(mean_value, (int, float)) else mean_value
            else:
                results[param_name] = f"Error: {response.status_code}"

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = [[
            data.get('NG', 0), data.get('FGT', 0), data.get('HZT', 0),
            data.get('Stack', 0), data.get('Feed', 0), data.get('RPM', 0),
            data.get('Cooler', 0), data.get('CO', 0), data.get('BA', 0),
            data.get('EIT', 0), data.get('EOT', 0), data.get('EIP', 0),
            data.get('PAP', 0), data.get('O2',0), data.get('Molochite', 0)
        ]]
        prediction = model.predict(features)
        rounded_prediction = round(prediction[0], 3)
        return jsonify({'prediction': rounded_prediction})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)