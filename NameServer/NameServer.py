from bottle import get, post, request, run
import json, requests

chatServers = []
messageQueue = []

class NameServer():
    def __init__(self, port):
        self.port = port

    @get('/')
    def test():
        return "OK"

    @post('/register')
    def register():
        new_server = {}
        response = {}
        content_data = json.loads(request.json)
        response["valid"] = False
        valid = True
        try:
            if content_data["ip"]:
                new_server["ip"] = str(content_data["ip"])
            else:
                valid = False
            if content_data["pub_port"]:
                new_server["pub_port"] = int(content_data["pub_port"])
            else:
                valid = False
            if content_data["pull_port"]:
                new_server["pull_port"] = int(content_data["pull_port"])
            else:
                valid = False
            if content_data["reply_port"]:
                new_server["reply_port"] = int(content_data["reply_port"])
            else:
                valid = False

            response["valid"] = valid
            if valid:
                chatServers.append(new_server)
                response["server_list"] = chatServers
        except:
            print "ups"

        return response

    def run(self):
        run(host='localhost', port=self.port, debug=True)

if __name__ == '__main__':
    server = NameServer(7999)
    server.run()
