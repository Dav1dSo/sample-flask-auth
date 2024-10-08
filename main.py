from flask import Flask, request
from models.user import User
import bcrypt
from factory import db
from flask_login import (
    LoginManager,
    login_user,
    current_user,
    logout_user,
    login_required,
)
import logging

app = Flask(__name__)

app.config["SECRET_KEY"] = "your-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost:5432/mydatabase'

login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"


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

            if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                login_user(user)
                print(current_user.is_authenticated)
                return {"msg": "Login realizado com sucesso!"}, 200

            return {"error": "Credênciais incorretas!"}, 400
        return {"error": "Username e password devem ser enviádos!"}, 400

    except Exception as err:
        logging.error(f"ERROR AO REALIZAR LOGIN: {type(err)} - {err}")
        return {"error": "Ocorreum erro ao relizar login!"}, 500


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    try:
        if current_user.is_authenticated:
            logout_user()
            return {"msg": "Logout realizado com sucesso!"}, 200

        return {"error": "Não foi possível realizar logout!"}, 400

    except Exception as err:
        logging.error(f"ERROR AO REALIZAR LOGOUT: {type(err)} - {err}")
        return {"error": "Ocorreum erro ao relizar logout!"}, 500


@app.route("/create-user", methods=["POST"])
def create_user():
    try:
        user_name = request.json.get("user_name")
        password = request.json.get("password")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        username_exists = (
            db.session.query(User).filter(User.username == user_name).first()
        )

        if username_exists is not None:
            return {"error": "User name já em uso!"}, 409

        if user_name != None and password != None:
            new_user = User(username=user_name, password=hashed_password.decode('utf-8'), role='user')
            db.session.add(new_user)
            db.session.commit()

            return {"msg": "Usuário criado com sucesso!"}, 201

        return {"error": "User name e password devem ser enviados!"}, 400

    except Exception as err:
        db.session.rollback()
        logging.error(f"ERROR AO CRIAR USUÁRIO: {type(err)} - {err}")
        return {"error": "Ocorreum erro ao criar usuário!"}, 500


@app.route("/get-all-user", methods=["GET"])
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
            users_query = users_query.filter(
                User.username.ilike(f"%{filter_user_name}%")
            )

        if filter_id:
            users_query = users_query.filter(User.id.ilike(f"%{filter_id}%"))

        paginate = users_query.paginate(page=page, per_page=per_page, error_out=False)

        res = [{"id": user.id, "username": user.username} for user in paginate.items]

        return res, 200

    except Exception as err:
        db.session.rollback()
        logging.error(f"ERROR AO LISTAR USUÁRIOS: {type(err)} - {err}")
        return {"error": "Ocorreum erro ao listar usuários!"}, 500


@app.route("/get-user-by-id/<int:user_id>", methods=["GET"])
@login_required
def get_user(user_id):
    try:

        get_user = db.session.query(User).filter(User.id == user_id).first()

        if get_user is None:
            return {'msg': 'Nenhum usuário encontrado!'}, 404
        
        res = {"id": get_user.id, "username": get_user.username}

        return res, 200

    except Exception as err:
        db.session.rollback()
        logging.error(f"ERROR AO LISTAR USUÁRIOS: {type(err)} - {err}")
        return {"error": "Ocorreum erro ao listar usuários!"}, 500

@app.route("/delete-user/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    try:
        
        if current_user.role != 'admin':
            return {'error': 'Operação não permitida'}, 403
                
        if current_user.id != user_id and current_user.role == 'user':
            return {'error': 'Você não tem permissão para realizar está ação!'}, 403
        
        user_to_delete = db.session.query(User).filter(User.id.ilike(f"%{user_id}%")).first()
    
        if user_to_delete is None:
            return {'error': 'Usuário não encontrado!'}, 404

        db.session.delete(user_to_delete)
        db.session.commit()
    
        return {"msg": 'Usuário deletado com sucesso!'}, 200
    
    except Exception as err:
        db.session.rollback()
        logging.error(f"ERROR AO DELETAR USUÁRIO {type(err)} - {err}")
        return {"error": "Ocorreum erro ao deletar usuário!"}, 500 
    
@app.route("/update-user/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    try:
        
        user_name = request.json.get("user_name")
        password = request.json.get("password")
        
        if current_user.role != 'admin':
            return {'error': 'Operação não permitida'}, 403
                
        if current_user.id != user_id and current_user.role == 'user':
            return {'error': 'Você não tem permissão para realizar está ação!'}, 403
        
        if user_name != None and password != None:
            user_to_update = db.session.query(User).filter(User.id == user_id).first()
        
            if user_to_update is None:
                return {'error': 'Usuário não encontrado!'}, 404

            user_to_update.username = user_name
            user_to_update.password = password

            db.session.commit()
        
            return {"msg": 'Usuário atualizado com sucesso!'}, 200

        return {"error": "User name e password devem ser enviados!"}, 400
        
    except Exception as err:
        db.session.rollback()
        logging.error(f"ERROR AO ATUALIZAR USUÁRIO {type(err)} - {err}")
        return {"error": "Ocorreum erro ao atualizar usuário!"}, 500 

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
