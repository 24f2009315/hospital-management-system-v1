from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer(),primary_key=True,autoincrement=True)
    name = db.Column(db.String(),nullable=False)
    username = db.Column(db.String(),nullable=False)
    password = db.Column(db.String(),nullable=False)
    role = db.Column(db.String(),nullable=False)

class Doctor(db.Model):
    __tablename__ = "doctor"

    id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    name = db.Column(db.String(),nullable=False)
    specialization=db.Column(db.String(),nullable=False)
    availability=db.Column(db.String())
    email=db.Column(db.String(),unique=True,nullable=False)
    password=db.Column(db.String(),nullable=False)
    department_id=db.Column(db.Integer(),db.ForeignKey("department.id"))
    role = db.Column(db.String(),nullable=False)

class Patient(db.Model):
    __tablename__ = "patient"

    id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    name=db.Column(db.String(),nullable=False)
    age=db.Column(db.Integer(),nullable=False)
    gender=db.Column(db.String())
    contact=db.Column(db.String(),unique=True,nullable=False)
    email=db.Column(db.String(),unique=True,nullable=False)
    password=db.Column(db.String(),nullable=False)
    address=db.Column(db.String())
    role = db.Column(db.String(),nullable=False)

class Appointment(db.Model):
    __tablename__ = "appointment"

    id = db.Column(db.Integer(),primary_key=True,autoincrement=True)
    patient_id = db.Column(db.Integer() , db.ForeignKey("patient.id") ,nullable=False)
    doctor_id = db.Column(db.Integer() , db.ForeignKey("doctor.id"),nullable=True)
    date = db.Column(db.Date()  ,nullable = False)
    time = db.Column(db.Time(),nullable = False)
    status = db.Column(db.String(),nullable = False , default="Booked")

class Treatment(db.Model):
    __tablename__ = "treatment"

    id=db.Column(db.Integer(),primary_key=True,autoincrement=True)
    appointment_id = db.Column(db.Integer(),db.ForeignKey("appointment.id"),nullable=False)
    diagnosis = db.Column(db.String(),nullable = False)
    prescription = db.Column(db.String(),nullable = False)
    notes = db.Column(db.String())

class Department(db.Model):
    __tablename__ = "department"

    id = db.Column(db.Integer(),primary_key = True,autoincrement=True)
    department_name = db.Column(db.String(),nullable = False,unique=True)
    description = db.Column(db.String(),nullable = False)
    doctors_registered = db.Column(db.String())