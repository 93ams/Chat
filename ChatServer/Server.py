import zmq, sys, requests, json, threading, uuid
###################################################################
#  ReplyWorker(sub_socket)                                        #
#                                                                 #
#  Thread para processar os pedidos que chegam ao porto de reply, #
#  recebe na mensagem o url do publisher do novo servidor         #
#                                                                 #
###################################################################
class ReplyWorker(threading.Thread):
    def __init__(self, sub_socket):
        super(ReplyWorker, self).__init__ ()
        self.port = 10000            #porto de reply
        self.socket = ctx.socket(zmq.REP) #socket de reply
        self.sub_socket = sub_socket #socket para registar novos servidores como publishers
        self.boot()

    def get_port(self):
        return self.port

    def boot(self):
        ctx = zmq.Context()
        End = False

        while not End:  #procura porto livre para fazer bind da socket de reply
            try:
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
                response["valid"] = False
            self.sub_socket.connect("tcp://" + request["ip"] + ":" + str(request["port"]))
                         # ^ regista endereço como publisher
            self.socket.send(json.dumps(response))
        self.socket.close()

###################################################################
#  PullWorker(pub_socket)                                         #
#                                                                 #
#  Processa as mensagens recebidas no porto de pull, guarda e     #
#  reenvia para todos os subscribers.                             #
#                                                                 #
###################################################################

class PullWorker(threading.Thread):
    def __init__(self, pub_socket):
        super(PullWorker, self).__init__ ()
        self.pub_socket = pub_socket
        self.messageDict = {}              #armazena as mensagens recebidas
        self.port = 8000                   #porto de pull
        self.socket = ctx.socket(zmq.PULL) #socket de pull
        self.boot()

    def get_port(self):
        return self.port

    #adiciona a mensagem ao dicionario
    def add_messages(self, message):
        new_message = {}
        new_message["user"] = message["user"]
        new_message["text"] = message["text"]
        self.messageDict[message["id"]] = new_message

    #vai buscar mensagem(ns) ou devolve dicionario vazio
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
            try: #procura porto livre para fazer bind da socket de pull
                self.socket.bind('tcp://*:' + str(self.port))
                print "Pull Port: " + str(self.port)
                End = True
            except:
                self.port += 1

    #guarda a mensagem e reenvia a para todos os subscribers
    def run(self):
        while True:
            message = self.socket.recv()
            try:
                message = json.loads(message)
            except:
                pass
            id = str(uuid.uuid4())
            self.messageDict[id] = message #guarda a mensagem
            message["id"] = id
            self.pub_socket.send(json.dumps(message))

class ChatServer():
    def __init__(self, ns_port):
        #porto do servidor de nomes para se registar
        self.name_server_port = ns_port
        self.ip = "localhost"
        self.boot()

    #cria as sockets e faz bind nos respectivos portos
    def boot(self):
        ctx = zmq.Context()
        pub_port = 9000

        End = False
        while not End:
            try: #procura porto livre para fazer bind da socket de pub
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

        self.subscribe = ctx.socket(zmq.SUB)         #nao percebo porque mas
        self.subscribe.setsockopt(zmq.SUBSCRIBE, "") #< isto é obrigatorio

        self.reply = ReplyWorker(self.subscribe) #cria o worker de reply
        self.reply_port = self.reply.get_port()  #descobre o seu porto
        self.reply.start()                       #e mete o a trabalhar

        self.request = ctx.socket(zmq.REQ)

    def connect(self):
        content_data               = {}
        content_data["ip"]         = self.ip
        content_data["pub_port"]   = self.pub_port
        content_data["pull_port"]  = self.pull_port
        content_data["reply_port"] = self.reply_port
        #envia informação para o servidor de nomes, para se registar
        #e para saber os enderecos dos outros servidores
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
                try: #envia pedido para o outro servidor se registar como subscriber
                    self.request.connect("tcp://" + server["ip"] + ":" + str(server["reply_port"]))
                    self.request.send(json.dumps(message))
                    print self.request.recv()
                    self.request.close()
                except:
                    print "unable to connect to server @ tcp://" + server["ip"] + ":" + str(server["reply_port"])
                try: #regista se como subscriber do respectivo servidor
                    self.subscribe.connect("tcp://" + server["ip"] + ":" + str(server["pub_port"]))
                except:
                    print "unable to subscribe to server @ tcp://" + server["ip"] + ":" + str(server["pub_port"])
    def run(self):
        while True:
            message = self.subscribe.recv() #recebe mensagem
            message = json.loads(message)   #verifica se existe
            if self.pull.get_messages(str(message["id"])) == {}:
                self.pull.add_messages(message)    #caso não exista, guarda
                self.pub.send(json.dumps(message)) #e envia para os seus
        self.pub.close()         #fecha as sockets #subscribers
        self.pull._Thread__stop()#para as thread
        self.reply._Thread__stop()#mas ainda não pus condicao de paragem no
                                  #ciclo, portanto isto e irrelevante
def main():
    server = ChatServer(7999)
    server.connect()
    server.run()

if __name__ == '__main__':
    main()
