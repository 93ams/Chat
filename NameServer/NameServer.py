from bottle import Bottle, request
import json

class NameServer(Bottle):
    def __init__(self, host, port):
        super(NameServer, self).__init__()
        self._host = host
        self._port = port
        self._server_list = []
        self._routes()

    def _routes(self):
        self.route('/register', method="POST", callback=self._register)

    def start(self):
        self.run(host=self._host, port=self._port)

    def _register(self):
        response = {}
        new_server = {}
        try:
            content_data = json.loads(request.body.read())
            new_server["ip"] = str(content_data["ip"])
            new_server["pub_port"] = int(content_data["pub_port"])
            new_server["pull_port"] = int(content_data["pull_port"])
            new_server["reply_port"] = int(content_data["reply_port"])
            response["server_list"] = self._server_list[:]
            response["valid"] = True
            self._server_list.append(new_server)
        except:
            response["valid"] = False

        return json.dumps(response)

if __name__ == '__main__':
    server = NameServer(host='localhost', port=7999)
    server.start()
