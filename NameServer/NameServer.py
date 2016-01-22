 #!/usr/bin/env python
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
                if DEBUG:
                    print r.text
                return False
        else:
            return False
    except Exception as e:
        if DEBUG:
            print e
        return False

def get_from_database(url):
    try:
        r = requests.get(url)
        print r.text
        data = json.loads(r.text)
        return data
    except Exception as e:
        if DEBUG:
            print e
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

def remove_server(url, serverID):
    try:
        r = requests.delete(url + "/serverID")
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
            if username:
                if get_from_database(self.__db_url + "/users/" + str(username)):
                    data["command"] = "login"
                    data["user"] = username
                    print send_to_database("PUT", self.__db_url + "/users/", data)
                else:
                    users[username] = {}
                    user = users[username]
                    user["current_server"] = None
                    user["current_room"] = None
                    user["status"] = "ON"
                    user["username"] = username
                    print send_to_database("POST", self.__db_url + "/users/", user)
                return True
            return False
        except:
            return False

    def unregister(self, username):
        if username:
            data = {}
            try:
                user = users[username]
                data["command"] = "logout"
                send_to_database("PUT", self.__db_url + "/users/", user)
            except Exception as e:
                print e

    def list_rooms(self):
      	rooms = get_from_database(self.__db_url + "/rooms/")
        return rooms

    def enter_room(self, RoomID, username):
        if RoomID:
            try:
                data = {}
                room = get_from_database(self.__db_url + "/rooms/" + str(RoomID))
                ServerID = room["server"]
                print self.__db_url + "/servers/" + ServerID
                server = get_from_database(self.__db_url + "/servers/" + ServerID)
                print "Server"
                print server
                if not server:
                    return None
                data["Username"] = username
                data["command"] = "enter"
                send_to_database("PUT", self.__db_url + "/rooms/" + str(RoomID), data)
            except:
                try:
                    servers = get_from_database(self.__db_url + "/servers/")
                    if not servers:
                        return None
                    ServerID = best_server(servers)
                    server = servers[ServerID]
                    new_room = {}
                    new_room["users"] = [username]
                    new_room["server"] = ServerID
                    new_room["RoomID"] = str(RoomID)
                    send_to_database("POST", self.__db_url + "/rooms/", new_room)
                except Exception as e:
                    if DEBUG:
                        print e
                    return None
            return server
        else:
            return None

    def leave_room(self, RoomID, username):
        try:
            if RoomID and username:
                data = {}
                data["Username"] = username
                data["command"] = "exit"
                send_to_database("PUT", self.__db_url + "/rooms/" + RoomID , data)
    	        return True
            else:
                return False
        except:
            return False

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
            return None

    def unregister(self, server_id):
        #rebalancear as salas
        if remove_server(self.__db_url, server_id):
            return True
        else:
            if DEBUG:
                print "failed to add server to the database"
            return False

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
