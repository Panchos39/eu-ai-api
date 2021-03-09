#!/usr/bin/python3

from flask import Flask
from flask_restful import Api, Resource, reqparse
import joblib
import numpy as np

server = Flask(__name__)
API = Api(server)

#IRIS_MODEL = joblib.load('/home/user/eu_workspace/eu-ai-api/iris.mdl')


class Score(Resource):

    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('test_session_id')
        parser.add_argument('model')
        parser.add_argument('vr_configuration')
        parser.add_argument('modification')
        parser.add_argument('vr_big_data_id')
        parser.add_argument('bio_big_data_id')
        parser.add_argument('questionaire')
        parser.add_argument('hr_feedback')

        args = parser.parse_args()  # creates dict

        #X_new = np.fromiter(args.values(), dtype=float)  # convert input to array

        out = {
            'test_session_id' : "some_id",
            'status': 'Completed',
            'competence_evals' : {
                "self-confidence" : 3,
                "self-control" : 3,
                "openness_to_change" : 3,
                "responsibility" : 3,
                "communicability" : 3
            }           
        }

        return out, 200


API.add_resource(Score, '/score')