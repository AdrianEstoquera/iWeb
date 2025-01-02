# config.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "pass"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "mysql+pymysql://cinemaViewWeb:pass@mysql-container:3306/cineViewUsers"
    SQLALCHEMY_TRACK_MODIFICATIONS = False