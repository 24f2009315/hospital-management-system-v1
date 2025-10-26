from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for
from application.models import Doctor,db,Appointment,Patient,User,Department,Treatment

api=Blueprint("doctor_api",__name__)

@api.route("/doctor_dashboard",methods = ["GET","POST"])
def doctor_dashboard():
    if request.method == "GET":
        current_doctor=Doctor.query.first()
        appointments = Appointment.query.filter_by(doctor_id=current_doctor.doctor_id).all()
        patient_map = {p.patient_id: p.name for p in Patient.query.all()}
        return render_template("doctor/doctor_dashboard.html",name=current_doctor.name,appointments=appointments,patient_map=patient_map)

@api.route("/doctor_dashboard/mark_completed/<int:appointment_id>")
def mark_completed(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = "Completed"
        db.session.delete(appointment)
    db.session.commit()
    flash("Appointment marked as completed", "success")
    return redirect(url_for("doctor_api.doctor_dashboard"))

@api.route("/doctor_dashboard/mark_cancelled/<int:appointment_id>")
def mark_cancelled(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = "Cancelled"
        db.session.delete(appointment)
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
        department = Department.query.filter_by(department_id=doctor.department).first() if doctor else None
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