from flask import Flask , Blueprint
from application.models import db,User
from werkzeug.security import generate_password_hash
from application.auth import api as auth_api
from application.admin_api import api as admin_api

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
    app.register_blueprint(auth_api)
    app.register_blueprint(admin_api)
    return app

app=create_app()

if __name__ == "__main__":
    app.debug=True
    app.run()