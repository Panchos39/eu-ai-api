#!/usr/bin/python3

from flask import Flask, g, abort, current_app, request, url_for
from flask_restful import Api, Resource, reqparse
from werkzeug.exceptions import HTTPException, InternalServerError
import joblib
import numpy as np
from datetime import datetime
from functools import wraps
import threading
import time
import uuid

server = Flask(__name__)
API = Api(server)

#IRIS_MODEL = joblib.load('/home/user/eu_workspace/eu-ai-api/iris.mdl')

tasks = {}

@server.before_first_request
def before_first_request():
    """Start a background thread that cleans up old tasks."""
    def clean_old_tasks():
        """
        This function cleans up old tasks from our in-memory data structure.
        """
        global tasks
        while True:
            # Only keep tasks that are running or that finished less than 5
            # minutes ago.
            five_min_ago = datetime.timestamp(datetime.utcnow()) - 5 * 60
            tasks = {task_id: task for task_id, task in tasks.items()
                     if 'completion_timestamp' not in task or task['completion_timestamp'] > five_min_ago}
            time.sleep(60)
    print(current_app.config)
    if not current_app.config['TESTING']:
        #print('TESTING')
        thread = threading.Thread(target=clean_old_tasks)
        thread.start()


def async_api(wrapped_function):
    @wraps(wrapped_function)
    def new_function(*args, **kwargs):
        def task_call(flask_app, environ):
            # Create a request context similar to that of the original request
            # so that the task can have access to flask.g, flask.request, etc.
            
            with flask_app.request_context(environ):
                try:
                    tasks[task_id]['return_value'] = wrapped_function(*args, **kwargs)
                except HTTPException as e:
                    tasks[task_id]['return_value'] = current_app.handle_http_exception(e)
                except Exception as e:
                    # The function raised an exception, so we set a 500 error
                    tasks[task_id]['return_value'] = InternalServerError()
                    if current_app.debug:
                        # We want to find out if something happened so reraise
                        raise
                finally:
                    # We record the time of the response, to help in garbage
                    # collecting old tasks
                    tasks[task_id]['completion_timestamp'] = datetime.timestamp(datetime.utcnow())

                    # close the database session (if any)

        # Assign an id to the asynchronous task
        task_id = uuid.uuid4().hex
        # Record the task, and then launch it
        tasks[task_id] = {'task_thread': threading.Thread(
            target=task_call, args=(current_app._get_current_object(),
                               request.environ))}
        tasks[task_id]['task_thread'].start()

        # Return a 202 response, with a link that the client can use to
        # obtain task status
        #print(url_for('gettaskstatus', task_id=task_id))
        #return 'accepted', 202, {'Location': '/status/' + str(task_id)}
        # Return a 202 response, with an id that the client can use to obtain task status
        return {'test_session_id': task_id}, 202
    return new_function

class GetTaskStatus(Resource):
    def get(self, task_id):
        """
        Return status about an asynchronous task. If this request returns a 202
        status code, it means that task hasn't finished yet. Else, the response
        from the task is returned.
        """
        task = tasks.get(task_id)
        if task is None:
            abort(404)
        if 'return_value' not in task:
            # Return a 202 response, with an id that the client can use to obtain task status
            return {'test_session_id': task_id}, 202
            #return '', 202, {'Location': url_for('gettaskstatus', task_id=task_id)}
        return task['return_value']

class CatchAll(Resource):
    @async_api
    def get(self, path=''):
        # perform some intensive processing
        print("starting processing task, path: '%s'" % path)
        time.sleep(10)
        print("completed processing task, path: '%s'" % path)
        return f'The answer is: {path}'

