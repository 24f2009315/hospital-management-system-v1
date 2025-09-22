from flask import Flask , Blueprint , request , render_template ,flash,redirect,url_for
from application.models import User , db
from werkzeug.security import check_password_hash , generate_password_hash

api = Blueprint("admin_api",__name__)

@api.route("/admin_dashboard",methods=["GET","POST"])
def admin_dashboard():
    if request.method == "GET":
        return render_template("admin/admin_dashboard.html")
    
@api.route("/add_doctors",methods=["GET","POST"])
def add_doctors():
    if request.method == "GET":
        return render_template("admin/add_doctors.html")
    
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("username already taken",category="invalid-username")
            return render_template("admin/add_doctors.html")
        
        new_doctor = User(name = name , username = username , password = generate_password_hash(password) , role='doctor')

        db.session.add(new_doctor)
        db.session.commit()

        flash("doctor added successfully",category="success")
        return redirect(url_for("admin_api.admin_dashboard"))
    return render_template("admin/add_doctors.html")