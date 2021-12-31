import requests
import json
import time
import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-rf", "--request_file", type=str,
                    help="json file with request")
	parser.add_argument("-u", "--url", type=str,
					help="url for post request")
	parser.add_argument("-p", "--port", type=int,
					help="port of server")
	parser.add_argument("-m", "--method", type=str,
					help="method to api")

	args = parser.parse_args()
	request_file = args.request_file
	url = args.url
	port = args.port
	method = args.method
	#url = 'http://95.217.106.4:10402/score'  # localhost and the defined port + endpoint
	api_url = url + ':' + str(port) + '/' + method
	with open(request_file) as fi :
		request = json.load(fi)
	body = request

	test_session_ids = [requests.post(api_url, data=body).json().get('test_session_id')
            for _ in range(2)]
	print(test_session_ids)
	time.sleep(11)
	results = [requests.get(url + ':' + str(port) + '/status/' + str(test_session_id)).json()
           for test_session_id in test_session_ids]
	print(results)