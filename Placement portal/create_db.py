from app import app
from models import db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    if not User.query.filter_by(role="admin").first():
        admin = User(
            role="admin",
            name="Admin",
            email="admin@portal.com",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()