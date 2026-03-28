from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))  
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    blacklisted = db.Column(db.Boolean, default=False)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_name = db.Column(db.String(150))
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(150))
    details = db.Column(db.Text)  
    approval_status = db.Column(db.String(20), default="Pending")  
    

    
    user = db.relationship('User', backref='company', uselist=False)
    drives = db.relationship('Drive', backref='company', lazy=True)



class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contact = db.Column(db.String(20))
    course = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    resume = db.Column(db.String(200))  


    user = db.relationship('User', backref='student', uselist=False)
    applications = db.relationship('Application', backref='student', lazy=True)



class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    job_title = db.Column(db.String(150))
    job_description = db.Column(db.Text)
    eligibility = db.Column(db.String(255))
    deadline = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Pending")



    applications = db.relationship('Application', backref='drive', lazy=True)



class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'))
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Applied")
    