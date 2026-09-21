import pytest
from datetime import datetime, timedelta
from app.models import User, Link, Click, generate_short_code


class TestUserModel:
    def test_password_hashing(self, db):
        u = User(username='test', email='t@t.com')
        u.set_password('secret123')
        assert u.password_hash != 'secret123'
        assert u.check_password('secret123')
        assert not u.check_password('wrong')

    def test_user_creation(self, user):
        assert user.id is not None
        assert user.username == 'ali'
        assert user.email == 'ali@test.com'
        assert user.is_admin is False


class TestLinkModel:
    def test_generate_short_code(self):
        code = generate_short_code()
        assert len(code) == 6
        assert code.isalnum()

    def test_generate_unique_code(self, db):
        """کدهای یکتا ساخته بشن"""
        codes = set()
        for _ in range(50):
            codes.add(generate_short_code(6))
        # احتمال تصادم خیلی کمه، ولی چک می‌کنیم
        assert len(codes) > 45

    def test_link_creation(self, link):
        assert link.short_code == 'abc123'
        assert link.original_url == 'https://example.com'
        assert link.clicks_count == 0
        assert link.is_active is True

    def test_link_not_expired_by_default(self, link):
        assert link.is_expired() is False
        assert link.is_available() is True

    def test_link_expired(self, db, user):
        l = Link(
            short_code='exp123',
            original_url='https://test.com',
            user_id=user.id,
            expires_at=datetime.utcnow() - timedelta(days=1),
        )
        db.session.add(l)
        db.session.commit()
        assert l.is_expired() is True
        assert l.is_available() is False

    def test_link_future_expiry(self, db, user):
        l = Link(
            short_code='fut123',
            original_url='https://test.com',
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db.session.add(l)
        db.session.commit()
        assert l.is_expired() is False
        assert l.is_available() is True

    def test_inactive_link(self, db, user):
        l = Link(
            short_code='ina123',
            original_url='https://test.com',
            user_id=user.id,
            is_active=False,
        )
        db.session.add(l)
        db.session.commit()
        assert l.is_available() is False


class TestClickModel:
    def test_click_creation(self, db, link):
        c = Click(
            link_id=link.id,
            ip_address='192.168.1.1',
            device='mobile',
            browser='Chrome',
        )
        db.session.add(c)
        db.session.commit()
        assert c.id is not None
        assert c.link.id == link.id
        assert c.device == 'mobile'

    def test_clicks_cascade_delete(self, db, link):
        """با حذف لینک، کلیک‌هاش هم پاک بشن"""
        c1 = Click(link_id=link.id, ip_address='1.1.1.1')
        c2 = Click(link_id=link.id, ip_address='2.2.2.2')
        db.session.add_all([c1, c2])
        db.session.commit()
        assert Click.query.count() == 2

        db.session.delete(link)
        db.session.commit()
        assert Click.query.count() == 0
