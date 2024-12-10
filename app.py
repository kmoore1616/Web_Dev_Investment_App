from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, UserMixin, logout_user, current_user
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = **TODO Need to implement database**
app.config['SECRET_KEY'] = "act07-app1.py.pngDownload act07-app1.py.png (282 KB)"
db = SQLAlchemy(app)
