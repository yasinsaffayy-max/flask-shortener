import json
from app.models import Link


class TestHealthAPI:
    def test_health(self, client):
        r = client.get('/api/health')
        assert r.status_code == 200
        data = r.get_json()
        assert data['status'] == 'ok'
        assert 'timestamp' in data


class TestShortenAPI:
    def test_shorten_success(self, client, db):
        r = client.post('/api/shorten',
            data=json.dumps({'url': 'https://example.com/test'}),
            content_type='application/json'
        )
        assert r.status_code == 201
        data = r.get_json()
        assert 'short_code' in data
        assert 'short_url' in data
        assert data['original_url'] == 'https://example.com/test'

    def test_shorten_without_protocol(self, client, db):
        """اگه کاربر http نذاره، خودمون اضافه کنیم"""
        r = client.post('/api/shorten',
            data=json.dumps({'url': 'example.com'}),
            content_type='application/json'
        )
        assert r.status_code == 201
        data = r.get_json()
        assert data['original_url'].startswith('https://')

    def test_shorten_missing_url(self, client):
        r = client.post('/api/shorten',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert r.status_code == 400
        data = r.get_json()
        assert 'error' in data

    def test_shorten_empty_url(self, client):
        r = client.post('/api/shorten',
            data=json.dumps({'url': ''}),
            content_type='application/json'
        )
        assert r.status_code == 400

    def test_shorten_with_title(self, client, db):
        r = client.post('/api/shorten',
            data=json.dumps({
                'url': 'https://example.com',
                'title': 'عنوان من'
            }),
            content_type='application/json'
        )
        assert r.status_code == 201
        data = r.get_json()
        assert data['title'] == 'عنوان من'


class TestStatsAPI:
    def test_stats_success(self, client, link):
        r = client.get(f'/api/stats/{link.short_code}')
        assert r.status_code == 200
        data = r.get_json()
        assert data['short_code'] == link.short_code
        assert data['original_url'] == link.original_url
        assert data['total_clicks'] == 0

    def test_stats_404(self, client, db):
        r = client.get('/api/stats/nonexistent')
        assert r.status_code == 404

    def test_stats_after_clicks(self, client, db, link):
        # ۳ تا کلیک بزنیم
        for _ in range(3):
            client.get(f'/{link.short_code}')

        r = client.get(f'/api/stats/{link.short_code}')
        data = r.get_json()
        assert data['total_clicks'] == 3
