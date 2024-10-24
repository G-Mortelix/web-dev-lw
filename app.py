from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from extensions import db, mail
from user_routes import user_bp
from admin_routes import Admin, admin_bp, init_app as admin_init_app
from model_db import News, Inquiry, Admin

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('sec_key')
if not app.secret_key:
    raise ValueError("No secret key set for Flask application")

app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('db_url')
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise ValueError("No database URL set for Flask application")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  

with app.app_context():
    db.create_all()

csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = 'admin_bp.admin_login'

with app.app_context():
    db.create_all()

admin_init_app(app)

# Homepage route
@app.route('/')
def home():
    return render_template('home.html')

# Admin authentication loader
@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))

if __name__ == "__main__":
    app.run(debug=True)