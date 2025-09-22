from flask import Flask , Blueprint , request , render_template ,flash,redirect,url_for
from application.models import User , db
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
        flash("Invalid user",category="invalid-username")
        return render_template("login.html")
    
    if user.role == "patient":
        return f"you are a patient"
    elif user.role == "doctor":
        return f"you are a doctor"
    return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")

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
    
    new_patient=User(name = name , username = username , password = generate_password_hash(password),role='patient')
    db.session.add(new_patient)
    db.session.commit()

    flash("Signup successful",category="success")
    return render_template("login.html")