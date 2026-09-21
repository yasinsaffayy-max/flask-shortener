import os
import tempfile
import pytest
from app import create_app, db as _db
from app.models import User, Link, Click


# پوشه temp برای QR Codeها
QRCODE_TMP = os.path.join(tempfile.gettempdir(), 'qrcodes_test')
os.makedirs(QRCODE_TMP, exist_ok=True)


class TestConfig:
    """کانفیگ مخصوص تست"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key-for-ci'
    BASE_URL = 'http://localhost'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'   # ← دیتابیس در حافظه
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    QRCODE_FOLDER = QRCODE_TMP


@pytest.fixture(scope='session')
def app():
    """ساخت اپ برای همه تست‌ها"""
    # کانفیگ تست رو به دیکشنری config اضافه کن
    from config import config
    config['test'] = TestConfig

    # حالا با config درست، اپ رو بساز
    app = create_app('test')
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db(app):
    """دیتابیس تمیز برای هر تست"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def user(db):
    u = User(username='ali', email='ali@test.com')
    u.set_password('password123')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def admin(db):
    u = User(username='admin', email='admin@test.com', is_admin=True)
    u.set_password('admin123')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def auth_client(client, user):
    client.post('/auth/login', data={
        'username': 'ali',
        'password': 'password123'
    }, follow_redirects=True)
    return client


@pytest.fixture
def link(db, user):
    l = Link(
        short_code='abc123',
        original_url='https://example.com',
        title='نمونه',
        user_id=user.id,
    )
    db.session.add(l)
    db.session.commit()
    return l
