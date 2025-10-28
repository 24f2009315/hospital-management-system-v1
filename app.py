from flask import Flask , Blueprint , jsonify , request
from application.models import db,User,Department
from werkzeug.security import generate_password_hash
from application.auth import api as auth_api
from application.admin_api import api as admin_api
from application.doctor_api import api as doctor_api
from application.patient_api import api as patient_api
from application.appointment_api import api as appointment_api

def create_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///model.db"
    app.config["SECRET_KEY"]="fgwiigfvssyughgtytfyhj"

    db.init_app(app)
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="vaishnavi").first():
            admin=User(name = "Vaishnavi" , username = "vaishnavi" , password=generate_password_hash("vaishnavi"),role="admin")
            db.session.add(admin)
            db.session.commit()
        if not Department.query.first():
            default_departments = [
                Department(department_name="Cardiology", description="Heart specialists"),
                Department(department_name="Neurology", description="Brain specialists"),
                Department(department_name="Pediatrics", description="Child health specialists")
            ]
            db.session.add_all(default_departments)
            db.session.commit()
    app.register_blueprint(auth_api)
    app.register_blueprint(admin_api)
    app.register_blueprint(doctor_api)
    app.register_blueprint(patient_api)
    app.register_blueprint(appointment_api)
    return app

app=create_app()

if __name__ == "__main__":
    app.debug=True
    app.run()