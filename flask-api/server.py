import json

from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse

from database import db_session
from models import Sign

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('particle_id')

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Signs(Resource):
    def get(self):
        signs = Sign.query.all()
        return json.dumps([s.id for s in signs])

    def post(self):
        args = parser.parse_args()
        sign = Sign(args['name'], args['particle_id'])
        db_session.add(sign)
        db_session.commit()
        return sign.id


api.add_resource(HelloWorld, '/')
api.add_resource(Signs, '/signs')

if __name__ == '__main__':
    app.run(debug=True)