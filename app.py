from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user, current_user
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'stocks.sqlite'
app.config['SECRET_KEY'] = "act07-app1.py.pngDownload act07-app1.py.png (282 KB)"
db = SQLAlchemy(app)

@app.route('/create', methods =['POST','GET'])
def create():
    if request.method == 'GET':
        return render_template('create.html')
    elif request.method == 'POST':
        username = request.form['swimmer']
        password = request.form['height']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return render_template('portfolio.html')
