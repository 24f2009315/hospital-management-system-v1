from flask import Flask , Blueprint , request , render_template ,flash,redirect,url_for
from application.models import User , db ,Doctor,Patient
from werkzeug.security import check_password_hash , generate_password_hash

api = Blueprint("admin_api",__name__)

@api.route("/admin_dashboard",methods=["GET","POST"])
def admin_dashboard():
    if request.method == "GET":
        all_doctors = Doctor.query.all()
        all_patients = Patient.query.all()
        return render_template("admin/admin_dashboard.html",doctor = all_doctors,patient = all_patients)
    
@api.route("/add_doctors",methods=["GET","POST"])
def add_doctors():
    if request.method == "GET":
        return render_template("admin/add_doctors.html")
    
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        specialization = request.form.get("specialization")
        department_id = request.form.get("department_id")

        if User.query.filter_by(username=username).first():
            flash("username already taken",category="invalid-username")
            return render_template("admin/add_doctors.html")
        
        new_user = User(name = name , username = username , password = generate_password_hash(password) , role='doctor')

        db.session.add(new_user)
        db.session.commit()

        new_doctor = Doctor(doctor_id = new_user.user_id , name = name , username = username , specialization = specialization , department_id = department_id)

        db.session.add(new_doctor)
        db.session.commit()

        flash("doctor added successfully",category="success")
        return redirect(url_for("admin_api.admin_dashboard"))
    return render_template("admin/add_doctors.html")

@api.route("/admin_dashboard/delete_doctor/<int:id>")
def delete_doctor(id):
    one_doctor = Doctor.query.get(id)

    if one_doctor:

        linked_user = User.query.get(one_doctor.user_id)
        if linked_user:
            db.session.delete(linked_user)

        db.session.delete(one_doctor)
        db.session.commit()

    flash("Doctor Deleted Successfully",category="alert-success")
    return redirect(url_for('admin_api.admin_dashboard'))

@api.route("/admin_dashboard/delete_patient/<int:id>")
def delete_patient(id):
    one_patient = Patient.query.get(id)

    if one_patient:

        linked_user = User.query.get(one_patient.user_id)
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
    specialization = request.form.get("specialization")
    department_id = request.form.get("department_id")

    doctor.name = name
    doctor.username = username
    doctor.specialization = specialization
    doctor.department_id = department_id

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
            (Doctor.specialization.ilike(f'%{query}%'))
        ).all()

        patients = Patient.query.filter(
            (Patient.name.ilike(f'%{query}%')) |
            (Patient.contact.ilike(f'%{query}%'))
        ).all()
    return render_template("admin/admin_search.html",doctors = doctors,patients=patients)