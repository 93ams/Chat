import Pyro4

servers = []
rooms = {}
users = {}

def add_server(host, pull_port, pub_port):
    new_server = {}
    try:
        new_server["host"]      = host
        new_server["pull_port"] = int(pull_port)
        new_server["pub_port"]  = int(pub_port)
        new_server["rooms"]     = []
        servers.append(new_server)
    except:
        print "failed to add server " + host + ":" + str(pull_port) + "/" + str(pub_port) + " to list"

def best_server():
    best = 1000
    best_index =-1
    index = 0
    for index in range(len(servers)):
        server = servers[index]
        n_rooms = len(server["rooms"])
        if best == -1 or best > n_rooms:
            best = n_rooms
            best_index = index
        index += 1
    return servers[best_index]

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

    def get_room_list(self):
        return rooms.keys()

    def leave_room(self, RoomID):
        room = rooms[RoomID]
        room["users"].remove(username)
        if not room["users"]:
            server = room["server"]
            server["rooms"].remove(RoomID)
            room["server"] = None

    def enter_room(self, RoomID, username):
        server = best_server()
        try:
            room = rooms[RoomID]
            server = room["server"]
            room["users"].append(username)
        except:
            rooms[RoomID] = {}
            room = rooms[RoomID]
            room["users"] = [username]
            room["server"] = server
            server["rooms"].append(RoomID)
        return server

class NameServerForServers(object):
    def __init__(self):
        self.__registered = False

    def register(self, host, pull_port, pub_port):
        self.__host      = host
        self.__pull_port = pull_port
        self.__pub_port  = pub_port
        add_server(host, pull_port, pub_port)
        #enviar para a base de dados, webserver e/ou meter no dicionario
        self.__registered = True

    def unregister(self):
        self.__registered = False

    def is_registered(self):
        return self.__registered

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
