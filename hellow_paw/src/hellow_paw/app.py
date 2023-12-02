import sqlite3
from datetime import datetime

from flask import Flask, render_template, request

app = Flask(__name__)


def init_db():
    with sqlite3.connect('../../data/log.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS logs
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         date_logged TEXT,
                         ip_address TEXT,
                         user_agent TEXT,
                         accepted_languages TEXT)''')


# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logs')
def logs():
    with sqlite3.connect('../../data/log.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT date_logged, ip_address FROM logs')
        logs = cursor.fetchall()
        return render_template('logs.html', logs=logs)


@app.route('/log', methods=['POST'])
def log_ip():
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    accepted_languages = request.headers.get('Accept-Language')
    date_logged = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect('../../data/log.db') as conn:
        conn.execute(
            'INSERT INTO logs (date_logged, ip_address, user_agent, accepted_languages) VALUES (?, ?, ?, ?)',
            (date_logged, ip_address, user_agent, accepted_languages))
    return '', 204

@app.route('/userinfo')
def user_info():
    with sqlite3.connect('../../data/log.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT date_logged, ip_address, user_agent, accepted_languages FROM logs ORDER BY date_logged DESC')
        all_logs = cursor.fetchall()
        return render_template('user_info.html', logs=all_logs)


if __name__ == "__main__":
    init_db()  # Initialize the database
    app.run(debug=True)  # Start the Flask application
