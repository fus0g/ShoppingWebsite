from os import path
from os.path import pathsep

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

loginManager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] =  "abcdefg"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)



    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    from .models import User
    from .models import Vendor
    create_database(app)

    loginManager.init_app(app)

    @loginManager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @loginManager.user_loader
    def load_user(id):
        return Vendor.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/'+DB_NAME):
        with app.app_context():
            db.create_all()
        print("created DB")