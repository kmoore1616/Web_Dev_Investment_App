from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user, current_user
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'stocks.sqlite'
app.config['SECRET_KEY'] = "act07-app1.py.pngDownload act07-app1.py.png (282 KB)"
db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)

class Portfolio(db.Model):
    portfolio_id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String)
    cash = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    
class Stock(db.Model):
    stock_id = db.Column(db.Integer,primary_key=True)
    symbol = db.Column(db.String)
    amount = db.Column(db.Integer)
    date_purchased = db.Column(db.Integer)    # This is important to find gains/losses from a stock. Im not sure how sqlite formats dates
    portfolio_id =  db.Column(db.Integer, db.ForeignKey('portfolio.portfolio_id'))

@app.route('/create_user', methods =['POST','GET'])
def create_user():
    if request.method == 'GET':
        return render_template('create.html')
    elif request.method == 'POST':
        username = request.form['swimmer']
        password = request.form['height']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return render_template('portfolio.html')
    
@app.route('/create_stock', methods =['POST','GET'])
def create_stock():
    if request.method == 'GET':
        return render_template('create.html')
    elif request.method == 'POST':
        symbol = request.form['symbol']
        amount = request.form['amount']
        cash = request.form['cash']
        stock = Stock(symbol=symbol, amount=amount, cash=cash)
        db.session.add(stock)
        db.session.commit()
        return render_template('portfolio.html')

@app.route('/update_user/<id>', methods = ['GET','POST'])
def update_portfolio(id):
    portfolio_id = int(id)
    portfolio = Portfolio.query.filter_by(id=portfolio_id).first()
    if request.method == 'GET':
        return render_template('update.html',portfolio=portfolio)
    elif request.method == 'POST':
        name = request.form['name']
        cash = request.form['cash']
        
        portfolio.name = name
        portfolio.cash = cash
        db.session.commit()
        return render_template('portfolio.html')

@app.route('/update_stock/<id>', methods=['GET', 'POST'])
def update_stock(id):
    stock_id = int(id)
    stock = Stock.query.filter_by(id=stock_id).first()
    if request.method == 'GET':
        return render_template('update.html', stock=stock)
    elif request.method == 'POST':
        symbol = request.form['symbol']
        amount = request.form['amount']
        price_purchased = request.form['price_purchased']

        stock.symbol = symbol
        stock.amount = amount
        stock.price_purchased = price_purchased
        db.session.commit()
        return render_template('portfolio.html')

@app.route('/delete_stock/<id>', methods=['POST'])
def delete_stock(id):
    stock_id = int(id)
    stock = Stock.query.filter_by(id=stock_id).first()
    db.session.delete(stock)
    db.session.commit()
    return render_template('portfolio.html')

if __name__ == '__main__':
    app.run(debug=True)
