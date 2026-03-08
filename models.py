from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Crop(db.Model):
    __tablename__ = 'crops'
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    crop_name = db.Column(db.String(100))
    land_area = db.Column(db.Float)
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(10))
    rate = db.Column(db.Float)
    harvest_date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    seller = db.relationship('User', backref='crops')

class Interest(db.Model):
    __tablename__ = 'interests'
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(10), default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    crop = db.relationship('Crop', backref='interests')
    buyer = db.relationship('User', backref='interests')

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user = db.relationship('User', backref='notifications')