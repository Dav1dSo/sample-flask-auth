from flask import Flask, request
from models.user import User
from factory import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import logging

app = Flask(__name__)

app.config["SECRET_KEY"] = "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view ='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/", methods=["GET"])
def home():
    return f"Hellow word!"


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json

        user_name = data.get("user_name")
        password = data.get("password")

        if user_name and password:
            user = db.session.query(User).filter(User.username == user_name).first()

            if user is None:
                return {"error": "Usuário não encontrado!"}, 404

            if user and password == user.password:
                login_user(user)
                print(current_user.is_authenticated)
                return {"msg": "Login realizado com sucesso!"}, 200

            return {"error": "Credênciais incorretas!"}, 400
        return {'error': "Username e password devem ser enviádos!"}, 400
        

    except Exception as err:
        logging.error(f"ERROR AO REALIZAR LOGIN: {type(err)} - {err}")
        return {"error": "Ocorreum erro ao relizar login!"}, 500

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    try:
        if current_user.is_authenticated:
            logout_user()
            return {'msg': "Logout realizado com sucesso!"}, 200
        
        return {'error': "Não foi possível realizar logout!"}, 400
        
        
    except Exception as err:
        logging.error(f"ERROR AO REALIZAR LOGOUT: {type(err)} - {err}")
        return {"error": "Ocorreum erro ao relizar logout!"}, 500


if __name__ == "__main__":
    app.run(debug=True)
