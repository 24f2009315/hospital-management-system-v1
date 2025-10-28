from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for,jsonify,request,session
from flask_login import login_required,current_user
from application.models import Doctor,db,Appointment,Patient,User,Department,Treatment
from datetime import datetime,timedelta

api=Blueprint("doctor_api",__name__)

@api.route("/doctor_dashboard",methods = ["GET","POST"])
@login_required
def doctor_dashboard():
    if current_user.role != "doctor":
        flash("Access Denied","danger")
        return redirect(url_for('auth.login'))
    if request.method == "GET":
        current_doctor=Doctor.query.first()
        booked = Appointment.query.filter_by(doctor_id=current_doctor.doctor_id, status="Booked").all()
        completed = Appointment.query.filter_by(doctor_id=current_doctor.doctor_id, status="Completed").all()
        cancelled = Appointment.query.filter_by(doctor_id=current_doctor.doctor_id, status="Cancelled").all()

        patient_map = {p.patient_id: p.name for p in Patient.query.all()}
        appointment_status = {
            "Booked": len(booked),
            "Completed": len(completed),
            "Cancelled": len(cancelled)
        }

        return render_template("doctor/doctor_dashboard.html",
            doctor=current_doctor,
            name=current_doctor.name,
            booked=booked,
            completed=completed,
            cancelled=cancelled,
            patient_map=patient_map,
            appointment_status=appointment_status)

@api.route("/doctor_dashboard/mark_completed/<int:appointment_id>")
def mark_completed(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = "Completed"
        db.session.commit()
        flash("Appointment marked as completed", "success")
    return redirect(url_for("doctor_api.doctor_dashboard"))

@api.route("/doctor_dashboard/mark_cancelled/<int:appointment_id>")
def mark_cancelled(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = "Cancelled"
        db.session.commit()
        flash("Appointment cancelled", "warning")
    return redirect(url_for("doctor_api.doctor_dashboard"))

@api.route("/doctor_dashboard/update_history/<int:patient_id>", methods=["GET","POST"])
def update_history(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    if not patient:
        flash("Patient not found", category='error')
        return redirect(url_for('doctor_api.doctor_dashboard'))

    # Find the doctor via the appointment
    appointment = Appointment.query.filter_by(patient_id=patient_id).first()
    doctor = None
    if appointment:
        doctor = Doctor.query.filter_by(doctor_id=appointment.doctor_id).first()

    if request.method == "GET":
        department = Department.query.filter_by(department_name=doctor.department).first() if doctor else None
        return render_template("doctor/update_history.html", patient=patient, department=department)

    # POST - update patient history
    diagnosis = request.form.get("diagnosis")
    prescription = request.form.get("prescription")
    notes = request.form.get("notes")

    # Optionally update Patient's last visit info
    patient.diagnosis = diagnosis
    patient.prescription = prescription
    patient.notes=notes

    # Create a new Treatment record
    if appointment:
        new_treatment = Treatment(
            appointment_id = appointment.appointment_id,
            diagnosis = diagnosis,
            prescription = prescription,
            notes = notes
        )
        db.session.add(new_treatment)
    db.session.commit()

    flash("Patient history updated and recorded in Treatment table successfully", category='success')
    return redirect(url_for('doctor_api.doctor_dashboard'))

@api.route("/doctor_dashboard/patient_history/<int:patient_id>")
def patient_history(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    if not patient:
        flash("Patient not found", category='error')
        return redirect(url_for('doctor_api.doctor_dashboard'))

    # Get all appointments for this patient
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()

    # Get all treatments linked to these appointments
    treatments = Treatment.query.filter(Treatment.appointment_id.in_([appt.appointment_id for appt in appointments])).all()

    return render_template("doctor/patient_history.html",patient=patient,treatments=treatments)

@api.route("/update_availability/<int:doctor_id>", methods=["GET", "POST"])
def update_availability(doctor_id):
    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()

    if not doctor:
        flash("Doctor not found.", category="alert-danger")
        return redirect(url_for("doctor_api.doctor_dashboard"))

    # ✅ Generate next 7 calendar dates
    today = datetime.today().date()
    next_7_days = [(today + timedelta(days=i)) for i in range(7)]

    if request.method == "POST":
        # Get all checked dates from the form
        selected_dates = request.form.getlist("available_dates")
        doctor.availability = ",".join(selected_dates)
        db.session.commit()
        flash("Availability updated successfully!", "alert-success")
        return redirect(url_for("doctor_api.doctor_dashboard"))

    # Split stored availability to highlight checked ones
    available_dates = doctor.availability.split(",") if doctor.availability else []

    # ✅ Send all required data to template
    return render_template(
        "doctor/update_availability.html",
        doctor=doctor,
        dates=next_7_days,
        available=available_dates
    )



# ================================
# ✅ JSON API SECTION (for milestone)
# ================================

@api.route("/api/doctors", methods=["GET"])
def get_doctors_json():
    doctors = Doctor.query.all()
    doctor_list = []
    for d in doctors:
        doctor_list.append({
            "id": d.id,
            "name": d.name,
            "username": d.username,
            "department": d.department,
            "availability": d.availability
        })
    return jsonify(doctor_list)


@api.route("/api/doctors", methods=["POST"])
def add_doctor_json():
    data = request.get_json()
    new_doctor = Doctor(
        doctor_id=data.get("doctor_id"),
        name=data.get("name"),
        username=data.get("username"),
        department=data.get("department"),
        availability=data.get("availability")
    )
    db.session.add(new_doctor)
    db.session.commit()
    return jsonify({"message": "Doctor added successfully"}), 201


@api.route("/api/doctors/<int:id>", methods=["PUT"])
def update_doctor_json(id):
    doctor = Doctor.query.get(id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    data = request.get_json()
    doctor.name = data.get("name", doctor.name)
    doctor.department = data.get("department", doctor.department)
    doctor.availability = data.get("availability", doctor.availability)
    doctor.username = data.get("username", doctor.username)

    user = User.query.get(doctor.doctor_id)
    if user and "username" in data:
        user.username = data["username"]
    db.session.commit()
    return jsonify({"message": "Doctor updated successfully"})


@api.route("/api/doctors/<int:id>", methods=["DELETE"])
def delete_doctor_json(id):
    doctor = Doctor.query.get(id)
    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    db.session.delete(doctor)
    db.session.commit()
    return jsonify({"message": "Doctor deleted successfully"})