import requests
import json
if __name__ == '__main__':

	url = 'http://95.217.106.4:10402/score'  # localhost and the defined port + endpoint
	#url = 'http://127.0.0.1:5000/test_sessions/asdasdasdass/score/'
	#url = 'http://127.0.0.1:5000/score'
	with open('request_score.json') as fi :
		request = json.load(fi)
	body = request
	response = requests.post(url, data=body)
	print(response.json())