#!/usr/bin/python3

from flask import Flask, g, abort, current_app, request, url_for, jsonify
from flask_restful import Api, Resource, reqparse
from werkzeug.exceptions import HTTPException, InternalServerError
import joblib
import numpy as np
from datetime import datetime
from functools import wraps
import threading
import time
import uuid
import requests
import json
from utils import *
from pymongo import MongoClient
from pprint import pprint

server = Flask(__name__)
API = Api(server)

#IRIS_MODEL = joblib.load('/home/user/eu_workspace/eu-ai-api/iris.mdl')

tasks = {}
'''
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
'''

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
        
        headers = request.headers 
        auth = headers.get("X-Authorization")
         
        if auth != 'asoidewfoef':
            return {"message": "ERROR: Unauthorized"}, 202
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
        return {'request_id': task_id}, 202
    return new_function

class GetTaskStatus(Resource):
    def get(self, task_id):
        """
        Return status about an asynchronous task. If this request returns a 202
        status code, it means that task hasn't finished yet. Else, the response
        from the task is returned.
        """
        headers = request.headers 
        auth = headers.get("X-Authorization")
         
        if auth != 'asoidewfoef':
            return {"message": "ERROR: Unauthorized"}, 202
        task = tasks.get(task_id)
        if task is None:
            abort(404)
        if 'return_value' not in task:
            # Return a 202 response, with an id that the client can use to obtain task status
            return {'status': "in progress"}, 202
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
            'status': 'completed',
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
            'status' : 'completed',
            'scenarios' :
            [
                {
                    "name": "1",
                    "scenes" : 
                    [
                        { 
                            "name" : "1",
                            "value"  : 0.58 
                        },
                        { 
                            "name" : "2",
                            "value": 0.58 
                        },
                        { 
                            "name" : "3",  
                            "value": 0.58 
                        }
                    ]
                },
                {
                    "name" : "2",
                    "scenes" :
                    [
                        
                        { 
                            "name" : "1", 
                            "value" : 0.58 
                        },
                        { 
                            "name" : "1.1", 
                            "value" : 0.58 
                        },
                        { 
                            "name" : "1.2", 
                            "value" : 0.58 
                        },
                        { 
                            "name" : "2.1", 
                            "value" : 0.58 
                        },
                        { 
                            "name" : "2.2",
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "3",
                    "scenes" :
                    [

                        {
                            "name" : "1",
                            "value": 0.58 
                        },
                        {
                            "name" : "2",
                            "value" : 0.58 
                        },
                        {   "name" : "3",
                            "value": 0.58 
                        },
                        { 
                            "name" :"4",
                            "value" : 0.58 },
                        {
                            "name": "5",
                            "value" : 0.58 
                        },
                        {
                            "name" : "6",
                            "value" : 0.58 
                        },
                        {
                            "name" : "7",
                            "value": 0.58 
                        }
                    ]
                },
                {
                    "name" : "4",
                    "scenes" :
                    [

                        {
                            "name" : "1",
                            "value": 0.58 
                        },
                        {
                            "name" :"2", 
                            "value" : 0.58 
                        },
                        {
                            "name" : "3", 
                            "value" : 0.58 
                        },
                        {
                            "name" : "4",
                            "value": 0.58 
                        }
                    ]
                },
                {
                    "name" : "5",
                    "scenes" :
                    [
                    
                        {
                            "name" : "1",
                            "value" : 0.58 
                        },
                        {
                            "name" : "2",
                            "value" : 0.58 
                        },
                        {
                            "name" : "3",
                            "value" : 0.58 
                        },
                        { 
                            "name" : "4",
                            "value" : 0.58 
                        },
                        {
                            "name" : "5",
                            "value" : 0.58 
                        },
                        { 
                            "name" : "6", 
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "6",
                    "scenes" :
                    [
                    
                        {
                            "name" : "1",
                            "value" : 0.58 
                        },
                        {
                            "name" : "2",
                            "value" : 0.58 
                        },
                        {
                            "name" : "3",
                            "value" : 0.58 
                        },
                        {
                            "name" : "4",
                            "value" : 0.58 
                        },
                        {
                            "name" : "5",
                            "value" : 0.58 
                        },
                        {
                            "name" : "6",
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "7",
                    "scenes" : 
                    [
                        {
                            "name": "1",
                            "value" : 0.58 
                        },  
                        { 
                            "name" : "2",
                            "value" : 0.58 
                        },
                        {
                            "name" : "3",
                            "value" : 0.58 
                        },
                        {
                            "name" : "4",
                            "value" : 0.58 
                        },
                        {
                            "name" : "5",
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "8",
                    "scenes" :
                    [
                        {
                            "name" : "1",
                            "value" : 0.58 
                        },
                        {
                            "name" :  "2",
                            "value" : 0.58 
                        },
                        {
                            "name" : "3",
                            "value" : 0.58 
                        },
                        {
                            "name" : "4",
                            "value" : 0.58 
                        },
                        {
                            "name" : "5",
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "9",
                    "scenes" :
                    [
                        {
                            "name" :  "1",
                            "value" : 0.58 
                        },
                        { 
                            "name" : "2",
                            "value" : 0.58 
                        },
                        {
                            "name"  : "3",
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "10",
                    "scenes" : 
                    [
                        {
                            "name" : "1",
                            "value": 0.58 
                        },
                    
                        {
                            "name" : "2",
                            "value": 0.58
                        },
                        {
                            "name" : "3",
                            "value": 0.58 
                        },
                        {
                            "name"  : "4",
                            "value" : 0.58 
                        }
                    ]
                }
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
            'status' : 'completed',
            'scenarios' :
            [
                {
                    "name": "1",
                    "scenes" : 
                    [
                        { 
                            "name" : "1",
                            "value"  : 0.58 
                        },
                        { 
                            "name" : "2",
                            "value": 0.58 
                        },
                        { 
                            "name" : "3",  
                            "value": 0.58 
                        }
                    ]
                },
                {
                    "name" : "2",
                    "scenes" :
                    [
                        
                        { 
                            "name" : "1", 
                            "value" : 0.58 
                        },
                        { 
                            "name" : "1.1", 
                            "value" : 0.58 
                        },
                        { 
                            "name" : "1.2", 
                            "value" : 0.58 
                        },
                        { 
                            "name" : "2.1", 
                            "value" : 0.58 
                        },
                        { 
                            "name" : "2.2",
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "3",
                    "scenes" :
                    [

                        {
                            "name" : "1",
                            "value": 0.58 
                        },
                        {
                            "name" : "2",
                            "value" : 0.58 
                        },
                        {   "name" : "3",
                            "value": 0.58 
                        },
                        { 
                            "name" :"4",
                            "value" : 0.58 },
                        {
                            "name": "5",
                            "value" : 0.58 
                        },
                        {
                            "name" : "6",
                            "value" : 0.58 
                        },
                        {
                            "name" : "7",
                            "value": 0.58 
                        }
                    ]
                },
                {
                    "name" : "4",
                    "scenes" :
                    [

                        {
                            "name" : "1",
                            "value": 0.58 
                        },
                        {
                            "name" :"2", 
                            "value" : 0.58 
                        },
                        {
                            "name" : "3", 
                            "value" : 0.58 
                        },
                        {
                            "name" : "4",
                            "value": 0.58 
                        }
                    ]
                },
                {
                    "name" : "5",
                    "scenes" :
                    [
                    
                        {
                            "name" : "1",
                            "value" : 0.58 
                        },
                        {
                            "name" : "2",
                            "value" : 0.58 
                        },
                        {
                            "name" : "3",
                            "value" : 0.58 
                        },
                        { 
                            "name" : "4",
                            "value" : 0.58 
                        },
                        {
                            "name" : "5",
                            "value" : 0.58 
                        },
                        { 
                            "name" : "6", 
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "6",
                    "scenes" :
                    [
                    
                        {
                            "name" : "1",
                            "value" : 0.58 
                        },
                        {
                            "name" : "2",
                            "value" : 0.58 
                        },
                        {
                            "name" : "3",
                            "value" : 0.58 
                        },
                        {
                            "name" : "4",
                            "value" : 0.58 
                        },
                        {
                            "name" : "5",
                            "value" : 0.58 
                        },
                        {
                            "name" : "6",
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "7",
                    "scenes" : 
                    [
                        {
                            "name": "1",
                            "value" : 0.58 
                        },  
                        { 
                            "name" : "2",
                            "value" : 0.58 
                        },
                        {
                            "name" : "3",
                            "value" : 0.58 
                        },
                        {
                            "name" : "4",
                            "value" : 0.58 
                        },
                        {
                            "name" : "5",
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "8",
                    "scenes" :
                    [
                        {
                            "name" : "1",
                            "value" : 0.58 
                        },
                        {
                            "name" :  "2",
                            "value" : 0.58 
                        },
                        {
                            "name" : "3",
                            "value" : 0.58 
                        },
                        {
                            "name" : "4",
                            "value" : 0.58 
                        },
                        {
                            "name" : "5",
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "9",
                    "scenes" :
                    [
                        {
                            "name" :  "1",
                            "value" : 0.58 
                        },
                        { 
                            "name" : "2",
                            "value" : 0.58 
                        },
                        {
                            "name"  : "3",
                            "value" : 0.58 
                        }
                    ]
                },
                {
                    "name" : "10",
                    "scenes" : 
                    [
                        {
                            "name" : "1",
                            "value": 0.58 
                        },
                    
                        {
                            "name" : "2",
                            "value": 0.58
                        },
                        {
                            "name" : "3",
                            "value": 0.58 
                        },
                        {
                            "name"  : "4",
                            "value" : 0.58 
                        }
                    ]
                }
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
            'status' : 'completed',
            'scenarios' :
            [
                {
                    "name": "1",
                    "scenes" : 
                    [
                        { 
                            "name" : "1",
                            "vr_value"  : 0.58,
                            "empathy_value": 0.77
                        },
                        { 
                            "name" : "2",
                            "vr_value": 0.58,
                            "empathy_value": 0.77
                        },
                        { 
                            "name" : "3",  
                            "vr_value": 0.58,
                            "empathy_value": 0.77
                        }
                    ]
                },
                {
                    "name" : "2",
                    "scenes" :
                    [
                        
                        { 
                            "name" : "1", 
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        { 
                            "name" : "1.1", 
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        { 
                            "name" : "1.2", 
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        { 
                            "name" : "2.1", 
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        { 
                            "name" : "2.2",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        }
                    ]
                },
                {
                    "name" : "3",
                    "scenes" :
                    [

                        {
                            "name" : "1",
                            "vr_value": 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "2",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {   "name" : "3",
                            "vr_value": 0.58,
                            "empathy_value": 0.77
                        },
                        { 
                            "name" :"4",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name": "5",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "6",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "7",
                            "vr_value": 0.58,
                            "empathy_value": 0.77
                        }
                    ]
                },
                {
                    "name" : "4",
                    "scenes" :
                    [

                        {
                            "name" : "1",
                            "vr_value": 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" :"2", 
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "3", 
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "4",
                            "vr_value": 0.58,
                            "empathy_value": 0.77
                        }
                    ]
                },
                {
                    "name" : "5",
                    "scenes" :
                    [
                    
                        {
                            "name" : "1",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "2",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "3",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        { 
                            "name" : "4",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "5",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        { 
                            "name" : "6", 
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        }
                    ]
                },
                {
                    "name" : "6",
                    "scenes" :
                    [
                    
                        {
                            "name" : "1",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "2",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "3",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "4",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "5",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "6",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        }
                    ]
                },
                {
                    "name" : "7",
                    "scenes" : 
                    [
                        {
                            "name": "1",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },  
                        { 
                            "name" : "2",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "3",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "4",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "5",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        }
                    ]
                },
                {
                    "name" : "8",
                    "scenes" :
                    [
                        {
                            "name" : "1",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" :  "2",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "3",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "4",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "5",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        }
                    ]
                },
                {
                    "name" : "9",
                    "scenes" :
                    [
                        {
                            "name" :  "1",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        { 
                            "name" : "2",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name"  : "3",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        }
                    ]
                },
                {
                    "name" : "10",
                    "scenes" : 
                    [
                        {
                            "name" : "1",
                            "vr_value": 0.58,
                            "empathy_value": 0.77
                        },
                    
                        {
                            "name" : "2",
                            "vr_value": 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name" : "3",
                            "vr_value": 0.58,
                            "empathy_value": 0.77
                        },
                        {
                            "name"  : "4",
                            "vr_value" : 0.58,
                            "empathy_value": 0.77
                        }
                    ]
                }
            ]
        }
        return out

class Score(Resource):

    @async_api
    def post(self, uid):
        parser = reqparse.RequestParser()
        parser.add_argument('test_session_id')
        parser.add_argument('model')
        parser.add_argument('vr_configuration')
        parser.add_argument('modification')
        parser.add_argument('vr_big_data_id')
        parser.add_argument('vr_original_name')
        parser.add_argument('bio_big_data_id')
        parser.add_argument('bio_original_name')
        parser.add_argument('questionaire')

        args = parser.parse_args()  # creates dict
        
        url = 'http://64.227.122.210/api/raw-results/'  # localhost and the defined port + endpoint
        vr_uuid = args['vr_big_data_id']
        print(vr_uuid)
        bio_uuid = args['bio_big_data_id']
        vr = requests.get(url + vr_uuid, headers={"X-Authorization": "EbQPR@%wb$YZM25A"}).text
        vr_name = args['vr_original_name']
        if "copy" in vr_name :
            vr_name = vr_name.split('(')[0] + '.csv'
        bio_name = args['bio_original_name']
        if "copy" in bio_name :
            bio_name = bio_name.split('(')[0] + '.txt'
        biometry = requests.get(url + bio_uuid, headers={"X-Authorization": "EbQPR@%wb$YZM25A"}).json()
        #print(biometry)
        respondent = [get_fusion_evals(vr, biometry, from_memory=True, init_vr_time=vr_name, init_bio_time=bio_name)]

        template = ['1_1', '1_2', '1_3', 
                    '2_1', '2_1.1', '2_1.2', '2_2', '2_2.1', '2_2.2', 
                    '3_1', '3_2', '3_3', '3_4', '3_5', '3_6', '3_7', 
                    '4_1', '4_2', '4_3', '4_4', 
                    '5_1', '5_2', '5_3', '5_4', '5_5', '5_6', 
                    '6_1', '6_2', '6_3', '6_4', '6_5', '6_6', 
                    '7_1', '7_2', '7_3', '7_4', '7_5', 
                    '8_1', '8_2', '8_3', '8_4', '8_5', 
                    '9_1', '9_2', '9_3', 
                    '10_1', '10_2', '10_3', '10_4']

        tmp = respondents_to_df(respondent, gen_template(template, ['vr']), only_vr=True)
        competences = ['Self-confidence', 'Self-control', 'Openness to change', 'Responsibility', 'Communicability']
        series = []
        means = []
        for ix, comp in enumerate(competences) :
            series.append(pd.Series(list(tmp[0][comp].values())))
            means.append(series[ix].mean())

        out = {
            "status": "completed",
            "competence_evals" : {
                "self-confidence" : means[0],
                "self-control" : means[1],
                "openness_to_change" : means[2],
                "responsibility" : means[3],                                                                                                                                                                                
                "communicability" : means[4]                                                                                                                                                                            
            }
        }           

        return out

'''
class Testdb(Resource):
    def post(self):
        # connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
        #return {"name" : "gavno"}
        client = MongoClient('mongodb://root:example@mongo:10403/')
        #print('gavno________________________________________________________________________________')
        db=client.aidb
        collection = db.fruits
        result = collection.find_one({"name" : "apple"})
        out = {"name": result["name"], "origin" : result["origin"]}
        # Issue the serverStatus command and print the results
        #serverStatusResult=db.command("serverStatus")
        #out = { "process" : serverStatusResult['process'], "host" : serverStatusResult['host']}
        
        return out
'''

API.add_resource(Score, '/test-sessions/<string:uid>/score')
#API.add_resource(Score, '/score')
API.add_resource(Train, '/train/request')
API.add_resource(AnalysisVR, '/analysis/vr/request')
API.add_resource(AnalysisBio,'/analysis/bio/request')
API.add_resource(AnalysisComplex, '/analysis/complex/request')
#API.add_resource(Testdb, '/testdb')
#API.add_resource(CatchAll, '/<path:path>', '/')
API.add_resource(GetTaskStatus, '/status/<task_id>', '/test-sessions/score/<task_id>', 
								'/train/<task_id>', 
								'/analysis/vr/<task_id>', '/analysis/bio/<task_id>', '/analysis/complex/<task_id>')

if __name__ == '__main__':
    #server.run(host="0.0.0.0", debug=True, port='5000', threaded=True)
    server.run(host="0.0.0.0", debug=True, port='10402', threaded=True)
    # connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
    #client = MongoClient('mongodb://root:example@mongo:27017/')
    #print('gavno________________________________________________________________________________')
    #db=client.admin
    # Issue the serverStatus command and print the results
    #serverStatusResult=db.command("serverStatus")
    #pprint(serverStatusResult)
    
