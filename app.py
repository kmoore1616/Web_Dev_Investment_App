from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from dataclasses import dataclass
import requests
from datetime import date


# Boilerplate
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.sqlite'
app.config['SECRET_KEY'] = "act07-app1.py.pngDownload act07-app1.py.png (282 KB)"
db = SQLAlchemy(app)


login_manager = LoginManager(app)
login_manager.init_app(app)

# Api Key
key = "DL4qPHbMNiz6ke4JJ5SywYYkW5HTaxQw7mi98yQv" # Bad!

# ========================================= STOCK INFORMATION GATHERING ===============================================

# Basically a C struct. Should've just a dict in hindsight
# Used to hold data from all stocks in a protfolio
@dataclass
class Stock_struct:
    symbol: str
    shares: float
    price: float
    profit: float

# Organizes relavant data from a user's portfolio into an array of Stock_structs
def get_stocks():
    user_portfolio = Portfolio.query.filter_by(portfolio_id=current_user.user_id).first() # Get user portfolio
    stocks = Stock.query.filter_by(portfolio_id=user_portfolio.portfolio_id).all() # Get user's stocks
    user_stocks = []    # Array to hold structs
    for stock in stocks:    # Iterate through all stock objects user has in portfolio
        purchase_date = stock.date_purchased    # Grab purchase date to determine original price.
        sd = get_stock_data(stock.symbol, purchase_date)  # get_stock_data call api to determine stocks current and original price in an array
        o_price = sd[0]     # First element holds original price
        cur_price = sd[1]   # Second holds current price
        cur_profit = (float(cur_price) - float(o_price)) * stock.amount     # Calculates profit
        new_stock = Stock_struct(       # Assemble a s new stock struct
                symbol = stock.symbol,
                shares = stock.amount,
                price = cur_price,
                profit = cur_profit
        )
        user_stocks.append(new_stock)   # Append struct to final array

    return user_stocks  # Return the built array


# Gets original and present data from a stock
def get_stock_data(stock_symbol, date):
    sd = []     # Array to hold the original and current price of the stock
    url = f"https://api.stockdata.org/v1/data/eod?symbols={stock_symbol}&date_from={date}&date_to={date}&api_token={key}" # URL to grab data from when stock was purchased. Note: User cannot purchase stocks on invalid days (IE market is closed) so this call should never fail
    stock_data = requests.get(url)  # Make the API call
    stock_data = stock_data.json()  # Turn into JSON (Python Dict)
    try:
        sd.append(stock_data['data'][0]['close'])   # If purchased on same day, before data for said stock is released, this grabs data from day prior
    except:
        day = date[-2:]     # Grab last two chars from date IE 2024-12-12. Grabs the 12
        date = date[:-2]    # Strips last to chars from date IE 2024-12-
        date = date + str(int(day)-1)   # Goes back a day and reappends day to date IE 2024-12-11
        url = f"https://api.stockdata.org/v1/data/eod?symbols={stock_symbol}&date_from={date}&date_to={date}&api_token={key}"   # Rebuild URL
        stock_data = requests.get(url)  # Make new call
        stock_data = stock_data.json()
        sd.append(stock_data['data'][0]['close'])   # Append original purchase data to SD

    url = f"https://api.stockdata.org/v1/data/eod?symbols={stock_symbol}&api_token={key}"   # Build url to grab latest stock price
    stock_data = requests.get(url)  # Send the API request
    stock_data = stock_data.json()
    sd.append(stock_data['data'][0]['close'])   # Append current purchase data to SD
    return sd   # and return it




# =========================================== DB STUFF ====================================================================

# User table. Used for login authentication
class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)


    def get_id(self):
        return str(self.user_id)  # Had to rework this method so it returns the actual user.user_id instead of just user.id


# Portfolio table, connected with both User and Stock
# A user has a portfolio and a portfolio contains stocks
class Portfolio(db.Model):
    portfolio_id = db.Column(db.Integer,primary_key=True)
    cash = db.Column(db.REAL)   # Liquid Capital
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def get_id(self):
        return str(self.user_id)  # See above

# Stock table. Keeps track of what stocks user is vested in
class Stock(db.Model):
    stock_id = db.Column(db.Integer,primary_key=True)
    symbol = db.Column(db.String)
    amount = db.Column(db.REAL)
    date_purchased = db.Column(db.String) #"2021-11-11"    # This is important to find gains/losses from a stock.
    portfolio_id =  db.Column(db.Integer, db.ForeignKey('portfolio.portfolio_id'))

    def get_id(self):
        return str(self.user_id)  # See above

# DB Boilerplate
with app.app_context():
    db.create_all()

# Login Boilerplate
@login_manager.user_loader
def load_user(uid):
    return User.query.get(uid)


# =========================================== FLASK ROUTES ================================================================


# "/" route not used, redirects to login. If logged in, redirects to portfolio (FINISHED)
@app.route("/")
def index():
    return redirect("/login")

# Create new account route
@app.route('/create', methods = ['POST','GET'])
def create_user():
    if request.method == 'GET':
        return render_template('create.html')
    elif request.method == 'POST':
        name = request.form['name']     # Grab Relevant Data
        username = request.form['username']
        password = request.form['password']

        user = User(name=name,username=username, password=password)     # Create new user object
        db.session.add(user)    # Add new user object to DB
        db.session.commit()     # and commit changes
        new_user_id = User.query.filter_by(username=username).first().user_id   # Grab newly formed user object's ID
        new_portfolio = Portfolio(cash=0, user_id=new_user_id)  # Create new portfolio object for new user
        db.session.add(new_portfolio)
        db.session.commit()
        return render_template('login.html') # Redirect user to login page



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




