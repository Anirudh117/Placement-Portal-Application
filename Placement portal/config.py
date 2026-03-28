import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "supersecretkey"
    DATABASE = os.path.join(BASE_DIR, "instance", "placement.db")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "resumes")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE
    SQLALCHEMY_TRACK_MODIFICATIONS = False