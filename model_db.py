from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    source = db.Column(db.String(250))
    image_url = db.Column(db.String(250))
    date_posted = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<News {self.title}>'

class Admin(db.Model, UserMixin):
    __tablename__ = 'admin_creds'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='admin')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='scrypt')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Inquiry(db.Model):
    __tablename__ = 'inquiries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

def add_inquiry(name, email, subject, message):
    new_inquiry = Inquiry(
        name=name,
        email=email,
        subject=subject,
        message=message
    )
    db.session.add(new_inquiry)
    db.session.commit()

def get_inquiries():
    return Inquiry.query.order_by(Inquiry.timestamp.desc()).all()

def get_inquiry_by_id(inquiry_id):
    return Inquiry.query.get(inquiry_id)
