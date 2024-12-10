from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user, current_user
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'stocks.sqlite'
app.config['SECRET_KEY'] = "act07-app1.py.pngDownload act07-app1.py.png (282 KB)"
db = SQLAlchemy(app)

class user(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

class portfolio(db.Model):
    portfolio_id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String)
    cash = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    
class stock(db.Model):
    stock_id = db.Column(db.Integer,primary_key=True)
    symbol = db.Column(db.String)
    amount = db.Column(db.Integer)
    price_purchased = db.Column(db.Integer)
    portfolio_id =  db.Column(db.Integer, db.ForeignKey('portfolio.portfolio_id'))

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

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    portfolio_id = int(id)
    user = User.query.filter_by(id=portfolio_id).first()
    db.session.delete(user)
    db.session.commit()
    return render_template('portfolio.html')
