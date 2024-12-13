from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user, current_user
from dataclasses import dataclass
from requests import Request

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.sqlite'
app.config['SECRET_KEY'] = "act07-app1.py.pngDownload act07-app1.py.png (282 KB)"
db = SQLAlchemy(app)


login_manager = LoginManager(app)
login_manager.init_app(app)


@dataclass
class Stock_struct:
    symbol: str
    shares: float
    price: float
    profit: float

# Organizes relavant data from a user's portfolio
def get_stocks():
    user_portfolio = Portfolio.query.filter_by(portfolio_id=current_user.user_id).first() # Get user portfolio
    stocks = Stock.query.filter_by(portfolio_id=user_portfolio.portfolio_id).all() # Get user's stocks
    print("*** MORE DEBUG ***")
    print(stocks)
    user_stocks = []
    for stock in stocks:
        purchase_date = stocks.date_purchased
        sd = get_stock_data(stock.symbol, purchase_date)  # TODO Need to figure out how to do API Call
        o_price = sd[0]["close"]
        cur_price = sd[1]["close"]
        cur_profit = (float(cur_price) - float(o_price)) * stocks.amount
        new_stock = Stock_struct(
                symbol = stock.symbol,
                shares = stock.amount,
                price = cur_price,
                profit = cur_profit
        )
        user_stocks.append(new_stock)

    return user_stocks


# Gets original and present data from a stock
def get_stock_data(symbol, date_purchased):
    stock_data = []
    standin1 = { # TODO Tempoary Variable!! Replace with API Call
            "open": 145.67,
            "high": 146.50,
            "low": 144.50,
            "close": 145.00,
            "volume": 53456789,
            "symbol": "AAPL",
            "exchange": "NASDAQ",
            "date": "2021-10-03T00:00:00+0000"
    }
    stock_data.append(standin1)
    standin2 = { # TODO Tempoary Variable!! Replace with API Call
            "open": 145.67,
            "high": 146.50,
            "low": 144.50,
            "close": 246.49,
            "volume": 53456789,
            "symbol": "AAPL",
            "exchange": "NASDAQ",
            "date": "2024-12-11T00:00:00+0000"
    }
    stock_data.append(standin2)
    return stock_data

# ************************************************************ DB STUFF ****************************************************

# User table. Used for login authentication
class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)


    def get_id(self):
        return str(self.user_id)  # Flask-Login requires the ID to be a string


# Portfolio table, connected with both User and Stock
# A user has a portfolio and a portfolio contains stocks
class Portfolio(db.Model):
    portfolio_id = db.Column(db.Integer,primary_key=True)
    cash = db.Column(db.REAL)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def get_id(self):
        return str(self.user_id)  # Flask-Login requires the ID to be a string

# Stock table. Keeps track of what stocks user is vested in
class Stock(db.Model):
    stock_id = db.Column(db.Integer,primary_key=True)
    symbol = db.Column(db.String)
    amount = db.Column(db.REAL)
    date_purchased = db.Column(db.String) #"2021-11-11"    # This is important to find gains/losses from a stock. Im not sure how sqlite formats dates
    portfolio_id =  db.Column(db.Integer, db.ForeignKey('portfolio.portfolio_id'))

    def get_id(self):
        return str(self.user_id)  # Flask-Login requires the ID to be a string

# DB Boilerplate
with app.app_context():
    db.create_all()

# Login Boilerplate
@login_manager.user_loader
def load_user(uid):
    return User.query.get(uid)


# Create new account route (FINISHED)
@app.route('/create', methods = ['POST','GET'])
def create_user():
    if request.method == 'GET':
        return render_template('create.html')
    elif request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']

        user = User(name=name,username=username, password=password)
        db.session.add(user)
        db.session.commit()
        new_user_id = User.query.filter_by(username=username).first().user_id
        new_portfolio = Portfolio(cash=0, user_id=new_user_id)
        db.session.add(new_portfolio)
        db.session.commit()
        return render_template('login.html')


# TODO, Do these tables need to have routes?
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


# TODO, Do these tables need to have routes?
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


# TODO, Do these tables need to have routes?
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


# TODO, Do these tables need to have routes?
@app.route('/delete_stock/<id>', methods=['POST'])
def delete_stock(id):
    stock_id = int(id)
    stock = Stock.query.filter_by(id=stock_id).first()
    db.session.delete(stock)
    db.session.commit()
    return render_template('portfolio.html')

# Main route that is show relavant data to user. User can deposit/withdraw money & Invest in stocks
@app.route("/portfolio", methods=["GET", "POST"])
@login_required
def portfolio():
    user_portfolio = Portfolio.query.filter_by(portfolio_id=current_user.user_id).first() # Get user portfolio
    if request.method == "GET":
        stocks = get_stocks()
        total_profit = 0.0
        for stock in stocks:
            total_profit += stock.profit
        return render_template("portfolio.html", stocks = stocks, cash = user_portfolio.cash, total_profit = total_profit)
    elif request.form.get("action") == "deposit":
        user_portfolio.cash += float(request.form["cash_add"])
        db.session.commit()
        return redirect("portfolio")
    elif request.form.get("action") == "withdraw":
        user_portfolio.cash -= float(request.form["cash_remove"])
        db.session.commit()
        return redirect("portfolio")





# "/" route not used, redirects to login. If logged in, redirects to portfolio (FINISHED)
@app.route("/")
def index():
    return redirect("/login")

# Logs in user (FINISHED)
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method=="GET":
        if current_user.is_authenticated:
            return redirect("/portfolio")

        return render_template('login.html', is_authenticated=current_user.is_authenticated, error_msg=False)
    else:
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user is None:
            return render_template('login.html', is_authenticated=current_user.is_authenticated, error_msg=True)


        if user.password == password:
            login_user(user)
            return redirect("/portfolio")
        else:
            return render_template('login.html', is_authenticated=current_user.is_authenticated, error_msg=True)


# Logs User out
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("logout.html")


@app.errorhandler(404)
def e404(err):
    return render_template("404.html")


if __name__ == '__main__':
    app.run(debug=True)
