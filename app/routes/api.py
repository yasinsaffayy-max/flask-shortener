from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from app import db
from app.models import Link, Click

api_bp = Blueprint('api', __name__)


def get_client_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) or '0.0.0.0'
    return ip.split(',')[0].strip()


@api_bp.route('/shorten', methods=['POST'])
def shorten():
    """API ساخت لینک کوتاه
    POST /api/shorten
    Body: {"url": "https://example.com", "title": "optional"}
    """
    data = request.get_json(silent=True) or {}
    url = (data.get('url') or '').strip()

    if not url:
        return jsonify({'error': 'url is required'}), 400

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # محدودیت ساده: ۱۰ لینک در روز برای هر IP
    ip = get_client_ip()
    since = datetime.utcnow() - timedelta(days=1)
    count = Link.query.filter(
        Link.ip_creator == ip,
        Link.created_at >= since
    ).count()
    if count >= 10:
        return jsonify({'error': 'Rate limit exceeded (10/day)'}), 429

    link = Link(
        short_code=Link.generate_unique_code(),
        original_url=url,
        title=(data.get('title') or '').strip() or None,
        ip_creator=ip,
    )
    db.session.add(link)
    db.session.commit()

    short_url = f"{request.host_url.rstrip('/')}/{link.short_code}"

    return jsonify({
        'short_code': link.short_code,
        'short_url': short_url,
        'original_url': link.original_url,
        'title': link.title,
        'created_at': link.created_at.isoformat(),
    }), 201


@api_bp.route('/stats/<code>')
def stats(code):
    """API آمار یه لینک
    GET /api/stats/abc123
    """
    link = Link.query.filter_by(short_code=code).first()
    if not link:
        return jsonify({'error': 'Link not found'}), 404

    clicks = Click.query.filter_by(link_id=link.id).all()

    devices = {}
    browsers = {}
    for c in clicks:
        devices[c.device or 'unknown'] = devices.get(c.device or 'unknown', 0) + 1
        b = (c.browser or 'Unknown').split()[0]
        browsers[b] = browsers.get(b, 0) + 1

    return jsonify({
        'short_code': link.short_code,
        'original_url': link.original_url,
        'total_clicks': link.clicks_count,
        'is_active': link.is_active,
        'created_at': link.created_at.isoformat(),
        'devices': devices,
        'browsers': browsers,
    })


@api_bp.route('/health')
def health():
    """چک سلامت سرویس"""
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})
