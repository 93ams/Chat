#NameServer

import Pyro4
from uuid import uuid4
import requests, json

servers = {}
rooms = {}
users = {}

DEBUG = True

def send_to_database(method, url, data = None):
    try:
        if data and url and (method == "POST" or method == "PUT"):
            r = requests.request(method, url, json = data)
            if r.text == "OK":
                return True
            else:
                print r.text
                return False
        else:
            return False
    except Exception as e:
        print e
        return False

def get_from_database(url):
    try:
        r = requests.get(url)
        return json.loads(r.text)
    except:
        return None

def add_server(host, pull_port, pub_port):
    new_server = {}
    try:
        new_server["host"]      = host
        new_server["pull_port"] = int(pull_port)
        new_server["pub_port"]  = int(pub_port)
        id                      = str(uuid4())
        new_server["rooms"]     = []
        servers[id]             = new_server
        new_server["ServerID"]  = id
        return new_server
    except:
        if DEBUG:
            print "failed to create server"
        return None

def remove_server(server_id):
    try:
        del servers[server_id]
        return True
    except:
        if DEBUG:
            print "failed to remove server: " + server_id
        return False

def best_server(server_list):
    best = -1
    best_server = ""
    try:
        for ServerID, server in server_list.iteritems():
            n_rooms = len(server["rooms"])
            if best == -1 or best > n_rooms:
                best = n_rooms
                best_server = ServerID
        return best_server
    except:
        return ""

class NameServerForClients(object):
    def __init__(self):
        self.__db_url = "http://localhost:7000/nameserver"

    def register(self, username):
        try:
            user = users[username]
            user["status"] = "ON"
            send_to_database("PUT", self.__db_url + "/users/", user)
        except:
            users[username] = {}
            user = users[username]
            user["current_server"] = None
            user["current_room"] = None
            user["status"] = "ON"
            user["username"] = username
            send_to_database("POST", self.__db_url + "/users/", user)

    def unregister(self, username):
        user = users[username]
        user["status"] = "OFF"
        send_to_database("PUT", self.__db_url + "/users/", user)

    def list_rooms(self):
      	rooms = get_from_database(self.__db_url + "/rooms/")
        return rooms

    def enter_room(self, RoomID, username):
        try:
            rooms = get_from_database(self.__db_url + "/rooms/" + RoomID)
            print "Rooms: "
            print rooms
            room = rooms[RoomID]
            ServerID = room["server"]
            server = servers[ServerID]
            room["users"].append(username)
            send_to_database("PUT", self.__db_url + "/rooms/", room)
        except:
            try:
                servers = get_from_database(self.__db_url + "/servers/")
                ServerID = best_server(servers)
                server = servers[ServerID]
                new_room = {}
                new_room["users"] = [username]
                new_room["server"] = ServerID
                new_room["RoomID"] = RoomID
                print send_to_database("POST", self.__db_url + "/rooms/", new_room)
            except Exception as e:
                print e
                return None
        user = users[username]
        user["current_room"] = RoomID
        user["current_server"] = ServerID

        return server

    def leave_room(self, RoomID, username):
        room = rooms[RoomID]
        room["users"].remove(username)
        user = users[username]
        user["current_room"] = None
        user["current_server"] = None
        #send_to_database()

        if not room["users"]:
            #fazer isto no webserver
            ServerID = room["server"]
            server = servers[ServerID]
            server["rooms"].remove(RoomID)
            room["server"] = None
        else:
        	pass

class NameServerForServers(object):
    def __init__(self):
        self.__db_url = "http://localhost:7000/nameserver"

    def register(self, host, pull_port, pub_port):
        #rebalancear as salas
        try:
            server = add_server(host, pull_port, pub_port)
            send_to_database("POST", self.__db_url + "/servers/", server)
            return server["ServerID"]
        except:
            if DEBUG:
                print "failed to add server to the database"
            return False

    def unregister(self, server_id):
        #rebalancear as salas
        return remove_server(server_id)

def main():
    Server_NS = NameServerForServers()
    Client_NS = NameServerForClients()

    daemon = Pyro4.Daemon()

    s_ns_uri = daemon.register(Server_NS)
    c_ns_uri = daemon.register(Client_NS)

    ns = Pyro4.locateNS()
    ns.register("nameserver.servers", s_ns_uri)
    ns.register("nameserver.clients", c_ns_uri)

    daemon.requestLoop()

if __name__=="__main__":
    main()