# Main route that is show relavant data to user. User can deposit/withdraw money & Invest in stocks & see current holdings
@app.route("/portfolio", methods=["GET", "POST"])
@login_required
def portfolio():
    user_portfolio = Portfolio.query.filter_by(user_id=current_user.user_id).first() # Get user portfolio
    cur_user = User.query.filter_by(user_id=current_user.user_id).first()

    # =============== GET ============================

    if request.method == "GET":
        stocks = get_stocks()   # Grab relevant stock information
        total_profit = 0.0      # Variable to store total profit
        for stock in stocks:
            total_profit += stock.profit   # Calculate total profit
        return render_template("portfolio.html", stocks = stocks, cash = user_portfolio.cash, total_profit = total_profit, name=cur_user.name) # Send relavant data to jinja template (See portfolio.html)

    # ============== DEPOSIT ========================

    elif request.form.get("action") == "deposit":   # Assumes POST request
        try:
            cash = float(request.form["cash_add"])  # Try to get user input for deposit
        except:
            flash("Invalid input")     # If invalid entry flash user (basically sends an alert from the html)
            return redirect("/portfolio")    # Redirect user to try again after error message is cleared
        user_portfolio.cash += cash     # If valid entry add cash to user's portfolio
        db.session.commit()
        return redirect("/portfolio")   # Re-render the page

    # ============= WITHDRAW =======================

    elif request.form.get("action") == "withdraw":
        try:
            cash = float(request.form["cash_remove"])   # Same logic as above
        except:
            flash("Invalid input")
            return redirect("/portfolio")
        user_portfolio.cash -= cash     # Withdraw cash from user's portfolio
        db.session.commit()
        return redirect("/portfolio")


    # ============ TRADE-BUY ==========================

    elif request.form.get("action") == "buy":
        cur_date = date.today()     # Grab current date
        if(cur_date.weekday() >= 5):    # Determine if it's a valid trading day
            flash("Markets Closed")     # If not inform user
            return redirect("/portfolio")   # and re-render page
        symbol = request.form.get("symbol") # If valid trading day get user's input
        try:
            amount = float(request.form.get("amount"))  # Make sure input is valid
        except:
            flash("Invalid input!") # If not inform user and re-render
            return redirect("/portfolio")
        response = requests.get(f"https://api.stockdata.org/v1/data/quote?symbols={symbol}&api_token={key}").json() # Make API call to get most recent price
        price = float(response['data'][0]['price'])     # Get price from response
        try:
            price = float(response['data'][0]['price'])     # Get price from response
        except:
            flash("Error, stock not found...")      # If stock doesnt exist inform user
            return redirect("/portfolio")
        cost = price*amount     # Calculate how much it will cost the user
        if(cost > user_portfolio.cash):
            flash("Not Enough Cash to Complete Trade!") # If too much inform user & re-render
            return redirect("/portfolio")
        user_portfolio.cash -= cost     # If user can afford it, subtract cost from cash
        new_stock = Stock(symbol=symbol, amount=amount, date_purchased=cur_date, portfolio_id=user_portfolio.portfolio_id)  # Add new stock to user's portfolio
        db.session.add(new_stock)
        db.session.commit() # Commit changes to DB


    # ============ TRADE-SELL ==========================
    elif request.form.get("action") == "sell":
        cur_date = date.today()     # Grab current date
        if(cur_date.weekday() >= 5):    # Determine if it's a valid trading day
            flash("Markets Closed")     # If not inform user
            return redirect("/portfolio")   # and re-render page
        symbol = request.form.get("symbolTS") # If valid trading day get user's input
        stock_TS = Stock.query.filter_by(portfolio_id=user_portfolio.portfolio_id, symbol = symbol).first()
        if stock_TS is None:
            flash("Stock not found, check your spelling...")    # If stock not in portfolio inform user
            return redirect("/portfolio")
        try:
            amount = float(request.form.get("amountTS"))  # Make sure input is valid
        except:
            flash("Invalid input!") # If not inform user and re-render
            return redirect("/portfolio")
        response = requests.get(f"https://api.stockdata.org/v1/data/quote?symbols={symbol}&api_token={key}").json() # Make API call to get most recent price
        price = float(response['data'][0]['price'])     # Get price from response
        holdings = price * stock_TS.amount      # Calculate how much user owns
        cost = price * amount       # Calculate how much user wants to sell
        if cost > holdings:     # Make sure user cant sell more than they have
            flash("Cost exceeds current holdings...")   # Inform user if they do
            return redirect("/portfolio")
        shares = amount/price   # Calculate how many shares user will sell
        stock_TS.amount -= shares   # Subtract that from their portfolio
        user_portfolio.cash += cost
        db.session.commit()

    else:
        return redirect("/portfolio")



@app.errorhandler(404)
def e404(err):
    return render_template("404.html")

@app.errorhandler(401)
def e401(err):
    return redirect("/login")

@app.errorhandler(403)
def e403(err):
    return redirect("/login")


if __name__ == '__main__':
    app.run(debug=True)
