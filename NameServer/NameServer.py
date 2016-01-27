 #!/usr/bin/env python
#NameServer

import Pyro4
from uuid import uuid4
import requests, json, time, datetime

DEBUG = False

server_list = {}

def send_to_database(method, url, data = None):
    try:
        if data and url and (method == "POST" or method == "PUT"):
            r = requests.request(method, url, json = data)
            if r.text == "OK":
                return True
            else:
                if DEBUG:
                    print "Start"
                    print url
                    print data
                    print r.text
                    print "End"
    except Exception as e:
        if DEBUG:
            print e
    return False

def add_beat(list, beat):
    if len(list) == 5:
        list.pop(0)
    list.append(beat)

def get_from_database(url):
    try:
        r = requests.get(url)
        if DEBUG:
            print r.text
        data = json.loads(r.text)
        return data
    except Exception as e:
        if DEBUG:
            print e
            print url
        return None

def add_server(host, pull_port, pub_port):
    new_server = {}
    try:
        new_server["host"]      = host
        new_server["pull_port"] = int(pull_port)
        new_server["pub_port"]  = int(pub_port)
        id                      = str(uuid4())
        new_server["rooms"]     = []
        new_server["ServerID"]  = id
        return new_server
    except:
        if DEBUG:
            print "failed to create server"
        return None

def remove_server(url, serverID):
    try:
        r = requests.delete(url + "/servers/" + serverID)
        return True
    except:
        if DEBUG:
            print "failed to remove server: " + server_id
        return False

def best_server(server_list):
    best = -1
    try:
        for server in server_list:
            n_rooms = len(server["rooms"])
            if best == -1 or best > n_rooms:
                best = n_rooms
                best_server = server
        return best_server
    except:
        return ""

class NameServerForClients(object):
    def __init__(self, db_url, heartbeat_rate):
        self.__db_url = db_url
        self.__heartbeat_rate = heartbeat_rate

    def register(self, username):
        if username:
            user = get_from_database(self.__db_url + "/users/" + str(username))
            if user:
                data = {}
                data["command"] = "login"
                try:
                    if send_to_database("PUT", self.__db_url + "/users/" + username, data):
                        return True
                except Exception as e:
                    if DEBUG:
                        print e
            else:
                new_user = {}
                new_user["username"] = username
                try:
                    if send_to_database("POST", self.__db_url + "/users/", new_user):
                        return True
                except Exception as e:
                    if DEBUG:
                        print e
        return False

    def unregister(self, username):
        if username:
            try:
                user = get_from_database(self.__db_url + "/users/" + str(username))
                if user:
                    data = {}
                    data["command"] = "logout"
                    if send_to_database("PUT", self.__db_url + "/users/" + str(username), data):
                        return True
            except Exception as e:
                if DEBUG:
                    print e
        return False

    def check_server(self, serverID):
        server = server_list[serverID]
        beat_list = server["last_beats"]
        last_beat = beat_list[len(beat_list) - 1]
        now = datetime.datetime.now()
        if now - last_beat < datetime.timedelta(seconds = 5 * self.__heartbeat_rate):
            return True
        else:
            return False

    def report_crash(self, serverID):
        print "Error @ " + serverID

    def list_rooms(self):
        try:
      	     rooms = get_from_database(self.__db_url + "/rooms/")
             room_list = []
             for room in rooms:
                 room_list.append(str(room["RoomID"]))
             return room_list
        except Exception as e:
            if DEBUG:
                print e
            return []

    def get_room_server(self, RoomID):
        try:
            room = get_from_database(self.__db_url + "/rooms/" + str(RoomID))
            if room:
                ServerID = room["server"]
                server = get_from_database(self.__db_url + "/servers/" + str(ServerID))
                if server:
                    return server
            else:
                server = get_from_database(self.__db_url + "/bestserver")
                if server:
                    new_room = {}
                    new_room["server"] = server["ServerID"]
                    new_room["RoomID"] = str(RoomID)
                    if send_to_database("POST", self.__db_url + "/rooms/", new_room):
                        return server
        except Exception as e:
            if DEBUG:
                print e
        return None

    def enter_room(self, RoomID, username):
        if RoomID:
            try:
                data = {}
                data["command"] = "enter"
                data["RoomID"] = RoomID
                if send_to_database("PUT", self.__db_url + "/users/" + str(username), data):
                    return True
            except Exception as e:
                if DEBUG:
                    print e
        return False

    def leave_room(self, username):
        if username:
            try:
                data = {}
                data["Username"] = username
                data["command"] = "exit"
                if send_to_database("PUT", self.__db_url + "/users/" + str(username) , data):
                    return True
            except Exception as e:
                if DEBUG:
                    print e
        return False

class NameServerForServers(object):
    def __init__(self, db_url, heartbeat_rate):
        self.__db_url = db_url
        self.__heartbeat_rate = heartbeat_rate

    def get_heartbeat_rate(self):
        return self.__heartbeat_rate

    def heartbeat(self, data):
        try:
            server = server_list[data["id"]]
            add_beat(server["last_beats"],  datetime.datetime.now())
        except Exception as e:
            print e

    def register(self, host, pull_port, pub_port):
        #rebalancear as salas

        try:
            server = add_server(host, pull_port, pub_port)
            send_to_database("POST", self.__db_url + "/servers/", server)
            server_list[server["ServerID"]] = {}
            s = server_list[server["ServerID"]]
            s["last_beats"] = []
            return server["ServerID"]
        except Exception as e:
            print "SHIT"
            if DEBUG:
                print e
            return None

    def unregister(self, server_id):

        if remove_server(self.__db_url, server_id):
            return True
        else:
            if DEBUG:
                print "failed to remove server from the database"
            return False

def main():
    db_url = "http://localhost:7000/nameserver" #"http://powerful-link-120314.appspot.com/nameserver"
    heartbeat_rate = 1

    Server_NS = NameServerForServers(db_url, heartbeat_rate)
    Client_NS = NameServerForClients(db_url, heartbeat_rate)

    daemon = Pyro4.Daemon()

    s_ns_uri = daemon.register(Server_NS)
    c_ns_uri = daemon.register(Client_NS)

    ns = Pyro4.locateNS()
    ns.register("nameserver.servers", s_ns_uri)
    ns.register("nameserver.clients", c_ns_uri)

    daemon.requestLoop()

if __name__=="__main__":
    main()
