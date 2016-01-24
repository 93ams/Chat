 #!/usr/bin/env python

import json
import webapp2
from webapp2_extras import routes
from DataBase import DataBase

users    = {}
messages = {}
rooms    = {}

DEBUG = True

#################### WebAppServer ####################

database = DataBase()

class MainPage(webapp2.RequestHandler):
    def get(self):
        
        s = ""
        s += '<p>'
        s += '<h4>Messages:  </h4>'
        s += '<a href="html/messages/count">Number of messages </a> &nbsp '
        s += '<a href="html/messages">List of messages </a> &nbsp '
        s += '</p>'

        try:
            users = database.users.get()

            if users:
                s += '<h3>Users:</h3>'
                for user in users:
                    s += '<p>'
                    s += '<h4>User: ' + user["Username"] + ' </h4>'
                    s += '<a href="html/users/' + user["Username"] + '/messages/count">Number of messages of user: ' + user["Username"] + ' </a> &nbsp '
                    s += '<a href="html/users/' + user["Username"] +'/messages">List of messages of user: ' + user["Username"] + ' </a> &nbsp '
                    s += '</p>'
            else:
                s += '<h3>No User Exist, Yet</h3>'
        except:
            pass

        try:
            rooms = database.rooms.get()
            if rooms:
                s += '<h3>Rooms:</h3>'
                for room in rooms:
                    s += '<p>'
                    s += '<h4>Room: ' + room["RoomID"] + ' </h4>'
                    s += '<a href="html/' + room["RoomID"] + '/users/count">Number of users in room: ' + room["RoomID"] + ' </a> &nbsp '
                    s += '<a href="html/' + room["RoomID"] + '/users">List of users in room: ' + room["RoomID"] + ' </a> &nbsp '
                    s += '<a href="html/' + room["RoomID"] + '/messages/count">Number of messages in room: ' + room["RoomID"] + ' </a> &nbsp '
                    s += '<a href="html/' + room["RoomID"] + '/messages">List of messages in room: ' + room["RoomID"] + ' </a> &nbsp '
                    s += '</p>'
            else:
                s += '<h3>No Room Exist, Yet</h3>'
        except:
            pass

        self.response.write(s)

###################### WebClient #####################

class UsersCount(webapp2.RequestHandler):
    def get(self, RoomID = None):
        if RoomID:
            users = database.users.get()
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
                self.response.write('There are no users, yet')

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
    def get(self, RoomID = None, Username = None):
        if RoomID:
            try:
                number_of_messages = 0
                for OuterID, message in messages.iteritems():
                    if message["RoomID"] == str(RoomID):
                        number_of_messages += 1
                if number_of_messages != 0:
                    self.response.write('Number of messages sent: ' + str(number_of_messages))
                else:
                    self.response.write('No message has been sent in this room, yet')
            except:
                self.response.write("This group doesn't exist, yet")
        elif Username:
            try:
                number_of_messages = 0
                for OuterID, message in messages.iteritems():
                    if message["from"] == str(Username):
                        number_of_messages += 1
                if message_list:
                    self.response.write('Number of messages sent: ' + str(number_of_messages))
                else:
                    self.response.write('No message has been sent by this user, yet')
            except Exception as e:
                print e
                self.response.write("User doesn't exist, yet")
        else:
            number_of_messages = len(messages)
            if number_of_messages:
                self.response.write('Number of messages sent: ' + str(number_of_messages))
            else:
                self.response.write('No message has been sent, yet')

class MessagesList(webapp2.RequestHandler):
    def get(self, RoomID = None, Username = None):
        if RoomID:
            try:
                message_list = []
                for OuterID, message in messages.iteritems():
                    if message["RoomID"] == str(RoomID):
                        message_list.append(message)
                if message_list:
                    self.response.write('List of messages of room: ' + str(RoomID))
                    self.response.write(message_list)
                else:
                    self.response.write('No message has been sent in this room, yet')
            except:
                self.response.write("Room doesn't exist, yet")
        elif Username:
            try:
                message_list = []
                for OuterID, message in messages.iteritems():
                    if message["from"] == str(Username):
                        message_list.append(message)
                if message_list:
                    self.response.write('List of messages of user: ' + str(Username))
                    self.response.write(message_list)
                else:
                    self.response.write('No message has been sent by this user, yet')
            except Exception as e:
                print e
                self.response.write("User doesn't exist, yet")
        else:
            if messages:
                self.response.write('List of messages: ')
                self.response.write(messages)
            else:
                self.response.write('No message has been sent, yet')

