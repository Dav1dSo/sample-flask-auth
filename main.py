from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-secret-key'
app.config("SQLALCHEMY_DATABASE_URI") = 'sqlite:///database.db'

db = SQLAlchemy(app)

@app.route('/', methods=['GET'])
def home():
    return f'hellow word!'

if __name__ == '__main__':
    app.run(debug=True)
    