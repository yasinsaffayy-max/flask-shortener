import secrets
import string
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


def generate_short_code(length=6):
    """ساخت کد کوتاه یکتا"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    links = db.relationship('Link', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Link(db.Model):
    __tablename__ = 'links'

    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    original_url = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(200))
    clicks_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_creator = db.Column(db.String(45))  # برای لینک‌های ناشناس

    clicks = db.relationship('Click', backref='link', lazy=True, cascade='all, delete-orphan')

    def is_expired(self):
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False

    def is_available(self):
        return self.is_active and not self.is_expired()

    @staticmethod
    def generate_unique_code():
        """کد کوتاه یکتا بساز"""
        while True:
            code = generate_short_code(6)
            if not Link.query.filter_by(short_code=code).first():
                return code

    def __repr__(self):
        return f'<Link {self.short_code}>'


class Click(db.Model):
    __tablename__ = 'clicks'

    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('links.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    referer = db.Column(db.Text)
    country = db.Column(db.String(2))         # US, IR, ...
    browser = db.Column(db.String(50))        # Chrome, Firefox, ...
    os = db.Column(db.String(50))             # Windows, Android, ...
    device = db.Column(db.String(20))         # mobile, tablet, pc
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Click {self.id} on {self.link_id}>'
