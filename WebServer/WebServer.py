 #!/usr/bin/env python
import webapp2
from webapp2_extras import routes
import json

users    = {}
messages = {}
rooms    = {}
servers  = {}

DEBUG = True

#################### WebAppServer ####################

class MainPage(webapp2.RequestHandler):
    def get(self):
        s = ""
        s += '<p>'
        s += '<h4>Messages:  </h4>'
        s += '<a href="html/messages/count">Number of messages </a> &nbsp '
        s += '<a href="html/messages">List of messages </a> &nbsp '
        s += '</p>'

        if users:
            s = '<h3>Users:</h3>'
            for username in users.keys():
                s += '<p>'
                s += '<h4>User: ' + username + ' </h4>'
                s += '<a href="html/' + username + '/users/count">Number of messages of user: ' + username + ' </a> &nbsp '
                s += '<a href="html/' + username + '/users">List of messages of user: ' + username + ' </a> &nbsp '
                s += '</p>'
        else:
            s = '<h3>No User Exist, Yet</h3>'

        if rooms:
            s = '<h3>Rooms:</h3>'
            for RoomID in rooms.keys():
                s += '<p>'
                s += '<h4>Room: ' + RoomID + ' </h4>'
                s += '<a href="html/' + RoomID + '/users/count">Number of users in room: ' + RoomID + ' </a> &nbsp '
                s += '<a href="html/' + RoomID + '/users">List of users in room: ' + RoomID + ' </a> &nbsp '
                s += '<a href="html/' + RoomID + '/messages/count">Number of messages in room: ' + RoomID + ' </a> &nbsp '
                s += '<a href="html/' + RoomID + '/messages">List of messages in room: ' + RoomID + ' </a> &nbsp '
                s += '</p>'
        else:
            s = '<h3>No Room Exist, Yet</h3>'
        self.response.write(s)

###################### WebClient #####################

class UsersCount(webapp2.RequestHandler):
    def get(self, RoomID = None):
        if RoomID:
            users_in_room = 0
            for username, user in users.iteritems():
                if user["current_room"] == str(RoomID):
                    users_in_room += 1
            self.response.write('There are ' + str(users_in_room) + ' users in room: ' + str(RoomID))
        else:
            number_of_users = 0
            for username, user in users.iteritems():
                if user["current_room"] == str(RoomID):
                    number_of_users += 1
            if DEBUG:
                print "number of users: " + str(number_of_users)
            if number_of_users:
                self.response.write('There are ' + str(number_of_users) + ' connected')
            else:
                self.response.write('There are no user connected')

class UsersList(webapp2.RequestHandler):
    def get(self, RoomID = None):
        if RoomID:
        	users_in_room = []
        	for username, user in users.iteritems():
        		if user["current_room"] == str(RoomID):
        			users_in_room.append(username)
        	self.response.write('Users in room ' + str(RoomID) + ': ')
        	self.response.write(users_in_room)
        else:
            if users:
                self.response.write('Active Users: ')
                self.response.write(users)
            else:
                self.response.write('There is no user connected')

class MessagesCount(webapp2.RequestHandler):
    def get(self, RoomID):
        if RoomID:
            try:
            	room = rooms[str(RoomID)]
            	number_of_messages = len(room["messages"])
                if number_of_messages != 0:
                    self.response.write('Number of messages sent: ' + str(number_of_messages))
                else:
                    self.response.write('No message has been sent in this room, yet')
            except:
                self.response.write("This group doesn't exist, yet")
        else:
            number_of_messages = 0
            for room in rooms:
                number_of_messages += len(room["messages"])
            if DEBUG:
                print "number of messages: " + str(number_of_messages)
            if number_of_messages:
                self.response.write('Number of messages sent: ' + str(number_of_messages))
            else:
                self.response.write('No message has been sent, yet')

class MessagesList(webapp2.RequestHandler):
    def get(self, RoomID):
        if RoomID:
            try:
                room = rooms[str(RoomID)]
                if room["messages"]:
                    self.response.write('List of messages of room: ' + str(RoomID))
                    self.response.write(room["messages"])
                else:
                    self.response.write('No message has been sent in this room, yet')
            except:
                self.response.write("Room doesn't exist, yet")
        else:
            messages = []
            for room in rooms:
                messages.extend(room["messages"])
            if messages:
                self.response.write('List of messages: ')
                self.response.write(messages)
            else:
                self.response.write('No message has been sent, yet')

####################### Servers ########################

class Servers(webapp2.RequestHandler):
    def get(self, ServerID = None):
        if ServerID:
            try:
                self.response.write(json.dumps(servers[ServerID]))
            except:
                self.response.write(json.dumps({}))
        else:
            if servers:
                self.response.write(json.dumps(servers))
            else:
                self.response.write(json.dumps({}))

    def post(self, ServerID = None):
        try:
            data = self.request.json
            ServerID = data["ServerID"]
            new_server = {}
            new_server["host"] = data["host"]
            new_server["pub_port"] = data["pub_port"]
            new_server["pull_port"] = data["pull_port"]
            new_server["rooms"] = []
            servers[ServerID] = new_server
            self.response.write('OK')
        except Exception as e:
            if DEBUG:
                print e
            self.response.write('FAIL')

    def delete(self, ServerID):
        try:
            servers.remove(ServerID)
            self.response.write('OK')
        except:
            self.response.write('FAIL')


