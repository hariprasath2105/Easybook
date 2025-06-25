from flask_mongoengine import MongoEngine
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = MongoEngine()

class User(db.Document):
    name = db.StringField(required=True)
    email = db.StringField(required=True, unique=True)
    roll_no = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.utcnow)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Counter(db.Document):
    name = db.StringField(required=True)
    type = db.StringField(required=True, choices=('card', 'cash'))
    description = db.StringField()

class Booking(db.Document):
    user_id = db.StringField(required=True)
    counter_id = db.StringField(required=True)
    date = db.DateTimeField(required=True)
    time = db.StringField(required=True)
    token = db.StringField(required=True)
    status = db.StringField(choices=('booked', 'completed', 'cancelled'), default='booked')
    created_at = db.DateTimeField(default=datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.utcnow)