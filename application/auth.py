from flask import Flask , Blueprint , request , render_template ,flash,redirect,url_for
from application.models import User , db ,Patient
from werkzeug.security import check_password_hash , generate_password_hash

api = Blueprint("auth",__name__)

@api.route("/",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username = username).first()
    if not user or not check_password_hash(user.password , password):
        flash("Invalid user",category="invalid-email")
        return render_template("login.html")
    
    if user.role == "patient":
        return redirect(url_for("patient_api.patient_dashboard"))
    elif user.role == "doctor":
        return redirect(url_for("doctor_api.doctor_dashboard"))
    return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")
    age = request.form.get("age")
    gender = request.form.get("gender")
    address = request.form.get("address")
    contact = request.form.get("contact")

    user=User.query.filter_by(username=username).first()

    if user:
        flash("username already taken",category="invalid-user")
        return render_template("signup.html",name = name , username = username)
    
    if not name:
        flash("Field required",category="invalid-name")
        return render_template("signup.html")
    
    if not username:
        flash("Field required",category="invalid-username")
        return render_template("signup.html")
    
    new_user=User(name = name , username = username , password = generate_password_hash(password),role='patient')
    db.session.add(new_user)
    db.session.commit()

    new_patient = Patient(patient_id = new_user.user_id , name = name , username = username , age = age , gender = gender , contact = contact , address = address)
    db.session.add(new_patient)
    db.session.commit()

    flash("Signup successful",category="success")
    return render_template("login.html")