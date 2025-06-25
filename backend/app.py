from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import random
import string
from models import db, User, Booking, Counter
from utils import generate_token, send_notification
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = os.urandom(24)

# MongoDB Configuration
app.config['MONGODB_SETTINGS'] = {
    'db': 'easybook',
    'host': 'mongodb://localhost:27017/easybook'
}

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'zigzagerror007@gmail.com'
app.config['MAIL_PASSWORD'] = 'mhmn gval qele knvm'
app.config['MAIL_DEFAULT_SENDER'] = 'zigzagerror007@gmail.com'

mail = Mail(app)
db.init_app(app)

# Slot configuration
SLOT_DURATION = 15  # minutes
WORKING_HOURS = {
    'start': 9,
    'end': 16.5,
    'break_start': 12,
    'break_end': 13
}

@app.context_processor
def inject_datetime():
    return {'datetime': datetime}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.objects(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = str(user.id)
            session['email'] = user.email
            session['name'] = user.name
            session['roll_no'] = user.roll_no
            return redirect(url_for('counters'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        roll_no = request.form['roll_no']
        password = generate_password_hash(request.form['password'])
        
        if User.objects(email=email).first():
            return render_template('register.html', error="Email already registered")
        
        user = User(name=name, email=email, roll_no=roll_no, password=password)
        user.save()
        
        session['user_id'] = str(user.id)
        session['email'] = user.email
        session['name'] = user.name
        session['roll_no'] = user.roll_no
        
        return redirect(url_for('counters'))
    return render_template('register.html')

@app.route('/counters')
def counters():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    selected_date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

    counters_data = []
    for counter in Counter.objects():
        slots = generate_time_slots(selected_date, str(counter.id))
        available_slots = sum(1 for s in slots if s['available'])
        booked_slots = sum(1 for s in slots if not s['available'])

        counters_data.append({
            'id': str(counter.id),
            'name': counter.name,
            'type': counter.type,
            'available_slots': available_slots,
            'booked_slots': booked_slots,
            'date': selected_date_str
        })

    return render_template('counters.html',
                           counters=counters_data,
                           selected_date=selected_date_str)

@app.route('/book/<counter_id>', methods=['GET', 'POST'])
def book(counter_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    counter = Counter.objects(id=counter_id).first()
    if not counter:
        return redirect(url_for('counters'))

    selected_date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()

    time_slots = generate_time_slots(selected_date, counter_id)

    if request.method == 'POST':
        slot_time = request.form['slot_time']
        date = request.form['date']

        slot_datetime = datetime.strptime(f"{date} {slot_time}", '%Y-%m-%d %H:%M')
        if slot_datetime < datetime.now():
            flash('Cannot book a slot that has already passed', 'error')
            return redirect(url_for('book', counter_id=counter_id, date=date))

        token = generate_token(session['name'], session['roll_no'])
        booking = Booking(
            user_id=session['user_id'],
            counter_id=counter_id,
            date=datetime.strptime(date, '%Y-%m-%d'),
            time=slot_time,
            token=token,
            status='booked'
        )
        booking.save()

        send_notification(
            email=session['email'],
            subject="EasyBook - Fee Payment Slot Confirmation",
            message=f"Your slot is confirmed for {date} at {slot_time}. Your token is {token}."
        )

        return redirect(url_for('confirmation', booking_id=str(booking.id)))

    return render_template('booking.html',
                           counter=counter,
                           time_slots=time_slots,
                           selected_date=selected_date_str)

@app.route('/confirmation/<booking_id>')
def confirmation(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    booking = Booking.objects(id=booking_id, user_id=session['user_id']).first()
    if not booking:
        return redirect(url_for('counters'))

    counter = Counter.objects(id=booking.counter_id).first()
    return render_template('confirmation.html', booking=booking, counter=counter)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.objects(id=session['user_id']).first()
    bookings = Booking.objects(user_id=session['user_id']).order_by('-date', '-time')

    return render_template('profile.html', user=user, bookings=bookings, datetime=datetime)

@app.route('/cancel_booking/<booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    booking = Booking.objects(id=booking_id, user_id=session['user_id']).first()
    if booking:
        booking.status = 'cancelled'
        booking.save()

        send_notification(
            email=session['email'],
            subject="EasyBook - Booking Cancelled",
            message=f"Your slot for {booking.date.strftime('%Y-%m-%d')} at {booking.time} has been cancelled."
        )

    return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/api/time_slots')
def get_time_slots():
    counter_id = request.args.get('counter_id')
    date_str = request.args.get('date')

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except:
        return jsonify({'error': 'Invalid date format'}), 400

    time_slots = generate_time_slots(date, counter_id)
    return jsonify(time_slots)

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    return jsonify({'status': 'success', 'booking_id': '123'})

def generate_time_slots(date, counter_id):
    slots = []
    now = datetime.now()
    current_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=WORKING_HOURS['start'])
    end_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=WORKING_HOURS['end'])

    while current_time < end_time:
        if WORKING_HOURS['break_start'] <= current_time.hour < WORKING_HOURS['break_end']:
            current_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=WORKING_HOURS['break_end'])
            continue

        slot_end = current_time + timedelta(minutes=SLOT_DURATION)
        if slot_end > end_time:
            break

        is_past = current_time < now
        existing_booking = None
        if not is_past:
            existing_booking = Booking.objects(
                counter_id=counter_id,
                date=date,
                time=current_time.strftime('%H:%M'),
                status='booked'
            ).first()

        slots.append({
            'time': current_time.strftime('%H:%M'),
            'available': not existing_booking and not is_past,
            'is_past': is_past
        })

        current_time = slot_end

    return slots

def initialize_counters():
    with app.app_context():
        if Counter.objects.count() == 0:
            Counter(name="Counter 1", type="card").save()
            Counter(name="Counter 2", type="card").save()
            Counter(name="Counter 3", type="cash").save()
            print("Initialized default counters")

initialize_counters()

if __name__ == '__main__':
    app.run(debug=True)
