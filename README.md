
# 🔗 Sho.rt — کوتاه‌کننده لینک با آمار کامل

یه سرویس کوتاه‌کننده لینک حرفه‌ای با Flask — مثل bit.ly ولی ساده‌تر و با نمودارهای زیبا.

# 🔗 Sho.rt — کوتاه‌کننده لینک با آمار کامل

![Tests](https://github.com/yasinsaffayy-max/flask-shortener/actions/workflows/tests.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/flask-3.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

یه سرویس کوتاه‌کننده لینک حرفه‌ای با Flask

## ✨ امکانات

- 🔗 **کوتاه‌سازی لینک** — هم برای کاربر لاگین‌کرده، هم مهمان
- 📊 **آمار کامل** — کلیک، دستگاه، مرورگر، IP، زمان
- 📈 **نمودار ۷ روز اخیر** با Chart.js
- 📱 **QR Code خودکار** برای هر لینک
- 🔒 **محدودیت نرخ** — مهمان: ۵ لینک/روز، API: ۱۰ درخواست/روز
- ⏰ **انقضای لینک** — تعیین تاریخ انقضا
- 🔀 **فعال/غیرفعال کردن لینک** بدون حذف
- 🌙 **حالت تاریک**
- 🚀 **REST API** برای ساخت لینک و آمار
- 👤 **احراز هویت** با Flask-Login
- 📱 **کاملاً رسپانسیو**

## 🛠 تکنولوژی‌ها

| بخش | تکنولوژی |
|-----|----------|
| Backend | Flask 3, SQLAlchemy, Flask-Login, Flask-WTF |
| Database | SQLite |
| Frontend | Bootstrap 5 RTL, Chart.js, Vazirmatn |
| Analytics | user-agents (تشخیص دستگاه) |
| QR Code | qrcode + Pillow |

## 🚀 نصب و اجرا

```bash
git clone https://github.com/yasinsaffayy-max/flask-shortener.git
cd flask-shortener

python -m venv venv
source venv/bin/activate  # ویندوز: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# مقدار SECRET_KEY رو ویرایش کن

python init_db.py
python run.py
```

مرورگر: http://127.0.0.1:5000

🔐 ورود ادمین

· Username: admin
· Password: admin123

📡 API

ساخت لینک کوتاه

```bash
curl -X POST http://127.0.0.1:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/url", "title": "اختیاری"}'
```

پاسخ:

```json
{
  "short_code": "aB3xY9",
  "short_url": "http://127.0.0.1:5000/aB3xY9",
  "original_url": "https://example.com/very/long/url",
  "created_at": "2026-09-20T10:30:00"
}
```

آمار یک لینک

```bash
curl http://127.0.0.1:5000/api/stats/aB3xY9
```

چک سلامت

```bash
curl http://127.0.0.1:5000/api/health
```

📁 ساختار پروژه

```
flask-shortener/
├── app/
│   ├── __init__.py
│   ├── models.py            # User, Link, Click
│   ├── forms.py
│   ├── decorators.py
│   ├── routes/
│   │   ├── main.py          # صفحه اصلی + redirect
│   │   ├── auth.py          # ثبت‌نام/ورود
│   │   ├── link.py          # ساخت لینک + آمار
│   │   └── api.py           # REST API
│   ├── templates/
│   └── static/
│       └── qrcodes/         # QR Codeها
├── config.py
├── run.py
├── init_db.py
└── requirements.txt
```

📝 لایسنس

MIT
