from flask import Flask , Blueprint , request , render_template ,flash,redirect,url_for
from application.models import User , db ,Doctor,Patient,Appointment,Treatment,Department
from werkzeug.security import check_password_hash , generate_password_hash

api = Blueprint("admin_api",__name__)

@api.route("/admin_dashboard",methods=["GET","POST"])
def admin_dashboard():
    if request.method == "GET":
        all_doctors = Doctor.query.all()
        all_patients = Patient.query.all()
        booked = Appointment.query.filter_by(status="Booked").all()
        completed = Appointment.query.filter_by(status="Completed").all()
        cancelled = Appointment.query.filter_by(status="Cancelled").all()

        total_doctors = len(all_doctors)
        total_patients = len(all_patients)
        total_appointments = len(booked) + len(completed) + len(cancelled)
        appointment_status = {
            "Booked": len(booked),
            "Completed": len(completed),
            "Cancelled": len(cancelled)
        }

        # Build doctor_id -> department map
        doctor_department_map = {doc.doctor_id: doc.department for doc in Doctor.query.all()}
        return render_template("admin/admin_dashboard.html",
            doctors = all_doctors,
            patients = all_patients,
            booked=booked,
            completed=completed,
            cancelled=cancelled,
            doctor_department_map=doctor_department_map,
            total_doctors=total_doctors,
            total_patients=total_patients,
            total_appointments=total_appointments,
            appointment_status=appointment_status)
    
@api.route("/add_doctors",methods=["GET","POST"])
def add_doctors():
    if request.method == "GET":
        all_departments=Department.query.all()
        return render_template("admin/add_doctors.html",all_departments=all_departments)
    
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        department = request.form.get("department")

        if User.query.filter_by(username=username).first():
            flash("username already taken",category="invalid-username")
            return render_template("admin/add_doctors.html")
        
        new_user = User(name=name,username=username,password=generate_password_hash(password),role="doctor")
        db.session.add(new_user)
        db.session.flush()

        new_doctor = Doctor(doctor_id=new_user.user_id,name=name,username=username,department=department)
        db.session.add(new_doctor)
        db.session.commit()
        flash("doctor added successfully",category="success")
        return redirect(url_for("admin_api.admin_dashboard"))
    return render_template("admin/add_doctors.html")

@api.route("/admin_dashboard/delete_doctor/<int:id>")
def delete_doctor(id):
    one_doctor = Doctor.query.get(id)

    if one_doctor:

        linked_user = User.query.get(one_doctor.doctor_id)
        if linked_user:
            db.session.delete(linked_user)
        Appointment.query.filter_by(doctor_id=one_doctor.doctor_id).delete()
        db.session.delete(one_doctor)
        db.session.commit()

    flash("Doctor Deleted Successfully",category="alert-success")
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/admin_dashboard/delete_patient/<int:id>")
def delete_patient(id):
    one_patient = Patient.query.get(id)

    if one_patient:

        linked_user = User.query.get(one_patient.patient_id)
        if linked_user:
            db.session.delete(linked_user)

        db.session.delete(one_patient)
        db.session.commit()

    flash("Patient Deleted Successfully",category="alert-success")
    return redirect(url_for('admin_api.admin_dashboard'))


@api.route("/admin_dashboard/update_doctor/<int:doctor_id>",methods=["GET","POST"])
def update_doctor(doctor_id):
    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
    if not doctor:
        return redirect(url_for('admin_api.admin_dashboard'))
    user = User.query.filter_by(user_id=doctor.doctor_id).first()
    if not user:
        return redirect(url_for('admin_api.admin_dashboard'))
    if request.method == "GET":
        return render_template("admin/update_doctors.html",doctor_id = doctor_id , name = doctor.name , username = doctor.username , specialization = doctor.specialization , department_id = doctor.department_id)
    
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")
    department = request.form.get("department")

    doctor.name = name
    doctor.username = username
    doctor.department = department

    user.name = name
    user.username = username
    if password:
        user.password = generate_password_hash(password)

    db.session.commit()

    flash("Doctor Updated Successfully",category="success")
    return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/admin_dashboard/search",methods=["GET","POST"])
def search_users():
    query = request.form.get("query","").strip()
    doctors = []
    patients = []
    if query:
        doctors = Doctor.query.filter(
            (Doctor.name.ilike(f'%{query}%')) |
            (Doctor.department.ilike(f'%{query}%'))
        ).all()

        patients = Patient.query.filter(
            (Patient.name.ilike(f'%{query}%')) |
            (Patient.contact.ilike(f'%{query}%'))
        ).all()
    return render_template("admin/admin_search.html",doctors = doctors,patients=patients)

@api.route("/admin_dashboard/patient_history/<int:patient_id>")
def patient_history(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    if not patient:
        flash("Patient not found", category='error')
        return redirect(url_for('admin_api.admin_dashboard'))

    # Get all appointments for this patient
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()

    # Get all treatments linked to these appointments
    treatments = Treatment.query.filter(Treatment.appointment_id.in_([appt.appointment_id for appt in appointments])).all()

    return render_template("admin/admin_history.html",patient=patient,treatments=treatments)