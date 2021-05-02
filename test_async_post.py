import requests
import json
import time
import argparse
import curlify

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-rf", "--request_file", type=str,
                    help="json file with request")
	parser.add_argument("-u", "--url", type=str,
					help="url for post request")
	parser.add_argument("-p", "--port", type=int,
					help="port of server")
	parser.add_argument("-g", "--group", type=str,
					help="group of methods")
	parser.add_argument("-t", "--test_session_id", type=str,
					help="test session id")
	parser.add_argument("-m", "--method", type=str,
					help="method to api")
	parser.add_argument("-s", "--submethod", type=str,
					help="submethod to api")

	args = parser.parse_args()
	request_file = args.request_file
	url = args.url
	port = args.port
	if args.group is not None :
		group = '/' + args.group
	else :
		group = ''
	if args.test_session_id is not None :
		test_session_id = '/' + args.test_session_id
	else :
		test_session_id = ''
	method = args.method
	if args.submethod is not None :
		submethod = '/' + args.submethod
	else :
		submethod = ''
	#url = 'http://95.217.106.4:10402/score'  # localhost and the defined port + endpoint
	api_url = url + ':' + str(port) + str(group) +  str(test_session_id) + '/' + method + submethod
	print(api_url)
	with open(request_file) as fi :
		request = json.load(fi)
	body = request
	print(body)

	responses = [requests.post(api_url, data=body)
            for _ in range(2)]
	print(curlify.to_curl(responses[0].request))
	print(responses[0].request.url)
	print(responses[0].request.body)
	print(responses[0].request.headers)
	request_ids = [responses[i].json().get('request_id') for i in range(2)]
	print(request_ids)
	time.sleep(3)
	print(url + ':' + str(port) + group + '/' + str(method) + '/' + str(request_ids[0]))
	some = requests.get(url + ':' + str(port) + group + '/' + str(method) + '/' + str(request_ids[0]))
	print(curlify.to_curl(some.request))
	time.sleep(8)
	#print(url + ':' + str(port) + '/' + group + '/'  + str(method) + '/' + str(request_ids[0]))
	results = [requests.get(url + ':' + str(port) +  group + '/' + str(method) + '/' + str(request_id)).json()
           for request_id in request_ids]
	print(results)