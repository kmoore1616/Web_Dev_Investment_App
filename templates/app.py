from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user, current_user
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hw7.sqlite'
app.config['SECRET_KEY'] = "act07-app1.py.pngDownload act07-app1.py.png (282 KB)" 
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.init_app(app)


class User(UserMixin, db.Model):    # User Table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    age = db.Column(db.String, nullable=False) 

with app.app_context(): # BP
    db.create_all()

@login_manager.user_loader  # BP
def load_user(uid):
    return User.query.get(uid)

@app.route('/')
def index():
    return render_template('home.html', is_authenticated=current_user.is_authenticated)


@app.route('/view_all') 
@login_required
def view_all():
    users = User.query.all()
    return render_template("view_all.html", users=users)

@app.route('/update', methods=["GET","POST"])
@login_required
def update():
    user=current_user
    if request.method == "GET":
        return render_template("update.html", is_authenticated=current_user.is_authenticated, error_msg = False)
    else:
        current_pswd = request.form["current_pswd"]
        new_pswd = request.form["new_pswd"]
        user=User.query.filter_by(username=user.username).first()
        if not current_pswd == user.password:
            return render_template("update.html", is_authenticated=current_user.is_authenticated, error_msg = True)
        else:
            user.password = new_pswd
            db.session.commit()
            return redirect("/")

@app.route('/create', methods=["GET", "POST"])  
def create():
    if current_user.is_authenticated:   # Safety Stuff
        return redirect("/")
    
    if request.method=="GET":
        return render_template("create.html", is_authenticated=current_user.is_authenticated, error_msg = False)
    else:
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']

        user = User(username=username)  # Create new instance
        user.name=name 
        user.password = password
        user.age = age
        db.session.add(user)
        try:                        # Here is the exception handling you thought I should look into. Check out this if you want to know more...
            db.session.commit()     # https://stackoverflow.com/questions/52075642/how-to-handle-unique-data-in-sqlalchemy-flask-python
        except IntegrityError:
            db.session.rollback() 
            return render_template("create.html", is_authenticated=current_user.is_authenticated, error_msg = True)
        login_user(user)
        return redirect("/")

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
            return redirect("/")
        else: 
            return render_template('login.html', is_authenticated=current_user.is_authenticated, error_msg=True)



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("logout.html")

@app.errorhandler(404)
def e404(err):
    return render_template("404.html")

app.run(debug=True)
