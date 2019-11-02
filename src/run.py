import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

app = Flask(__name__)
app.config.from_pyfile(f"ponto_facil.{os.environ['ENV']}.cfg")

jwt = JWTManager(app)

api = Api(app, prefix='/api/v1')


if __name__ == '__main__':
    app.run(debug=True)
