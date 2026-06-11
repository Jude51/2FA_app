from flask import Flask, render_template, request, session, redirect, flash
import bcrypt
from flask_sqlalchemy import SQLAlchemy
import pyotp
import qrcode
import os
import smtplib
import random
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///users.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise RuntimeError('SECRET_KEY must be set in environment')

db = SQLAlchemy(app)

EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
if not EMAIL_SENDER or not EMAIL_PASSWORD:
    raise RuntimeError('EMAIL_SENDER and EMAIL_PASSWORD must be set in environment')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))
    totp_secret = db.Column(db.String(32))
    email = db.Column(db.String(120))
    auth_method = db.Column(db.String(10))

@app.route('/')
def index():
    name = session.get('username')
    return render_template('index.html', username=name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        auth_method = request.form['auth_method']
        email = request.form.get('email', '')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Пользователь уже существует')
        else:
            bayt = password.encode('utf-8')
            hash = bcrypt.hashpw(bayt, bcrypt.gensalt())
            nobayt = hash.decode('utf-8')
            totp_secret = pyotp.random_base32()
            new_user = User(username=username, password=nobayt, totp_secret=totp_secret, email=email, auth_method=auth_method)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            session['totp_secret'] = totp_secret
            session['auth_method'] = auth_method
            if auth_method == 'totp':
                return redirect('/setup-2fa')
            else:
                return redirect('/login')
    return render_template('register.html')

@app.route('/setup-2fa')
def setup():
    totp_username = session['username']
    totp_secret = session['totp_secret']
    totp = pyotp.TOTP(totp_secret)
    uri = totp.provisioning_uri(name=totp_username, issuer_name='2FA_App')
    img = qrcode.make(uri)
    img.save(os.path.join(app.root_path, 'static', 'qrcode.png'))
    return render_template('setup_2fa.html')

@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        code = request.form['code']
        username = session['username']
        user = User.query.filter_by(username=username).first()
        auth_method = user.auth_method

        if auth_method == 'totp':
            totp = pyotp.TOTP(user.totp_secret)
            result = totp.verify(code)
        else:
            result = (code == session.get('email_code'))

        if result:
            session['user_id'] = user.id
            return redirect('/')
        else:
            flash('Неверный код')
    return render_template('verify_2fa.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            password_bayt = password.encode('utf-8')
            hash_bayt = user.password.encode('utf-8')
            check = bcrypt.checkpw(password_bayt, hash_bayt)
            if check:
                session['user_id'] = user.id
                session['username'] = username
                if user.auth_method == 'email':
                    code = str(random.randint(100000, 999999))
                    session['email_code'] = code
                    send_email(user.email, code)
                return redirect('/verify-2fa')
            else:
                flash('Неверный пароль')
        else:
            flash('Пользователь не найден')
    return render_template('login.html')


def send_email(to_email, code):
    msg = MIMEText(f'Ваш код входа: {code}')
    msg['Subject'] = 'Код входа 2FA App'
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
