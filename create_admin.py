from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    db.create_all()

    existing_admin = User.query.filter_by(role="Admin").first()

    if not existing_admin:
        admin = User(
            name="Admin",
            email="admin@trekapp.com",
            role="Admin",
            is_approved=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin already exists, skipping creation.")


        