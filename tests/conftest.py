import os
import tempfile
import pytest
from app import create_app, db as _db
from app.models import User, Link, Click


class TestConfig:
    """کانفیگ مخصوص تست"""
    TESTING = True
    WTF_CSRF_ENABLED = False  # CSRF رو خاموش کن تا راحت‌تر تست کنیم
    SECRET_KEY = 'test-secret-key'
    BASE_URL = 'http://localhost'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # دیتابیس در حافظه
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    QRCODE_FOLDER = tempfile.mkdtemp()


@pytest.fixture(scope='session')
def app():
    """ساخت اپ برای همه تست‌ها"""
    app = create_app('development')
    app.config.from_object(TestConfig)
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
    """کلاینت تست"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner"""
    return app.test_cli_runner()


# ===== Fixtureهای داده =====

@pytest.fixture
def user(db):
    """یه کاربر معمولی"""
    u = User(username='ali', email='ali@test.com')
    u.set_password('password123')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def admin(db):
    """یه ادمین"""
    u = User(username='admin', email='admin@test.com', is_admin=True)
    u.set_password('admin123')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def auth_client(client, user):
    """کلاینت لاگین‌شده"""
    client.post('/auth/login', data={
        'username': 'ali',
        'password': 'password123'
    }, follow_redirects=True)
    return client


@pytest.fixture
def link(db, user):
    """یه لینک نمونه"""
    l = Link(
        short_code='abc123',
        original_url='https://example.com',
        title='نمونه',
        user_id=user.id,
    )
    db.session.add(l)
    db.session.commit()
    return l