####################### Rooms ##########################

class Rooms(webapp2.RequestHandler):
    def get(self, RoomID = None):
        if RoomID:
            try:
                self.response.write(json.dumps(rooms[str(RoomID)]))
            except Exception as e:
                if DEBUG:
                    print e
                self.response.write(json.dumps({}))
        else:
            if rooms:
                self.response.write(json.dumps(rooms))
            else:
                self.response.write(json.dumps({}))

    def post(self, RoomID = None):
        try:
            data = self.request.json
            RoomID = str(data["RoomID"])
            new_room = {}
            new_room["users"] = []
            new_room["messages"] = []
            new_room["server"] = data["server"]
            rooms[RoomID] = new_room
            first_user = data["users"][0]
            first_user_name = first_user
            first_user = users[first_user]
            first_user["current_room"] = RoomID
            first_user["current_server"] = new_room["server"]
            new_room["users"].append(first_user_name)
            self.response.write('OK')
        except Exception as e:
            if DEBUG:
                print e
            self.response.write('FAIL')

    def put(self, RoomID):
        try:
            data = self.request.json
            print data
            username = data["Username"]
            user = users[username]
            print "User: "
            print user
            room = rooms[RoomID]
            print "Room: "
            print room
            command = data["command"]
            if command == "enter":
                user["current_room"] = RoomID
                print "Tou a entrar, existem estas mensages: "
                print room["messages"]
                self.response.write('OK')
            elif command == "exit":
                user["current_room"] = None
                room["users"].remove(username)
                print "Tou a sair, ficam estas mensagens: "
                print room["messages"]
                self.response.write('OK')
            else:
                self.response.write('FAIL')
        except Exception as e:
            if DEBUG:
                print e
            self.response.write('FAIL')

####################### Users ###########################

class Users(webapp2.RequestHandler):
    def get(self, UserName = None):
        if UserName:
            try:
                user = users[UserName]
                self.response.write(json.dumps(users[UserName]))
            except:
                self.response.write(json.dumps({}))
        else:
            self.response.write(json.dumps(users))

    def post(self, UserName = None):
        try:
            data = self.request.json
            username = data["username"]
            new_user = {}
            new_user["current_room"] = None
            users[username] = new_user
            self.response.write('OK')
        except:
            self.response.write('FAIL')

    def put(self, UserName):
        try:
            user = users[UserName]
            data = self.request.json
            RoomID = data[RoomID]
            room = rooms[RoomID]
            command = data["command"]
            if command == "login":
                user["status"] = "ON"
                self.response.write('OK')
            elif command == "logut":
                user["status"] = "OFF"
                self.response.write('OK')
            else:
                self.response.write('FAIL')
        except:
            self.response.write('FAIL')

################## Mensages #######################

class Messages(webapp2.RequestHandler):
    def get(self, RoomID = None, MessageID = None):
        if RoomID:
            try:
                room = rooms[RoomID]
                messages = room["messages"]
                if MessageID:
                    self.response.write(json.dumps(messages[messageID]))
                else:
                    self.response.write(json.dumps(messages.values()))
            except Exception as e:
                if DEBUG:
                    print e
                self.response.write(json.dumps({}))
        else:
            if rooms:
                messages = []
                for RoomID, room in rooms.iteritems():
                    if DEBUG:
                        print RoomID
                        print room["messages"]
                    messages.extend(room["messages"])
                self.response.write(json.dumps(messages))
            else:
                self.response.write(json.dumps({}))

    def post(self, RoomID, MessageID = None):
        try:
            data = self.request.json
            room = rooms[RoomID]
            #inserir id da mensagem
            message = data["message"]
            #message["MessageID"] =
            room["messages"].append(message)
            self.response.write('OK')
        except:
            self.response.write('FAIL')

app = webapp2.WSGIApplication([
    webapp2.Route(r'/', MainPage),

    webapp2.Route(r'/html/users', UsersList),
    webapp2.Route(r'/html/users/count', UsersCount),
    webapp2.Route(r'/html/<RoomID:\w+>/users/count', UsersCount),
    webapp2.Route(r'/html/<RoomID:\w+>/users', UsersList),
    webapp2.Route(r'/html/<RoomID:\w+>/messages/count', MessagesCount),
    webapp2.Route(r'/html/<RoomID:\w+>/messages', MessagesList),

    webapp2.Route(r'/nameserver/servers/<ServerID:[\w-]*>', Servers),
    webapp2.Route(r'/nameserver/rooms/<RoomID:\w*>', Rooms),
    webapp2.Route(r'/nameserver/users/<UserName:\w*>', Users),

    webapp2.Route(r'/server/messages', Messages),
    webapp2.Route(r'/server/<RoomID:\w+>/messages', Messages),
    webapp2.Route(r'/server/<RoomID:\w+>/messages/<MessageID>', Messages),

], debug=True)

def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='7000')

if __name__ == '__main__':
    main()
