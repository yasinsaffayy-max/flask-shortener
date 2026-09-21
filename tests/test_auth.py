from app.models import User


class TestRegister:
    def test_register_page_loads(self, client):
        r = client.get('/auth/register')
        assert r.status_code == 200

    def test_register_success(self, client, db):
        r = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'pass1234',
            'confirm_password': 'pass1234',
        }, follow_redirects=True)
        assert r.status_code == 200
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'new@test.com'

    def test_register_duplicate_username(self, client, user):
        r = client.post('/auth/register', data={
            'username': 'ali',
            'email': 'other@test.com',
            'password': 'pass1234',
            'confirm_password': 'pass1234',
        })
        assert r.status_code == 200
        # باید فقط همون کاربر ali بمونه
        assert User.query.filter_by(username='ali').count() == 1

    def test_register_password_mismatch(self, client, db):
        r = client.post('/auth/register', data={
            'username': 'newuser2',
            'email': 'new2@test.com',
            'password': 'pass1234',
            'confirm_password': 'different',
        })
        assert User.query.filter_by(username='newuser2').count() == 0

    def test_register_short_password(self, client, db):
        r = client.post('/auth/register', data={
            'username': 'newuser3',
            'email': 'new3@test.com',
            'password': '123',
            'confirm_password': '123',
        })
        assert User.query.filter_by(username='newuser3').count() == 0


class TestLogin:
    def test_login_page_loads(self, client):
        r = client.get('/auth/login')
        assert r.status_code == 200

    def test_login_success(self, client, user):
        r = client.post('/auth/login', data={
            'username': 'ali',
            'password': 'password123',
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_login_wrong_password(self, client, user):
        r = client.post('/auth/login', data={
            'username': 'ali',
            'password': 'wrong',
        }, follow_redirects=True)
        # نباید لاگین بشه
        with client.session_transaction() as sess:
            assert '_user_id' not in sess

    def test_login_nonexistent_user(self, client, db):
        r = client.post('/auth/login', data={
            'username': 'nobody',
            'password': 'whatever',
        }, follow_redirects=True)
        with client.session_transaction() as sess:
            assert '_user_id' not in sess


class TestLogout:
    def test_logout(self, auth_client):
        r = auth_client.get('/auth/logout', follow_redirects=True)
        assert r.status_code == 200
        # بعد از logout، دسترسی به داشبورد باید ریدایرکت بشه
        r2 = auth_client.get('/link/dashboard')
        assert r2.status_code == 302
