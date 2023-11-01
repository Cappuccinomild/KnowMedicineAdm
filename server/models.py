from server import db

class Medicine(db.Model):
    MED_ID = db.Column(db.Text(), primary_key=True)
    Name = db.Column(db.Text(), nullable=False)
    ThubLink = db.Column(db.Text(), nullable=False)
    Effect_Type = db.Column(db.Text(), nullable=False)
    Effect = db.Column(db.Text(), nullable=False)
    Usage_Type = db.Column(db.Text(), nullable=False)
    Usage = db.Column(db.Text(), nullable=False)
    Caution_Type = db.Column(db.Text(), nullable=False)
    Caution = db.Column(db.Text(), nullable=False)

class User(db.Model):
    USR_ID = db.Column(db.Text(), primary_key=True)
    Password = db.Column(db.Text(), nullable=False)
    Name = db.Column(db.Text(), nullable=False)
    Birthday = db.Column(db.DateTime(), nullable=False)
    Gender = db.Column(db.Text(), nullable=False)
    Phone = db.Column(db.Text(), nullable=False)
    