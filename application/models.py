from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model,UserMixin):
    __tablename__ = "user"

    user_id = db.Column(db.Integer(),primary_key=True,autoincrement=True)
    name = db.Column(db.String(),nullable=False)
    username = db.Column(db.String(),nullable=False)
    password = db.Column(db.String(),nullable=False)
    role = db.Column(db.String(),nullable=False)
    def get_id(self):
        return str(self.user_id)

    doctor = db.relationship("Doctor",backref="user",uselist=False,cascade="all, delete")
    patient = db.relationship("Patient",backref="user",uselist=False,cascade="all, delete")

class Doctor(db.Model):
    __tablename__ = "doctor"

    id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    doctor_id = db.Column(db.Integer(),db.ForeignKey('user.user_id'),nullable=False)
    name = db.Column(db.String(100),nullable=False)
    username = db.Column(db.String(100),nullable=False)
    department = db.Column(db.String(100),db.ForeignKey("department.department_name"),nullable=False)
    availability = db.Column(db.String(200), nullable=True)
    appointments = db.relationship("Appointment", backref="doctor", cascade="all, delete-orphan")

class Patient(db.Model):
    __tablename__ = "patient"

    id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), unique=True)
    name=db.Column(db.String(),nullable=False)
    username = db.Column(db.String(),nullable=False)
    age=db.Column(db.Integer(),nullable=False)
    gender=db.Column(db.String())
    contact=db.Column(db.String(),unique=True,nullable=False)
    address=db.Column(db.String())

    appointments=db.relationship("Appointment",backref="patient",cascade="all, delete-orphan")

class Appointment(db.Model):
    __tablename__ = "appointment"

    appointment_id = db.Column(db.Integer(),primary_key=True,autoincrement=True)
    patient_id = db.Column(db.Integer() , db.ForeignKey("patient.patient_id") ,nullable=False)
    doctor_id = db.Column(db.Integer() , db.ForeignKey("doctor.id"),nullable=True)
    date = db.Column(db.Date(),nullable = False)
    time = db.Column(db.Time(),nullable = False)
    status = db.Column(db.String(),nullable = False , default="Booked")

class Treatment(db.Model):
    __tablename__ = "treatment"

    id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    appointment_id = db.Column(db.Integer(),db.ForeignKey("appointment.appointment_id"),nullable=False)
    diagnosis = db.Column(db.String(),nullable = False)
    prescription = db.Column(db.String(),nullable = False)
    notes = db.Column(db.String())

class Department(db.Model):
    __tablename__ = "department"

    id = db.Column(db.Integer(),primary_key = True,autoincrement=True)
    department_name = db.Column(db.String(),nullable = False,unique=True)
    description = db.Column(db.String(),nullable = False)
    doctors = db.relationship("Doctor", backref="department_obj", lazy=True)