from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest
import psycopg2
import os
import time

app = Flask(__name__)

# -----------------------------
# Database Configuration
# -----------------------------
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


# -----------------------------
# Prometheus Metrics
# -----------------------------

# Total API requests
REQUEST_COUNT = Counter(
    'student_api_requests_total',
    'Total API Requests'
)

# Failed API requests
FAILED_REQUESTS = Counter(
    'student_api_failures_total',
    'Failed API requests'
)

# API latency
REQUEST_LATENCY = Histogram(
    'student_api_latency_seconds',
    'API latency in seconds'
)


# -----------------------------
# Database Connection
# -----------------------------
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


# -----------------------------
# Health Check Endpoint
# -----------------------------
@app.route('/')
def home():
    return "Student Grade API Running"


# -----------------------------
# Add Student Marks
# -----------------------------
@app.route('/marks', methods=['POST'])
def add_marks():
    REQUEST_COUNT.inc()

    start_time = time.time()

    try:
        data = request.json

        name = data.get('name')
        marks = data.get('marks')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO marks (name, marks) VALUES (%s, %s)",
            (name, marks)
        )

        conn.commit()
        cursor.close()
        conn.close()

        REQUEST_LATENCY.observe(
            time.time() - start_time
        )

        return jsonify({
            "message": "Student marks added successfully"
        })

    except Exception as e:
        FAILED_REQUESTS.inc()

        REQUEST_LATENCY.observe(
            time.time() - start_time
        )

        return jsonify({
            "error": str(e)
        }), 500


# -----------------------------
# Get Student Marks
# -----------------------------
@app.route('/results', methods=['GET'])
def get_results():
    REQUEST_COUNT.inc()

    start_time = time.time()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name, marks FROM marks"
        )

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        result = []

        for row in rows:
            result.append({
                "name": row[0],
                "marks": row[1]
            })

        REQUEST_LATENCY.observe(
            time.time() - start_time
        )

        return jsonify(result)

    except Exception as e:
        FAILED_REQUESTS.inc()

        REQUEST_LATENCY.observe(
            time.time() - start_time
        )

        return jsonify({
            "error": str(e)
        }), 500


# -----------------------------
# Prometheus Metrics Endpoint
# -----------------------------
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {
        'Content-Type': 'text/plain'
    }


# -----------------------------
# Run Flask App
# -----------------------------
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000
    )
