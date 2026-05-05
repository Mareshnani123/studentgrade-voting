from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "students")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.route("/marks", methods=["POST"])
def add_marks():
    data = request.json
    name = data.get("name")
    marks = data.get("marks")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO marks (name, marks) VALUES (%s, %s) RETURNING id;",
        (name, marks)
    )

    new_id = cur.fetchone()[0]
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"id": new_id, "name": name, "marks": marks})

@app.route("/marks", methods=["GET"])
def get_marks():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM marks;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
