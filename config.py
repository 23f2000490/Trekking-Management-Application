import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

class Config:
    SECRET_KEY = "your-secret-key-change-this-later"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "trekking.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False