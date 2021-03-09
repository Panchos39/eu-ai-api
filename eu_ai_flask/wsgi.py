from app import server
from app import API

if __name__ == '__main__':
    server.run(host="127.0.0.1", debug=True, port='5000')