class Train(Resource):
    @async_api
    def post(self) :
        parser = reqparse.RequestParser()
        parser.add_argument('model')
        parser.add_argument('vr_configuration')
        parser.add_argument('modification')
        parser.add_argument('criterion')

        args = parser.parse_args()  # creates dict

        #X_new = np.fromiter(args.values(), dtype=float)  # convert input to array
        time.sleep(10)
        out = {
            'status': 'Completed',
            'metrics' : {
                "accuracy" : 0.88,
                "precision" : 0.77,
                "recall" : 0.60,
                "f-metric" : 0.69,
            }           
        }

        return out
class AnalysisVR(Resource) :
    @async_api
    def post(self) :
        parser = reqparse.RequestParser()
        parser.add_argument('model')
        parser.add_argument('vr_configuration')
        parser.add_argument('modification')

        args = parser.parse_args()  # creates dict

        #X_new = np.fromiter(args.values(), dtype=float)  # convert input to array
        time.sleep(10)
        out = {
            'status' : 'Completed',
            'shapely_evals' :
            [
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 }
                ],
                [   { "1" :   0.58 },
                    { "1.1" : 0.58 },
                    { "1.2" : 0.58 },
                    { "2.1" : 0.58 },
                    { "2.2" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 },
                    { "7" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 }
                ]
            ]
        }
        return out


class AnalysisBio(Resource) :
    @async_api
    def post(self) :
        parser = reqparse.RequestParser()
        parser.add_argument('model')
        parser.add_argument('vr_configuration')
        parser.add_argument('modification')

        args = parser.parse_args()  # creates dict

        #X_new = np.fromiter(args.values(), dtype=float)  # convert input to array
        time.sleep(10)
        out = {
            'status' : 'Completed',
            "empathy_evals" :
            [

                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 }
                ],
                [   { "1" :   0.58 },
                    { "1.1" : 0.58 },
                    { "1.2" : 0.58 },
                    { "2.1" : 0.58 },
                    { "2.2" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 },
                    { "7" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 }
                ]
            ]
        }
        return out


class AnalysisComplex(Resource) :
    @async_api
    def post(self) :
        parser = reqparse.RequestParser()
        parser.add_argument('model')
        parser.add_argument('vr_configuration')
        parser.add_argument('modification')

        args = parser.parse_args()  # creates dict

        #X_new = np.fromiter(args.values(), dtype=float)  # convert input to array
        time.sleep(10)
        out = {
            'status' : 'Completed',
            'shapely_evals' :
            [

                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 }
                ],
                [   { "1" :   0.58 },
                    { "1.1" : 0.58 },
                    { "1.2" : 0.58 },
                    { "2.1" : 0.58 },
                    { "2.2" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 },
                    { "7" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 }
                ]
            ],
            "empathy_evals" :
            [

                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 }
                ],
                [   { "1" :   0.58 },
                    { "1.1" : 0.58 },
                    { "1.2" : 0.58 },
                    { "2.1" : 0.58 },
                    { "2.2" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 },
                    { "7" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                    { "6" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 },
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 },
                    { "5" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 }
                ],
                [
                    { "1" : 0.58 },
                    { "2" : 0.58 },
                    { "3" : 0.58 },
                    { "4" : 0.58 }
                ]
            ]
        }
        return out

class Score(Resource):

    @staticmethod
    def post():
        parser = reqparse.RequestParser()
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
            'status': 'Completed',
            'competence_evals' : {
                "self-confidence" : 2.77,
                "self-control" : 2.68,
                "openness_to_change" : 1.81,
                "responsibility" : 2.99,
                "communicability" : 2.41
            }           
        }

        return out, 200




API.add_resource(Score, '/score')
API.add_resource(Train, '/train')
API.add_resource(AnalysisVR, '/analysis/vr')
API.add_resource(AnalysisBio,'/analysis/bio')
API.add_resource(AnalysisComplex, '/analysis/complex')
#API.add_resource(CatchAll, '/<path:path>', '/')
API.add_resource(GetTaskStatus, '/status/<task_id>')

if __name__ == '__main__':
    server.run(host="0.0.0.0", debug=True, port='5000', threaded=True)