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

@app.route('/create-user', methods=['POST'])
def create_user():
    try:      
        user_name = request.json.get('user_name')
        password = request.json.get('password')
        
        username_exists = db.session.query(User).filter(User.username == user_name).first()
        
        if username_exists is not None:
            return {"error": "User name já em uso!"}, 409
        
        if user_name != None and password != None:
            new_user = User(
                username = user_name,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()
            
            return {'msg': "Usuário criado com sucesso!"}, 201
        
        return {'error': "User name e password devem ser enviados!"}, 400
        
    except Exception as err:
        db.session.rollback()
        logging.error(f"ERROR AO CRIAR USUÁRIO: {type(err)} - {err}")
        return {"error": "Ocorreum erro ao realizar logout!"}, 500

@app.route('/get-all-user', methods=['GET'])
@login_required
def get_all_users():
    try:
        
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        filter_user_name = request.args.get("username", None, type=str)
        filter_id = request.args.get("filter_id", None, type=str)
        
        query_users = db.session.query(User)
        
        users_query = query_users
        
        if filter_user_name:
            users_query = users_query.filter(User.username.ilike(f"%{filter_user_name}%"))
            
        if filter_id:
            users_query = users_query.filter(User.id.ilike(f"%{filter_id}%"))
        
        paginate = users_query.paginate(page=page, per_page=per_page, error_out=False)
        
        res = [
            {
                "id": user.id,
                "username": user.username
            } for user in paginate.items
        ]
        
        return res, 200
        
    except Exception as err:
        db.session.rollback()
        logging.error(f"ERROR AO LISTAR USUÁRIOS: {type(err)} - {err}")
        return {"error": "Ocorreum erro ao listar usuários!"}, 500

if __name__ == "__main__":
    app.run(debug=True)
