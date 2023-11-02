from server import db
from datetime import datetime

class Medicine(db.Model):
    med_id = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    thubLink = db.Column(db.String(255), nullable=False)
    effect_type = db.Column(db.String(2), nullable=False)
    effect = db.Column(db.Text, nullable=False)
    usage_type = db.Column(db.String(2), nullable=False)
    usage = db.Column(db.Text, nullable=False)
    caution_type = db.Column(db.String(2), nullable=False)
    caution = db.Column(db.Text, nullable=False)

class User(db.Model):
    user_id = db.Column(db.String(12), primary_key=True)
    auth = db.Column(db.String(20), nullable=False, default='common')
    password = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    birthday = db.Column(db.DateTime, nullable=False)
    gender = db.Column(db.String(2), nullable=False)
    phone = db.Column(db.String(17), nullable=False)

class User_log(db.Model):
    user_log_id = db.Column(db.String(12), primary_key=True)
    user_id = db.Column(db.String(12), nullable=False)
    med_id = db.Column(db.String(12), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rate = db.Column(db.Integer, nullable=False)

class Check_log(db.Model):
    check_log_id = db.Column(db.String(12), primary_key=True)
    user_id = db.Column(db.String(12), nullable=False)
    med_id = db.Column(db.String(12), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rate = db.Column(db.Integer, nullable=False)

# key, seq 모음
class ID_seq(db.Model):
    ID = db.Column(db.String(3), primary_key=True)
    seq = db.Column(db.Integer, nullable=False)
