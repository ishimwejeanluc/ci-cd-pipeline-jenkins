import os
import time

from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "topics_db")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "appsecret")
DB_PORT = int(os.getenv("DB_PORT", "3306"))


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
    )


def wait_for_db(retries=20, delay=3):
    for _ in range(retries):
        try:
            conn = get_connection()
            conn.close()
            return True
        except mysql.connector.Error:
            time.sleep(delay)
    return False


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/topics")
def list_topics():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, description, created_at FROM topics ORDER BY id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.post("/topics")
def create_topic():
    payload = request.get_json(silent=True) or {}
    title = payload.get("title")
    description = payload.get("description", "")

    if not title:
        return jsonify({"error": "title is required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO topics (title, description) VALUES (%s, %s)",
        (title, description),
    )
    conn.commit()
    topic_id = cursor.lastrowid
    cursor.execute(
        "SELECT id, title, description, created_at FROM topics WHERE id = %s",
        (topic_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(row), 201


@app.get("/topics/<int:topic_id>")
def get_topic(topic_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, title, description, created_at FROM topics WHERE id = %s",
        (topic_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        return jsonify({"error": "topic not found"}), 404

    return jsonify(row)


@app.put("/topics/<int:topic_id>")
def update_topic(topic_id):
    payload = request.get_json(silent=True) or {}
    title = payload.get("title")
    description = payload.get("description")

    if title is None and description is None:
        return jsonify({"error": "title or description is required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM topics WHERE id = %s", (topic_id,))
    existing = cursor.fetchone()
    if existing is None:
        cursor.close()
        conn.close()
        return jsonify({"error": "topic not found"}), 404

    if title is not None and description is not None:
        cursor.execute(
            "UPDATE topics SET title = %s, description = %s WHERE id = %s",
            (title, description, topic_id),
        )
    elif title is not None:
        cursor.execute(
            "UPDATE topics SET title = %s WHERE id = %s",
            (title, topic_id),
        )
    else:
        cursor.execute(
            "UPDATE topics SET description = %s WHERE id = %s",
            (description, topic_id),
        )

    conn.commit()
    cursor.execute(
        "SELECT id, title, description, created_at FROM topics WHERE id = %s",
        (topic_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(row)


@app.delete("/topics/<int:topic_id>")
def delete_topic(topic_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM topics WHERE id = %s", (topic_id,))
    existing = cursor.fetchone()
    if existing is None:
        cursor.close()
        conn.close()
        return jsonify({"error": "topic not found"}), 404

    cursor.execute("DELETE FROM topics WHERE id = %s", (topic_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "deleted"})


if __name__ == "__main__":
    if not wait_for_db():
        raise SystemExit("Database not ready")
    app.run(host="0.0.0.0", port=5000)
