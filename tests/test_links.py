from app.models import Link, Click


class TestHome:
    def test_home_loads(self, client):
        r = client.get('/')
        assert r.status_code == 200


class TestCreateLink:
    def test_create_link_anonymous(self, client, db):
        r = client.post('/link/create', data={
            'original_url': 'https://example.com/test',
        }, follow_redirects=True)
        assert r.status_code == 200
        link = Link.query.first()
        assert link is not None
        assert link.original_url == 'https://example.com/test'
        assert link.user_id is None  # مهمان

    def test_create_link_logged_in(self, auth_client, db, user):
        r = auth_client.post('/link/create', data={
            'original_url': 'https://example.com/mine',
            'title': 'لینک من',
        }, follow_redirects=True)
        link = Link.query.first()
        assert link is not None
        assert link.user_id == user.id
        assert link.title == 'لینک من'

    def test_create_link_invalid_url(self, client, db):
        r = client.post('/link/create', data={
            'original_url': 'not-a-url',
        }, follow_redirects=True)
        assert Link.query.count() == 0

    def test_create_link_empty_url(self, client, db):
        r = client.post('/link/create', data={
            'original_url': '',
        }, follow_redirects=True)
        assert Link.query.count() == 0


class TestRedirect:
    def test_redirect_success(self, client, link):
        r = client.get(f'/{link.short_code}')
        assert r.status_code == 302
        assert r.location == link.original_url

    def test_redirect_records_click(self, client, db, link):
        assert link.clicks_count == 0
        client.get(f'/{link.short_code}')
        db.session.refresh(link)
        assert link.clicks_count == 1
        assert Click.query.count() == 1

    def test_redirect_multiple_clicks(self, client, db, link):
        for _ in range(3):
            client.get(f'/{link.short_code}')
        db.session.refresh(link)
        assert link.clicks_count == 3

    def test_redirect_404(self, client, db):
        r = client.get('/nonexistent')
        assert r.status_code == 404

    def test_redirect_inactive(self, client, db, link):
        link.is_active = False
        db.session.commit()
        r = client.get(f'/{link.short_code}')
        assert r.status_code == 410  # Gone


class TestDashboard:
    def test_dashboard_requires_login(self, client):
        r = client.get('/link/dashboard')
        assert r.status_code == 302  # Redirect to login

    def test_dashboard_shows_links(self, auth_client, link):
        r = auth_client.get('/link/dashboard')
        assert r.status_code == 200
        assert b'abc123' in r.data

    def test_dashboard_doesnt_show_others_links(self, auth_client, db, admin):
        """لینک‌های کاربر دیگه رو نبینه"""
        other = Link(
            short_code='other1',
            original_url='https://other.com',
            user_id=admin.id,
        )
        db.session.add(other)
        db.session.commit()
        r = auth_client.get('/link/dashboard')
        assert b'other1' not in r.data


class TestLinkDetail:
    def test_detail_requires_login(self, client, link):
        r = client.get(f'/link/{link.short_code}')
        assert r.status_code == 302

    def test_detail_own_link(self, auth_client, link):
        r = auth_client.get(f'/link/{link.short_code}')
        assert r.status_code == 200

    def test_detail_others_link_403(self, auth_client, db, admin):
        other = Link(
            short_code='other2',
            original_url='https://other.com',
            user_id=admin.id,
        )
        db.session.add(other)
        db.session.commit()
        r = auth_client.get(f'/link/{other.short_code}')
        assert r.status_code == 403

    def test_admin_can_view_any_link(self, client, db, admin, link):
        # لاگین به عنوان ادمین
        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123',
        })
        r = client.get(f'/link/{link.short_code}')
        assert r.status_code == 200


class TestLinkActions:
    def test_toggle_active(self, auth_client, db, link):
        assert link.is_active is True
        r = auth_client.get(f'/link/{link.id}/toggle', follow_redirects=True)
        db.session.refresh(link)
        assert link.is_active is False

    def test_delete_link(self, auth_client, db, link):
        r = auth_client.post(f'/link/{link.id}/delete', follow_redirects=True)
        assert Link.query.count() == 0


class TestRateLimit:
    def test_anonymous_rate_limit(self, client, db):
        """مهمان‌ها فقط ۵ لینک در روز"""
        for i in range(5):
            client.post('/link/create', data={
                'original_url': f'https://example.com/{i}',
            })
        assert Link.query.count() == 5

        # لینک ششم باید بلاک بشه
        client.post('/link/create', data={
            'original_url': 'https://example.com/blocked',
        })
        assert Link.query.count() == 5  # هنوز ۵

    def test_logged_in_no_rate_limit(self, auth_client, db, user):
        for i in range(10):
            auth_client.post('/link/create', data={
                'original_url': f'https://example.com/{i}',
            })
        assert Link.query.count() == 10
