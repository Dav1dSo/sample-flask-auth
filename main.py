from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return f'hellow word!'

if __name__ == '__main__':
    app.run(debug=True)