from flask import Flask,render_template,request,session,redirect,flash
import bcrypt
from flask_sqlalchemy import SQLAlchemy
import pyotp
import qrcode
import os
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = '45534343'
db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True)
    password=db.Column(db.String(200))
    totp_secret=db.Column(db.String(32))

@app.route('/')
def index():
    name=session.get('username') 
    return render_template('index.html',username=name)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        bayt=password.encode('utf-8')
        hash=bcrypt.hashpw(bayt,bcrypt.gensalt())
        nobayt=hash.decode('utf-8')
        session['username']=username
        totp_secret=pyotp.random_base32()
        new_user=User(username=username,password=nobayt,totp_secret=totp_secret)
        user=User.query.filter_by(username=username).first()
        if user:
            flash('Пользоватаель уже существует')
        else:
            flash('Создать нового пользователя')
            db.session.add(new_user)
            db.session.commit()
            session['totp_secret']=totp_secret
            return redirect('/setup-2fa'    )
    else:
        pass
    return render_template('register.html')

@app.route('/setup-2fa')
def setup():
    totp_username=session['username']
    totp_secret =session['totp_secret']
    totp = pyotp.TOTP(totp_secret)
    uri = totp.provisioning_uri(name=totp_username, issuer_name='2FA_App')
    img = qrcode.make(uri)
    img.save(os.path.join(app.root_path, 'static', 'qrcode.png'))
    return render_template('setup_2fa.html')

@app.route('/verify-2fa',methods=['GET','POST'])
def verify():
    if 'username'  not in  session:
        return redirect('/login')
    if request.method=='POST':
        code=request.form['code']
        username=session['username']
        user=User.query.filter_by(username=username).first()
        totp = pyotp.TOTP(user.totp_secret)
        verify=totp.verify(code)
        if verify==True:
            session['just_logged_in'] = True
            return redirect('/')
        
        else:
            flash('Неверный код')
    return render_template('verify_2fa.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user=User.query.filter_by(username=username).first()
        if user:
            password_bayt=password.encode('utf-8')
            hash_bayt=user.password.encode('utf-8')
            check=bcrypt.checkpw(password_bayt,hash_bayt)


            if check==True:
                session['user_id']=user.id
                session['username']=username
                return redirect('/verify-2fa')
            else:
                flash('Неверный пароль')
        else:
            flash('Пользователь не найден')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True)