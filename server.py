import os
import base64
import sqlite3


from flask import Flask, request, jsonify, Response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)
auth = HTTPBasicAuth()

# Initialize SQLite DB
db_file = "keys.db"
decrypt_db_file = "decrypted_data.db"


def init_db():
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users
                          (username TEXT PRIMARY KEY,
                           password TEXT)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS keys
                          (username TEXT PRIMARY KEY,
                           public_key TEXT,
                           private_key TEXT)"""
        )
        conn.commit()
        conn.close()

    if not os.path.exists(decrypt_db_file):
        conn = sqlite3.connect(decrypt_db_file)
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS decrypted_data
                          (username TEXT,
                           data TEXT)"""
        )
        conn.commit()
        conn.close()


@auth.verify_password
def verify_password(username, password):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        return username
    return None


@app.route("/register", methods=["POST"])
def register_user():
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = generate_password_hash(password)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Username already exists"}), 400
    conn.close()

    return jsonify({"message": "User registered successfully"}), 201


def get_private_key(username):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT private_key FROM keys WHERE username=?", (username,))
    private_key = cursor.fetchone()
    conn.close()

    if private_key:
        return private_key[0]
    return None


@app.route("/generate_keys", methods=["GET"])
@auth.login_required
def generate_keys():
    username = auth.current_user()

    # Generate RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    public_key = private_key.public_key()

    # Serialize keys
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    # Store keys in database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO keys (username, public_key, private_key) VALUES (?, ?, ?)",
        (username, public_key_pem, private_key_pem),
    )
    conn.commit()
    conn.close()

    return jsonify({"public_key": public_key_pem})


@app.route("/webhook_event", methods=["POST"])
@auth.login_required
def register_event():
    username = auth.current_user()
    data = request.json.get("data")
    print(username, data)
    if not data:
        return jsonify({"error": "No data provided"}), 400

    data = data.encode("utf-8")
    private_key_pem = get_private_key(username)

    if not private_key_pem:
        return jsonify({"error": "Private key not found"}), 404

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("utf-8"), password=None, backend=default_backend()
    )
    print(private_key)
    print(data)
    try:
        print("Hi")
        encrypted_data = base64.b64decode(data)
        decrypted_data = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        ).decode("utf-8")
        print("data")
        print(decrypted_data)
    except Exception as e:
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 400

    conn = sqlite3.connect(decrypt_db_file)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO decrypted_data (username, data) VALUES (?, ?)",
        (username, decrypted_data),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Event received and decrypted"}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
