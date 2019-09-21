from flask import Flask, make_response
from bson import dumps
from flask_jwt_extended import JWTManager
from flask_restful import Api


def output_json(obj, code, headers=None):
    """
    This is needed because we need to use a custom JSON converter
    that knows how to translate MongoDB types to JSON.
    """
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})

    return resp


DEFAULT_REPRESENTATIONS = {'application/json': output_json}

app = Flask(__name__)
app.config['SECRET_KEY'] = '477e856e-e51f-4f80-9858-a7ef2f0b38e1'
app.config['PROPAGATE_EXCEPTIONS'] = True

jwt = JWTManager(app)

api = Api(app, prefix='/api/v1')
api.representations = DEFAULT_REPRESENTATIONS

if __name__ == '__main__':
    app.run(debug=True)
