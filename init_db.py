"""ساخت دیتابیس و کاربر ادمین"""
from app import create_app, db
from app.models import User, Link, Click

app = create_app('development')

with app.app_context():
    db.create_all()
    print("✅ جداول ساخته شدند")

    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@short.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ ادمین ساخته شد (admin / admin123)")
    else:
        print("ℹ️ ادمین از قبل وجود دارد")

    print("\n🎉 آماده! حالا `python run.py` بزن.")
