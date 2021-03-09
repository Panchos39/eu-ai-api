import requests
import json
import time
if __name__ == '__main__':

	#url = 'http://95.217.106.4:10402/score'  # localhost and the defined port + endpoint
	url = 'http://127.0.0.1:5000/some:some'
	task_ids = [requests.get('http://127.0.0.1:5000/foo').json().get('TaskId')
            for _ in range(2)]
	print(task_ids)
	time.sleep(11)
	results = [requests.get('http://127.0.0.1:5000/status/' + str(task_id)).json()
           for task_id in task_ids]
	print(results)
	#print(response.json())