####################### Servers ########################

class Servers(webapp2.RequestHandler):
    def get(self, ServerID = None):
        try:
            data = database.servers.get(ServerID)
            self.response.write(json.dumps(data))
        except:
            self.response.write(json.dumps({}))

    def post(self, ServerID = None):
        try:
            data = json.loads(self.request.body)
            new_server = {}
            new_server["ServerID"] = data["ServerID"]
            new_server["host"] = data["host"]
            new_server["pub_port"] = data["pub_port"]
            new_server["pull_port"] = data["pull_port"]
            database.servers.insert(new_server)
            self.response.write('OK')
        except Exception as e:
            if DEBUG:
                print e
            self.response.write('FAIL')

    def delete(self, ServerID):
        try:
            servers.remove(ServerID)
            database.servers.remove(ServerID)
            self.response.write('OK')
        except:
            self.response.write('FAIL')


####################### Rooms ##########################

class Rooms(webapp2.RequestHandler):
    def get(self, RoomID = None):
        if RoomID:
            try:
                self.response.write(json.dumps(rooms[str(RoomID)]))
            except:
                self.response.write(json.dumps({}))
        else:
            if rooms:
                self.response.write(json.dumps(rooms))
            else:
                self.response.write(json.dumps({}))

    def post(self, RoomID = None):
        try:
            data = json.loads(self.request.body)
            RoomID = str(data["RoomID"])
            new_room = {}
            new_room["messages"] = []
            new_room["server"] = data["server"]
            rooms[RoomID] = new_room
            first_user = data["users"][0]
            first_user_name = first_user
            first_user = users[first_user]
            first_user["current_room"] = RoomID
            database.rooms.insert(room)
            database.users.update(first_user_name, first_user)
            self.response.write('OK')
        except Exception as e:
            if DEBUG:
                print e
            self.response.write('FAIL')

    def put(self, RoomID):
        try:
            data = json.loads(self.request.body)
            username = str(data["Username"])
            user = database.users.get(username)
            room = database.rooms.get(str(RoomID))
            command = str(data["command"])
            if command == "enter":
                user["current_room"] = str(RoomID)
                database.users.update(username, user)
                self.response.write('OK')
            elif command == "exit":
                user["current_room"] = None
                database.users.update(username, user)
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
            data = json.loads(self.request.body)
            username = str(data["username"])
            new_user = {}
            new_user["current_room"] = None
            new_user["status"] = "ON"
            users[username] = new_user
            database.users.insert(new_user)
            self.response.write('OK')
        except:
            self.response.write('FAIL')

    def put(self, UserName):
        try:
            user = users[UserName]
            data = json.loads(self.request.body)
            command = data["command"]
            if command == "login":
                user["status"] = "ON"
                self.response.write('OK')
            elif command == "logout":
                user["status"] = "OFF"
                self.response.write('OK')
            else:
                self.response.write('FAIL')
        except Exception as e:
            if DEBUG:
                print e
            self.response.write('FAIL')

################## Mensages #######################

class Messages(webapp2.RequestHandler):
    def post(self, RoomID, MessageID = None):
        try:
            data = json.loads(self.request.body)
            room = rooms[RoomID]
            room_messages = room["messages"]
            InnerID = len(room_messages)
            OuterID = len(messages)
            data["InnerID"] = InnerID
            data["OuterID"] = OuterID
            database.messages.insert(message)
            self.response.write('OK')
        except Exception as e:
            if DEBUG:
                print e
            self.response.write('FAIL')

app = webapp2.WSGIApplication([
    webapp2.Route(r'/', MainPage),

    webapp2.Route(r'/html/users/', UsersList),
    webapp2.Route(r'/html/users/count', UsersCount),
    webapp2.Route(r'/html/<RoomID:\w+>/users/count', UsersCount),
    webapp2.Route(r'/html/<RoomID:\w+>/users', UsersList),
    webapp2.Route(r'/html/messages', MessagesList),
    webapp2.Route(r'/html/messages/count', MessagesCount),
    webapp2.Route(r'/html/users/<Username:\w+>/messages', MessagesList),
    webapp2.Route(r'/html/users/<Username:\w+>/messages/count', MessagesCount),
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
