 #!/usr/bin/env python
import json
import os
import Pyro4
import sys
import threading
import zmq

DEBUG = True

def tprint(msg):
    sys.stdout.write(msg + '\n> ')
    sys.stdout.flush()

def print_rooms(rooms):
    print "#rooms"
    if len(rooms) != 0:
        for room in rooms:
            print "-" + room
    else:
        print "empty list"

def def_username():
    End = False
    while not End:
        username = raw_input("Username> ")
        if username != "":
            return username

class Backend(threading.Thread):
    def __init__(self, username, ctx, output = None):
        super(Backend, self).__init__ ()
        self.__username = username
        self.__ctx     = ctx
        self.__running = False
        self.__boot(output)

    def __boot(self, output = None):
        self.__socket = self.__ctx.socket(zmq.SUB)
        #self.__socket.setsockopt(zmq.SUBSCRIBE, "")
        if output == None:
            self.__print_message = tprint
        else:
            self.__print_message = output

    def connect(self, host, port):
        self.__host = host
        self.__port = port
        try:
            url = "tcp://" + host + ":" + str(port)
            self.__socket.connect(url)
        except:
            print "failed to connect backend to " + url

    def subscribe(self, RoomID):
        self.__socket.setsockopt(zmq.SUBSCRIBE, RoomID)

    def unsubscribe(self, RoomID):
        self.__socket.setsockopt(zmq.SUBSCRIBE, RoomID)

    def __is_running(self):
        return self.__running

    def disconnect(self):
        self.__socket.close()

    def process_message(self, message):
        try:
            json0 = message.find('{')
            message = json.loads(message[json0:])
            if message["from"] != self.__username:
                text = message["message"]
                text = message["from"] + ": " + text
                self.__print_message(text)
        except:
            self.__print_message(message)

    def stop(self):
        self.disconnect()
        self._Thread__stop()

    def run(self):
        self.__running = True
        while True:
            message = self.__socket.recv()
            self.process_message(message)

class Frontend(threading.Thread):
    def __init__(self, ctx):
        super(Frontend, self).__init__ ()
        self.__ctx = ctx
        self.__boot()

    def __boot(self):
        self.__socket = self.__ctx.socket(zmq.PUSH)

    def connect(self, host, port):
        self.__host = host
        self.__port = port
        try:
            url = "tcp://" + host + ":" + str(port)
            self.__socket.connect(url)
        except:
            print "failed to connect frontend to " + url

    def send(self, message):
        self.__socket.send(message)

    def stop(self):
        self.__socket.close()

class ChatClient():
    def __init__(self, output = None):
        self.__registered = False
        self.__connected = False
        self.__output = output
        self.__username = ""
        self.__current_room = None
        self.__ctx = zmq.Context()

    def register_to_nameserver(self, username, ns_host = "localhost", ns_port = 7999):
        try:
            if username == "":
                if DEBUG:
                    print "Invalid Username"
                return False
            self.__username = username
            self.__ns = Pyro4.Proxy("PYRONAME:nameserver.clients")
            if self.__ns.register(username):
                self.__registered = True
                return True
            else:
                if DEBUG:
                    print "Unable to connect"
                return False
        except:
            if DEBUG:
                print "Unable to connect"
            return False

    def unregister(self):
        if self.__username:
            if self.__ns.unregister(self.__username):
                return True
            else:
                print "Unable to logout"
        else:
            print "You are not logged, yet"

    def is_registered(self):
        return self.__registered

    def connect(self, host, frontend_port, backend_port):
        try:
            self.__frontend = Frontend(self.__ctx)
            self.__frontend.connect(host, frontend_port)
            self.__backend = Backend(self.__username, self.__ctx, self.__output)
            self.__backend.connect(host, backend_port)
            self.__backend.start()
            self.__connected = True
            return True
        except:
            return False

    def disconnect(self):
        try:
            self.__frontend.stop()
            self.__backend.stop()
            self.__connected = False
            return True
        except:
            return False

    def is_connected(self):
        return self.__connected

    def list_rooms(self):
        room_list = self.__ns.list_rooms()
        print_rooms(room_list)

    def enter_room(self, RoomID):
        server = self.__ns.enter_room(RoomID, self.__username)
        try:
            if self.connect(server["host"], server["pull_port"], server["pub_port"]):
                self.__current_room = RoomID
                self.__backend.subscribe(RoomID)
                return True
            else:
                if DEBUG:
                    print "Failed to enter room: " + RoomID
                return False
        except:
            print "failed to connect to server"
            return False

    def leave_room(self):
        try:
            self.disconnect()
            self.__ns.leave_room(self.__username)
            self.__current_room = None
            self.__backend.unsubscribe(RoomID)
            return True
        except:
            return False

    def send_message(self, message, to = ""):
        if to == "":
            to = self.__current_room
        try:
            message = {
                "message": message,
                "from": self.__username,
                "RoomID": to
            }
            self.__frontend.send(json.dumps(message))
            return True
        except:
            return False

    def room(self):
        End = False
        while not End:
            cmd = raw_input("> ")
            if cmd == "/exit":
                End = True
                self.leave_room()
                os.system('clear')
            elif cmd != "":

                if not self.send_message(cmd):
                    tprint("Unable to send message!")

    def stop(self):
        if self.__registered:
            self.unregister()
            if self.__connected:
                self.disconnect()
                self.__backend.exit()

    def run(self):
        End = False

        while not End:
            print "X: exit"
            print "L: List Room"
            print "E: Enter Room <RoomID>"
            cmd = raw_input("> ")
            if cmd == "X":
                End = True
            elif cmd == "L":
                self.list_rooms()
            elif cmd == "E":
                roomID = raw_input("RoomID> ")
                if self.__registered:
                    if roomID != "":
                        if self.enter_room(roomID):
                            os.system('clear')
                            print "Room " + roomID
                            self.room()
                    else:
                        print "invalid room ID"
                else:
                    return

def main():
    os.system('clear')
    server = ChatClient()
    if DEBUG and len(sys.argv) == 3:
        server.connect("localhost", sys.argv[1], sys.argv[2])
    else:
        server.register_to_nameserver(def_username())

    if server.is_registered():
        server.run()

    server.stop()
    os.system('reset')

if __name__ == '__main__':
    main()
