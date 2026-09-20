from datetime import datetime
from flask import Blueprint, render_template, redirect, request, abort, url_for
from app import db
from app.models import Link, Click

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """صفحه اصلی — فرم کوتاه‌کننده"""
    from app.forms import LinkForm
    form = LinkForm()
    return render_template('home.html', form=form, title='کوتاه‌کننده لینک')


@main_bp.route('/<short_code>')
def redirect_to_original(short_code):
    """ریدایرکت لینک کوتاه به لینک اصلی + ثبت کلیک"""
    # جلوگیری از تداخل با مسیرهای دیگه
    if short_code in ('auth', 'link', 'api', 'admin', 'static', 'favicon.ico'):
        abort(404)

    link = Link.query.filter_by(short_code=short_code).first_or_404()

    if not link.is_available():
        return render_template('link_expired.html', link=link, title='لینک غیرفعال'), 410

    # ثبت کلیک
    ua_string = request.headers.get('User-Agent', '')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) or '0.0.0.0'
    ip = ip.split(',')[0].strip()

    browser, os_name, device = 'Unknown', 'Unknown', 'unknown'
    try:
        from user_agents import parse
        ua = parse(ua_string)
        browser = f"{ua.browser.family} {ua.browser.version_string}".strip()
        os_name = f"{ua.os.family} {ua.os.version_string}".strip()
        if ua.is_mobile:
            device = 'mobile'
        elif ua.is_tablet:
            device = 'tablet'
        elif ua.is_pc:
            device = 'pc'
        else:
            device = 'other'
    except Exception:
        pass

    click = Click(
        link_id=link.id,
        ip_address=ip,
        user_agent=ua_string[:500] if ua_string else None,
        referer=request.referrer[:500] if request.referrer else None,
        browser=browser[:50],
        os=os_name[:50],
        device=device,
    )
    link.clicks_count = (link.clicks_count or 0) + 1
    db.session.add(click)
    db.session.commit()

    return redirect(link.original_url, code=302)
