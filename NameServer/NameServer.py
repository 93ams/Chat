import Pyro4
from uuid import uuid4

servers = {}
rooms = {}
users = {}

def remove_server(server_id):
    try:
        del servers[server_id]
        return True
    except:
        print "failed to remove server"
        return False

def add_server(host, pull_port, pub_port):
    new_server = {}
    try:
        new_server["host"]      = host
        new_server["pull_port"] = int(pull_port)
        new_server["pub_port"]  = int(pub_port)
        new_server["rooms"]     = []
        id = str(uuid4())
        servers[id] = new_server
        return id
    except:
        print "failed to add server " + host + ":" + str(pull_port) + "/" + str(pub_port) + " to list"

def best_server():
    best = 1000
    best_server = None
    for serverID in servers:
        server = servers[serverID]
        n_rooms = len(server["rooms"])
        if best == -1 or best > n_rooms:
            best = n_rooms
            best_server = serverID
    return best_server

class NameServerForClients(object):
    def __init__(self):
        pass

    def register(self, username):
        try:
            user = users[username]
        except:
            users[username] = {}
            user = users[username]
            user["current_server"] = None
            user["current_room"] = None
        user["status"] = "ON"

    def unregister(self, username):
        user = users[username]
        user["status"] = "OFF"

    def list_rooms(self):
        return rooms.keys()

    def enter_room(self, RoomID, username):
        try:
            room = rooms[RoomID]
            serverID = room["server"]
            server = servers[serverID]
            room["users"].append(username)
        except:
            serverID = best_server()
            server = servers[serverID]
            rooms[RoomID] = {}
            room = rooms[RoomID]
            room["users"] = [username]
            room["server"] = server
            server["rooms"].append(RoomID)

        user = users[username]
        user["current_room"] = RoomID
        user["current_server"] = serverID

        return server

    def leave_room(self, RoomID, username):
        room = rooms[RoomID]
        room["users"].remove(username)
        room["current_room"] = None
        room["current_server"] = None

        if not room["users"]:
            server = room["server"]
            server["rooms"].remove(RoomID)
            room["server"] = None

class NameServerForServers(object):
    def __init__(self):
        pass

    def register(self, host, pull_port, pub_port):
        return add_server(host, pull_port, pub_port)

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
