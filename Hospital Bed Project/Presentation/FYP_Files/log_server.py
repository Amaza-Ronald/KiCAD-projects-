from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Path to the alerts.log file
LOG_FILE = '/home/pi/Desktop/alerts.log'

@app.route('/logs/alerts.log')
def get_alerts():
    """Serve the alerts as a JSON array with optional filtering."""
    try:
        # Check if the log file exists
        if not os.path.exists(LOG_FILE):
            return jsonify({"error": "Log file not found"}), 404

        # Get query parameters for filtering (if provided)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        alert_type = request.args.get('alert_type')

        # Parse dates if provided
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        alerts = []
        with open(LOG_FILE, 'r') as file:
            for line in file:
                if line.strip():  # Skip empty lines
                    try:
                        alert = json.loads(line.strip())
                        alert_timestamp = datetime.strptime(alert.get('timestamp', ''), '%Y-%m-%d %H:%M:%S')

                        # Apply filters only if query parameters are provided
                        if start_date and alert_timestamp < start_date:
                            continue  # Skip alerts before the start date
                        if end_date and alert_timestamp > end_date:
                            continue  # Skip alerts after the end date
                        if alert_type and alert_type != 'all' and alert.get('type') != alert_type:
                            continue  # Skip alerts that don't match the type

                        alerts.append(alert)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON line: {e}")
                    except ValueError as e:
                        print(f"Error parsing timestamp in line: {e}")

        return jsonify(alerts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New endpoint for Android app to get recent alerts
@app.route('/api/recent-alerts', methods=['GET'])
def get_recent_alerts():
    """Serve the most recent first five alerts."""
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({"error": "Log file not found"}), 404

        alerts = []
        with open(LOG_FILE, 'r') as file:
            for line in file:
                if line.strip():  # Skip empty lines
                    try:
                        alert = json.loads(line.strip())
                        alerts.append(alert)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON line: {e}")

        # Get the most recent first five alerts
        recent_alerts = alerts[-5:][::-1]  # Reverse to get the most recent first
        return jsonify(recent_alerts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New endpoint for Android app to get all alerts
@app.route('/api/all-alerts', methods=['GET'])
def get_all_alerts():
    """Serve all alerts."""
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({"error": "Log file not found"}), 404

        alerts = []
        with open(LOG_FILE, 'r') as file:
            for line in file:
                if line.strip():  # Skip empty lines
                    try:
                        alert = json.loads(line.strip())
                        alerts.append(alert)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON line: {e}")

        return jsonify(alerts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)