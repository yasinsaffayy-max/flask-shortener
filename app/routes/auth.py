from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('link.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('ثبت‌نام موفق! حالا وارد شو.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form, title='ثبت‌نام')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('link.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash('نام کاربری یا رمز اشتباه است.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember.data)
        flash(f'خوش آمدی {user.username}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('link.dashboard'))

    return render_template('auth/login.html', form=form, title='ورود')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('خارج شدی.', 'info')
    return redirect(url_for('main.home'))
