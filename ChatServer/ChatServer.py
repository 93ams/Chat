 #!/usr/bin/env python
import datetime
import json
import os
import Pyro4
import requests
import sys
import time
import threading
import zmq

DEBUG = True

def tprint(msg):
    sys.stdout.write(msg + '\n> ')
    sys.stdout.flush()

def send_to_database(url, data = None):
    try:
        if data:
            r = requests.post(url, json = data)
            if r.text == "OK":
                return True
            else:
                if DEBUG:
                    tprint(r.text)
                return False
        else:
            return False
    except Exception as e:
        if DEBUG:
            print e
        return False

def find_a_port(socket, starting_port):
    port = starting_port
    End = False
    while not End or port == starting_port + 1000:
        try:
            socket.bind('tcp://*:' + str(port))
            End = True
        except:
            port += 1
    return port

class Heart(threading.Thread):
    def __init__(self, heartbeat_handler, heartbeat_rate, id):
        super(Heart, self).__init__ ()
        self.__heartbeat_handler = heartbeat_handler
        self.__heartbeat_rate = heartbeat_rate
        self.__id = id

    def stop(self):
        self._Thread__stop()

    def run(self):
        data = {"id": self.__id}
        while True:
            data["timedate"] = datetime.datetime.now()
            try:
                self.__heartbeat_handler(data)
            except Exception as e:
                if DEBUG:
                    print e
                self.stop()
            time.sleep(1/float(self.__heartbeat_rate))

class Worker(threading.Thread):
    def __init__(self, pull_socket, push_socket, publish_socket):
        super(Worker, self).__init__ ()
        self.__pull = pull_socket
        self.__push = push_socket
        self.__pub  = publish_socket
        self.__db_url = None

    def set_database_url(self, url):
        self.__db_url = url

    def send_message(self, data):
        try:
            msg = {}
            msg["from"] = data["from"]
            msg["message"] = data["message"]
            msg = data["RoomID"] + ' ' + json.dumps(msg)
            self.__pub.send_string(msg)
            if self.__db_url:
                if send_to_database(self.__db_url + "/messages", data):
                    return True
                else:
                    return False
            return True
        except Exception as e:
            if DEBUG:
                print e
            return False

    def recv_message(self):
        msg = self.__pull.recv()
        try:
            msg = json.loads(msg)
        except:
            pass
        return msg

    def run(self):
        while True:
            data = self.recv_message()
            self.send_message(data)

    def stop(self):
        self._Thread__stop()

class ChatServer():
    def __init__(self, host = "localhost"):
        self.__host       = host
        self.__registered = False
        self.__id         = ""
        self.__boot()

    def __setup_worker(self):
        self.__worker = Worker(self.__pull_socket, self.__push_socket, self.__publish_socket)
        self.__worker.set_database_url("http://localhost:7000/server")

    def __boot(self):
        self.__ctx = zmq.Context()

        self.__pull_socket    = self.__ctx.socket(zmq.PULL)
        self.__publish_socket = self.__ctx.socket(zmq.PUB)
        self.__push_socket    = self.__ctx.socket(zmq.PUSH)

        self.__pull_port = find_a_port(self.__pull_socket, 8000)
        self.__pub_port  = find_a_port(self.__publish_socket,  9000)
        self.__setup_worker()

    def register(self, ns_host, ns_port):
        try:
            self.__ns = Pyro4.Proxy("PYRONAME:nameserver.servers")
            hb_rate = self.__ns.get_heartbeat_rate()
            self.__id = self.__ns.register(self.__host, self.__pull_port, self.__pub_port)
            if self.__id:
                self.__heart = Heart(self.__ns.heartbeat, hb_rate, self.__id)
                self.__heart.start()
                self.__registered = True
                return True

        except Exception as e:
            if DEBUG:
                print e
        return False

    def unregister(self):
        try:
            self.__heart.stop()
            self.__ns.unregister(self.__id)
            self.__registered = False
            return True
        except:
            return False

    def start(self):
        self.__worker.start()
        self.__stopped = False
        while not self.__stopped:
            if DEBUG:
                print "E: to exit"
                print "S: to send a message to another server"
                print "P: to publish a message to the clients"
                cmd = raw_input("> ")
                cmd = cmd.split(":")
                if cmd[0] == "E":
                    self.__stopped = True
                elif cmd[0] == "S":
                    dest = ":".join(cmd[1:])
                    tprint("send message to: " + dest)
                    try:
                        self.__push_socket.connect("tcp://" + dest)
                        message = raw_input("Message> ")
                        self.__push_socket.send(message)
                        self.__push_socket.close()
                    except:
                        tprint("failed")
                elif cmd[0] == "P":
                    message = raw_input("Message> ")
                    self.__publish_socket.send(message)
                else:
                    print "invalid command"

    def stop(self):
        self.__worker.stop()
        self.__pull_socket.close()
        self.__publish_socket.close()
        if self.__registered:
            self.unregister()

def main():
    os.system('clear')
    server = ChatServer()

    if server.register("localhost", 7999) or DEBUG:
        server.start()
    else:
        print "Unable to register server"
    server.stop()
    #os.system('reset')

if __name__ == '__main__':
    main()
