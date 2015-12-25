import zmq, sys, requests, json, threading, uuid

class ReplyWorker(threading.Thread):
    def __init__(self, sub_socket):
        super(ReplyWorker, self).__init__ ()
        self.port = 10000
        self.sub_socket = sub_socket
        self.boot()

    def get_port(self):
        return self.port

    def boot(self):
        ctx = zmq.Context()
        End = False

        while not End:
            try:
                self.socket = ctx.socket(zmq.REP)
                self.socket.bind('tcp://*:'  + str(self.port))
                print "Reply Port: " + str(self.port)
                End = True
            except:
                self.port += 1

    def run(self):
        while True:
            response = {}
            response["valid"] = True
            request = self.socket.recv()
            try:
                request = json.loads(request)
                print request
            except:
                print request
            self.sub_socket.connect("tcp://" + request["ip"] + ":" + str(request["port"]))
            self.socket.send(json.dumps(response))
        self.socket.close()

class PullWorker(threading.Thread):
    def __init__(self, pub_socket):
        super(PullWorker, self).__init__ ()
        self.pub_socket = pub_socket
        self.messageDict = {}
        self.port = 8000
        self.boot()

    def get_port(self):
        return self.port

    def add_messages(self, message):
        new_message = {}
        new_message["user"] = message["user"]
        new_message["text"] = message["text"]
        self.messageDict[message["id"]] = new_message

    def get_messages(self, id = ""):
        if id == "":
            return self.messageDict
        else:
            try:
                return self.messageDict[id]
            except:
                return {}

    def boot(self):
        ctx = zmq.Context()
        End = False

        while not End:
            End = False
            try:
                self.socket = ctx.socket(zmq.PULL)
                self.socket.bind('tcp://*:' + str(self.port))
                print "Pull Port: " + str(self.port)
                End = True
            except:
                self.port += 1

    def run(self):
        while True:
            message = self.socket.recv()
            try:
                message = json.loads(message)
            except:
                pass
            id = str(uuid.uuid4())
            self.messageDict[id] = message
            message["id"] = id
            self.pub_socket.send(json.dumps(message))

class ChatServer():
    def __init__(self, ns_port):
        self.name_server_port = ns_port
        self.serverList = []
        self.ip = "localhost"
        self.boot()

    def boot(self):
        ctx = zmq.Context()
        pub_port = 9000

        End = False
        while not End:
            try:
                self.pub = ctx.socket(zmq.PUB)
                self.pub.bind('tcp://*:'+str(pub_port))
                print "Pub Port: " + str(pub_port)
                End = True
            except:
                pub_port += 1
        self.pub_port = pub_port

        self.pull = PullWorker(self.pub)
        self.pull_port = self.pull.get_port()
        self.pull.start()

        self.subscribe = ctx.socket(zmq.SUB)
        self.subscribe.setsockopt(zmq.SUBSCRIBE, "")

        self.reply = ReplyWorker(self.subscribe)
        self.reply_port = self.reply.get_port()
        self.reply.start()

        self.request = ctx.socket(zmq.REQ)

    def connect(self):
        content_data               = {}
        content_data["ip"]         = self.ip
        content_data["pub_port"]   = self.pub_port
        content_data["pull_port"]  = self.pull_port
        content_data["reply_port"] = self.reply_port

        r = requests.post("http://localhost:" + str(self.name_server_port) + "/register", json=json.dumps(content_data))

        try:
            r = json.loads(r.text)
        except:
            print "invalid response"

        message = {}
        message["ip"] = self.ip
        message["port"] = self.pub_port
        for server in r["server_list"]:
            if server["reply_port"] != self.reply_port:
                try:
                    self.request.connect("tcp://" + server["ip"] + ":" + str(server["reply_port"]))
                    self.request.send(json.dumps(message))
                    print self.request.recv()
                    self.request.close()
                except:
                    print "unable to connect to server @ tcp://" + server["ip"] + ":" + str(server["reply_port"])
                try:
                    self.subscribe.connect("tcp://" + server["ip"] + ":" + str(server["pub_port"]))
                except:
                    print "unable to subscribe to server @ tcp://" + server["ip"] + ":" + str(server["pub_port"])
    def run(self):
        while True:
            message = self.subscribe.recv()
            message = json.loads(message)
            if self.pull.get_messages(str(message["id"])) == {}:
                self.pull.add_messages(message)
                self.pub.send(json.dumps(message))
        self.pub.close()
        self.pull._Thread__stop()
        self.reply._Thread__stop()

def main():
    server = ChatServer(7999)
    server.connect()
    server.run()

if __name__ == '__main__':
    main()
