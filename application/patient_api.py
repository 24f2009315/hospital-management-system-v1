from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for
from application.models import Patient , Appointment , Doctor ,db,Department,Treatment
from datetime import datetime, time as time_class

api=Blueprint("patient_api",__name__)

@api.route("/patient_dashboard", methods=["GET", "POST"])
def patient_dashboard():
    current_patient = Patient.query.first()  # replace with current_user later
    # Fetch appointments for this patient
    booked = Appointment.query.filter_by(patient_id=current_patient.patient_id, status="Booked").all()
    completed = Appointment.query.filter_by(patient_id=current_patient.patient_id, status="Completed").all()
    cancelled = Appointment.query.filter_by(patient_id=current_patient.patient_id, status="Cancelled").all()

    all_departments = Department.query.all()
    doctor_department_map={doc.doctor_id: doc.department for doc in Doctor.query.all()}
    
    return render_template("patient/patient_dashboard.html",name=current_patient.name,patient_id=current_patient.patient_id,booked=booked,completed=completed,cancelled=cancelled,doctor_department_map=doctor_department_map,all_departments=all_departments)

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

@api.route("/patient_dashboard/search",methods=["GET","POST"])
def search_users():
    query = request.form.get("query","").strip()
    doctors = []
    if query:
        doctors = Doctor.query.filter(
            (Doctor.name.ilike(f'%{query}%')) |
            (Doctor.department.ilike(f'%{query}%'))
        ).all()
    return render_template("patient/patient_search.html",doctors = doctors)

@api.route("/patient_dashboard/patient_history/<int:patient_id>")
def patient_history(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    if not patient:
        flash("Patient not found", category='error')
        return redirect(url_for('patient_api.patient_dashboard'))

    # Get all appointments for this patient
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()

    # Get all treatments linked to these appointments
    treatments = Treatment.query.filter(Treatment.appointment_id.in_([appt.appointment_id for appt in appointments])).all()

    return render_template("patient/patient_history.html",patient=patient,treatments=treatments)

@api.route("/patient_dashboard/mark_cancelled/<int:appointment_id>")
def mark_cancelled(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = "Cancelled"
        db.session.commit()
        flash("Appointment cancelled", "warning")
    return redirect(url_for("patient_api.patient_dashboard"))