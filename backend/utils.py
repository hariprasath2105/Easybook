from flask_mail import Message
from datetime import datetime
import random
import string

def generate_token(name, roll_no):
    first_letter = name[0].upper() if name else 'X'
    last_four = roll_no[-4:] if roll_no and len(roll_no) >= 4 else '0000'
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{first_letter}-EB-{last_four}-{random_part}"

def send_notification(email, subject, message):
    from app import mail
    try:
        msg = Message(
            subject=subject,
            recipients=[email],
            body=message
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False