from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, IntegerField
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, ValidationError, Optional,
    URL, NumberRange
)
from app.models import User


class RegisterForm(FlaskForm):
    username = StringField('نام کاربری', validators=[
        DataRequired(message='نام کاربری الزامی است.'), Length(3, 50)
    ])
    email = StringField('ایمیل', validators=[
        DataRequired(), Email(message='ایمیل معتبر نیست.')
    ])
    password = PasswordField('رمز عبور', validators=[
        DataRequired(), Length(min=6, message='رمز حداقل ۶ کاراکتر باشد.')
    ])
    confirm_password = PasswordField('تکرار رمز عبور', validators=[
        DataRequired(), EqualTo('password', message='رمزها یکسان نیستند.')
    ])
    submit = SubmitField('ثبت‌نام')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('این نام کاربری قبلاً استفاده شده.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('این ایمیل قبلاً ثبت شده.')


class LoginForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired()])
    password = PasswordField('رمز عبور', validators=[DataRequired()])
    remember = BooleanField('مرا به خاطر بسپار')
    submit = SubmitField('ورود')


class LinkForm(FlaskForm):
    original_url = StringField('لینک اصلی', validators=[
        DataRequired(message='لینک الزامی است.'),
        Length(5, 2000),
        URL(message='لینک معتبر نیست. مثال: https://example.com')
    ])
    title = StringField('عنوان (اختیاری)', validators=[Optional(), Length(0, 200)])
    expires_days = IntegerField('انقضا (روز)', validators=[
        Optional(), NumberRange(min=1, max=365, message='بین ۱ تا ۳۶۵ روز')
    ], default=None)
    submit = SubmitField('کوتاه کن!')

    def validate_original_url(self, field):
        url = field.data.strip()
        if not url.startswith(('http://', 'https://')):
            raise ValidationError('لینک باید با http:// یا https:// شروع شود.')
