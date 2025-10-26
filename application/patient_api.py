from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for
from application.models import Patient , Appointment , Doctor ,db,Department
from datetime import datetime, time as time_class

api=Blueprint("patient_api",__name__)

@api.route("/patient_dashboard", methods=["GET", "POST"])
def patient_dashboard():
    current_patient = Patient.query.first()  # replace with current_user later
    # Fetch appointments for this patient
    appointments = Appointment.query.filter_by(patient_id=current_patient.patient_id).all()
    all_departments = Department.query.filter_by(department_name=Department.department_name).first()
    doctor_department_map={doc.doctor_id: doc.department for doc in Doctor.query.all()}
    
    return render_template("patient/patient_dashboard.html",name=current_patient.name,appointments=appointments,doctor_department_map=doctor_department_map,all_departments=all_departments)

@api.route("/book_appointment", methods=["GET","POST"])
def book_appointment():
    if request.method == "GET":
        doctors = Doctor.query.all()
        return render_template("patient/book_appointment.html", doctors=doctors)

    if request.method == "POST":
        doctor_id = int(request.form.get('doctor_id'))
        date_str = request.form.get('date')
        time_str = request.form.get('time')

        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        appointment_time = datetime.strptime(time_str, "%H:%M").time()
        current_patient = Patient.query.first()

        # Prevent double booking
        existing_appointment = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=appointment_date,
            time=appointment_time
        ).first()
        if existing_appointment:
            flash("Doctor already booked at this slot", category="warning")
            doctors=Doctor.query.all()
            return render_template("patient/book_appointment.html",doctors=doctors)

        # Create appointment
        new_appointment = Appointment(
            patient_id=current_patient.patient_id,
            doctor_id=int(doctor_id),
            date=appointment_date,
            time=appointment_time,
            status="Booked"
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash("Appointment booked successfully", category='alert-success')
        return redirect(url_for('patient_api.patient_dashboard'))