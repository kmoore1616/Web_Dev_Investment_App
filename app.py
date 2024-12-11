from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from flask_socketio import SocketIO, send, emit
from dataclasses import dataclass

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.sqlite'
app.config['SECRET_KEY'] = "act07-app1.py.pngDownload act07-app1.py.png (282 KB)"
db = SQLAlchemy(app)

socketio = SocketIO(app)

login_manager = LoginManager(app)
login_manager.init_app(app)

# ************************************************************ DB STUFF ****************************************************

@dataclass
class Portfolio_struct:
    cash: float
    symbol: str
    shares: int
    price: float
    color: str
    profit: float


class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)


    def get_id(self):
        return str(self.user_id)  # Flask-Login requires the ID to be a string

class Portfolio(db.Model):
    portfolio_id = db.Column(db.Integer,primary_key=True)
    cash = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def get_id(self):
        return str(self.user_id)  # Flask-Login requires the ID to be a string

class Stock(db.Model):
    stock_id = db.Column(db.Integer,primary_key=True)
    symbol = db.Column(db.String)
    amount = db.Column(db.Integer)
    date_purchased = db.Column(db.Integer)    # This is important to find gains/losses from a stock. Im not sure how sqlite formats dates
    portfolio_id =  db.Column(db.Integer, db.ForeignKey('portfolio.portfolio_id'))

    def get_id(self):
        return str(self.user_id)  # Flask-Login requires the ID to be a string


with app.app_context(): # BP
    db.create_all()

@login_manager.user_loader
def load_user(uid):
    return User.query.get(uid)



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
        return render_template('login.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method=="GET":
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


@app.route("/portfolio", methods=["GET", "POST"])
@login_required
def portfolio():
    adj = []
    portfolio = Portfolio_struct(
        cash=10000.0,
        symbol="AAPL",
        shares=50,
        price=150.0,
        color="green",
        profit=500.0
        )
    adj.append(portfolio)


    portfolio = Portfolio_struct(
        cash=10000.0,
        symbol="AAPL",
        shares=50,
        price=150.0,
        color="green",
        profit=500.0
        )

    adj.append(portfolio)

    return render_template("portfolio.html", portfolio = adj)

@app.route("/")
def index():
    return redirect("/portfolio")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("logout.html")

@socketio.on("message")
def get_stock_info(data):
    print(data)


@app.errorhandler(404)
def e404(err):
    return render_template("404.html")




if __name__ == '__main__':
    socketio.run(app, debug=True)
