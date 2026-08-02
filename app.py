from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    from auth import auth_bp
    app.register_blueprint(auth_bp)

    from admin import admin_bp
    app.register_blueprint(admin_bp)

    

    from staff import staff_bp
    app.register_blueprint(staff_bp)

    return app

app = create_app()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    app.run(debug=True)