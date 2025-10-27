from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for
from application.models import Patient , Appointment , Doctor ,db,Department,Treatment
from datetime import datetime, time as time_class
from sqlalchemy import or_

api=Blueprint("patient_api",__name__)

@api.route("/patient_dashboard", methods=["GET", "POST"])
def patient_dashboard():
    current_patient = Patient.query.first()  # replace with current_user later
    db.session.expire_all()
    booked = Appointment.query.filter_by(patient_id=current_patient.patient_id, status="Booked").all()
    completed = Appointment.query.filter_by(patient_id=current_patient.patient_id, status="Completed").all()
    cancelled = Appointment.query.filter_by(patient_id=current_patient.patient_id, status="Cancelled").all()

    all_departments = Department.query.all()
    all_doctors=Doctor.query.all()

    doctor_department_map = {doc.doctor_id: doc.department for doc in Doctor.query.all()}

    return render_template(
        "patient/patient_dashboard.html",
        name=current_patient.name,
        patient_id=current_patient.patient_id,
        booked=booked,
        completed=completed,
        cancelled=cancelled,
        doctor_department_map=doctor_department_map,
        all_departments=all_departments,
        all_doctors=all_doctors
    )

from datetime import datetime

@api.route("/book_appointment", methods=["GET", "POST"])
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
        selected_date_str = appointment_date.strftime("%Y-%m-%d")

        current_patient = Patient.query.first()
        doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()

        # ✅ FIXED: check using actual date strings
        available_dates = doctor.availability.split(",") if doctor and doctor.availability else []
        if selected_date_str not in available_dates:
            flash(f"Dr. {doctor.name} is not available on {selected_date_str}. Please select another date.", "alert-danger")
            doctors = Doctor.query.all()
            return render_template("patient/book_appointment.html", doctors=doctors)

        # 🕐 Prevent double booking
        existing_appointment = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=appointment_date,
            time=appointment_time
        ).first()
        if existing_appointment:
            flash("Doctor already booked at this slot", category="warning")
            doctors = Doctor.query.all()
            return render_template("patient/book_appointment.html", doctors=doctors)

        # ✅ Create appointment
        new_appointment = Appointment(
            patient_id=current_patient.patient_id,
            doctor_id=int(doctor_id),
            date=appointment_date,
            time=appointment_time,
            status="Booked"
        )
        db.session.add(new_appointment)
        db.session.commit()

        flash("Appointment booked successfully!", category='alert-success')
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

@api.route("/check_availability/<int:doctor_id>")
def check_availability(doctor_id):
    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()

    if not doctor:
        flash("Doctor not found.", category="alert-danger")
        return redirect(url_for("patient_api.patient_dashboard"))

    available_days=[]
    if doctor.availability:
        available_days = doctor.availability.split(",")
    
    return render_template(
        "patient/check_availability.html",
        doctor=doctor,
        available_days=available_days
    )

@api.route("/patient_dashboard/reschedule/<int:appointment_id>", methods=["GET", "POST"])
def reschedule_appointment(appointment_id):
    # load appointment
    appointment = Appointment.query.get_or_404(appointment_id)

    # find doctor robustly: appointment.doctor_id might store doctor.id or doctor.doctor_id
    doctor = Doctor.query.filter(
        or_(
            Doctor.id == appointment.doctor_id,
            Doctor.doctor_id == appointment.doctor_id
        )
    ).first()

    if not doctor:
        flash("Linked doctor not found for this appointment.", "warning")
        return redirect(url_for('patient_api.patient_dashboard'))

    if request.method == "POST":
        print(">>> RESCHEDULE POST triggered for appointment", appointment_id)
        new_date_str = request.form.get("date")
        new_time_str = request.form.get("time")

        if not new_date_str or not new_time_str:
            flash("Please select both date and time.", "warning")
            return redirect(url_for('patient_api.reschedule_appointment', appointment_id=appointment_id))

        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
        new_time = datetime.strptime(new_time_str, "%H:%M").time()

        # ---- AVAILABILITY CHECK (use date strings YYYY-MM-DD, consistent with booking) ----
        available_dates = doctor.availability.split(",") if doctor.availability else []
        available_dates = [d.strip() for d in available_dates if d.strip()]  # clean spaces

        # compare exact date string (same format you saved when doctor chose dates)
        selected_date_str = new_date.strftime("%Y-%m-%d")
        if available_dates and selected_date_str not in available_dates:
            flash(f"Dr. {doctor.name} is not available on {selected_date_str}. Please pick another date.", "warning")
            return redirect(url_for('patient_api.reschedule_appointment', appointment_id=appointment_id))

        # ---- DOUBLE BOOKING CHECK ----
        # existing appointment where appointment_id != this one AND date/time match
        # and doctor id matches either doctor.id or doctor.doctor_id (be defensive)
        existing = Appointment.query.filter(
            Appointment.appointment_id != appointment_id,
            Appointment.date == new_date,
            Appointment.time == new_time,
            or_(
                Appointment.doctor_id == doctor.id,
                Appointment.doctor_id == doctor.doctor_id
            )
        ).first()

        if existing:
            flash("This time slot is already booked for this doctor.", "warning")
            return redirect(url_for('patient_api.reschedule_appointment', appointment_id=appointment_id))

        # ---- UPDATE appointment ----
        appointment.date = new_date
        appointment.time = new_time

        # ensure session sees it and commit
        db.session.merge(appointment)
        db.session.commit()
        db.session.refresh(appointment)

        print(f"✅ Appointment {appointment.appointment_id} updated -> {appointment.date} {appointment.time}")
        flash("Appointment rescheduled successfully", "alert-success")
        return redirect(url_for("patient_api.patient_dashboard"))

    # GET -> render form
    return render_template("patient/reschedule.html", appointment=appointment, doctor=doctor)