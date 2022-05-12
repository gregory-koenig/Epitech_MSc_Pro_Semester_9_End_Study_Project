import secrets
import smtplib
import sqlite3
import ssl
import time

from flask import Flask, request, render_template, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
con = sqlite3.connect('hopper.db', check_same_thread=False)
cur = con.cursor()
cur.executescript('''
    CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        surname TEXT,
        mail TEXT,
        company TEXT, 
        job_title TEXT,
        api_key TEXT
    );

    CREATE TABLE IF NOT EXISTS key_usage (
        key_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        time TIMESTAMP,
        api_key TEXT,
        user_id INTEGER NOT NULL
    );
    ''')
con.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register-confirm')
def register_confirm():
    return render_template('register_confirm.html')


@app.route('/resend')
def resend():
    return render_template('resend.html')


@app.route('/resend-confirm')
def resend_confirm():
    return render_template('resend_confirm.html')


@app.route('/api', methods=['GET'])
def api():
    return 'Hopper API is currently running...', 200


@app.route('/logo.png')
def logo():
    return render_template('logo.png')


@app.route('/api/register', methods=['GET', 'POST'])
def register_user():
    name = request.args.get('name')
    surname = request.args.get('surname')
    mail = request.args.get('mail')
    company = request.args.get('company')
    job_title = request.args.get('job_title')
    api_key = secrets.token_hex(16)

    cur.execute('INSERT INTO user (name, surname, mail, company, job_title, api_key) VALUES(?, ?, ?, ?, ?, ?)',
                (name, surname, mail, company, job_title, api_key))
    con.commit()

    sender_email = 'hopper.contact.info@gmail.com'
    receiver_email = mail
    password = 'jRQR699Qy5ri'

    message = MIMEMultipart('alternative')
    message['Subject'] = 'Your API key'
    message['From'] = sender_email
    message['To'] = receiver_email

    text = f'''\
    Hi,
    Welcome to Hopper!
    Here is your API key: {api_key}'''
    html = f'''\
    <html>
      <body>
        <p>Hi,<br>
           Welcome to Hopper!<br>
           Here is your API key: {api_key}
        </p>
      </body>
    </html>
    '''

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

    return render_template('register_confirm.html')


@app.route('/api/key/resend', methods=['GET', 'POST'])
def resend_api_key():
    mail = request.args.get('mail')
    cur.execute("SELECT * FROM user WHERE mail = '%s'" % mail)
    row = cur.fetchone()
    if row:
        sender_email = 'hopper.contact.info@gmail.com'
        receiver_email = mail
        password = 'jRQR699Qy5ri'

        message = MIMEMultipart('alternative')
        message['Subject'] = 'Your API key'
        message['From'] = sender_email
        message['To'] = receiver_email

        text = f'''\
            Hi,
            Here is your API key: {row[6]}'''
        html = f'''\
            <html>
              <body>
                <p>Hi,<br>
                   Here is your API key: {row[6]}
                </p>
              </body>
            </html>
            '''

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        message.attach(part1)
        message.attach(part2)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )

        return render_template('resend_confirm.html')
    else:
        return 'Mail not found', 404


@app.route('/api/model/exec', methods=['POST'])
def exec_model():
    content = request.json
    api_key = content['api_key']
    ast = content['ast']

    cur.execute("SELECT * FROM user WHERE api_key = '%s'" % api_key)
    row = cur.fetchone()
    if row:
        user_id = row[0]
        cur.execute('INSERT INTO key_usage (time, api_key, user_id) VALUES (?, ?, ?)',
                    (time.time(), api_key, user_id))
        con.commit()
        json = jsonify(algo_vec=[0, 0, 0, 0, 1, 2, 3])
        return json, 200
    else:
        return 'API key is invalid', 404
