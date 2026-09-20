import os
import qrcode
from datetime import datetime, timedelta
from collections import Counter
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    current_app, abort, jsonify
)
from flask_login import current_user, login_required
from app import db
from app.models import Link, Click
from app.forms import LinkForm

link_bp = Blueprint('link', __name__)


def get_client_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) or '0.0.0.0'
    return ip.split(',')[0].strip()


def generate_qrcode(short_code):
    """ساخت QR Code برای لینک کوتاه"""
    url = f"{current_app.config['BASE_URL']}/{short_code}"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    filename = f"{short_code}.png"
    filepath = os.path.join(current_app.config['QRCODE_FOLDER'], filename)
    img.save(filepath)
    return filename


@link_bp.route('/create', methods=['POST'])
def create():
    """ساخت لینک کوتاه — هم برای کاربر، هم مهمان"""
    form = LinkForm()

    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for err in errors:
                flash(f'{err}', 'danger')
        return redirect(url_for('main.home'))

    # محدودیت برای مهمان: ۵ لینک در ۲۴ ساعت گذشته
    ip = get_client_ip()
    if not current_user.is_authenticated:
        since = datetime.utcnow() - timedelta(days=1)
        count = Link.query.filter(
            Link.user_id.is_(None),
            Link.ip_creator == ip,
            Link.created_at >= since
        ).count()
        if count >= 5:
            flash('مهمان‌ها فقط می‌توانند ۵ لینک در روز بسازند. برای لینک بیشتر ثبت‌نام کن.', 'warning')
            return redirect(url_for('main.home'))

    # ساخت لینک
    expires_at = None
    if form.expires_days.data:
        expires_at = datetime.utcnow() + timedelta(days=form.expires_days.data)

    link = Link(
        short_code=Link.generate_unique_code(),
        original_url=form.original_url.data.strip(),
        title=form.title.data.strip() if form.title.data else None,
        user_id=current_user.id if current_user.is_authenticated else None,
        ip_creator=ip,
        expires_at=expires_at,
    )
    db.session.add(link)
    db.session.commit()

    # ساخت QR Code
    try:
        generate_qrcode(link.short_code)
    except Exception as e:
        print(f"QR error: {e}")

    # اگه لاگین نیست، به صفحه نمایش لینک بره
    if not current_user.is_authenticated:
        return render_template('link/success.html', link=link, title='لینک ساخته شد')

    flash('لینک کوتاه ساخته شد!', 'success')
    return redirect(url_for('link.detail', code=link.short_code))


@link_bp.route('/dashboard')
@login_required
def dashboard():
    """داشبورد کاربر — لیست لینک‌ها"""
    page = request.args.get('page', 1, type=int)
    links = Link.query.filter_by(user_id=current_user.id).order_by(
        Link.created_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)

    # آمار کلی
    total_clicks = sum(l.clicks_count for l in Link.query.filter_by(user_id=current_user.id).all())
    total_links = Link.query.filter_by(user_id=current_user.id).count()

    return render_template(
        'link/dashboard.html',
        links=links,
        total_clicks=total_clicks,
        total_links=total_links,
        title='داشبورد'
    )


@link_bp.route('/<code>')
@login_required
def detail(code):
    """صفحه جزئیات و آمار یه لینک"""
    link = Link.query.filter_by(short_code=code).first_or_404()

    # فقط سازنده یا ادمین
    if link.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    # آخرین ۱۰۰ کلیک
    clicks = Click.query.filter_by(link_id=link.id).order_by(
        Click.clicked_at.desc()
    ).limit(100).all()

    # آمار
    stats = {
        'total': link.clicks_count,
        'today': Click.query.filter(
            Click.link_id == link.id,
            Click.clicked_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).count(),
        'week': Click.query.filter(
            Click.link_id == link.id,
            Click.clicked_at >= datetime.utcnow() - timedelta(days=7)
        ).count(),
    }

    # نمودار کلیک ۷ روز اخیر
    chart_data = []
    for i in range(6, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).date()
        count = Click.query.filter(
            Click.link_id == link.id,
            db.func.date(Click.clicked_at) == day
        ).count()
        chart_data.append({
            'label': day.strftime('%m/%d'),
            'value': count
        })

    # آمار دستگاه‌ها
    device_stats = dict(Counter(c.device for c in clicks if c.device))
    browser_stats = dict(Counter(c.browser.split()[0] if c.browser else 'Unknown' for c in clicks))

    # QR Code
    qr_filename = f"{link.short_code}.png"
    qr_path = os.path.join(current_app.config['QRCODE_FOLDER'], qr_filename)
    qr_exists = os.path.exists(qr_path)

    return render_template(
        'link/detail.html',
        link=link,
        clicks=clicks,
        stats=stats,
        chart_data=chart_data,
        device_stats=device_stats,
        browser_stats=browser_stats,
        qr_exists=qr_exists,
        qr_filename=qr_filename,
        title=f'آمار {link.short_code}'
    )


@link_bp.route('/<int:lid>/delete', methods=['POST'])
@login_required
def delete(lid):
    """حذف لینک"""
    link = Link.query.get_or_404(lid)
    if link.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(link)
    db.session.commit()
    flash('لینک حذف شد.', 'info')
    return redirect(url_for('link.dashboard'))


@link_bp.route('/<int:lid>/toggle')
@login_required
def toggle(lid):
    """فعال/غیرفعال کردن لینک"""
    link = Link.query.get_or_404(lid)
    if link.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    link.is_active = not link.is_active
    db.session.commit()
    state = 'فعال' if link.is_active else 'غیرفعال'
    flash(f'لینک {state} شد.', 'info')
    return redirect(url_for('link.dashboard'))
