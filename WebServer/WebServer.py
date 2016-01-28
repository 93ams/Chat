 #!/usr/bin/env python

import json
import webapp2
from webapp2_extras import routes
from DataBase import DataBase

DEBUG = True

#################### WebAppServer ####################

database = DataBase()

#database.reset()

class MainPage(webapp2.RequestHandler):
    def get(self):

        s = ""
        s += '<h4>Messages:  </h4>'
        s += '<p>'
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
                    s += '<a href="html/users/' + user["Username"] + '/messages/count">Number of messages </a> &nbsp '
                    s += '<a href="html/users/' + user["Username"] +'/messages">List of messages </a> &nbsp '
                    s += '</p>'
            else:
                s += '<h3>No User exists, Yet</h3>'
        except Exception as e:
            if DEBUG:
                print e
            pass

        try:
            rooms = database.rooms.get()
            if rooms:
                s += '<h3>Rooms:</h3>'
                for room in rooms:
                    s += '<p>'
                    s += '<h4>Room: ' + room["RoomID"] + ' </h4>'
                    s += '<a href="html/rooms/' + room["RoomID"] + '/users/count">Number of users </a> &nbsp '
                    s += '<a href="html/rooms/' + room["RoomID"] + '/users">List of users </a> &nbsp '
                    s += '<a href="html/rooms/' + room["RoomID"] + '/messages/count">Number of messages </a> &nbsp '
                    s += '<a href="html/rooms/' + room["RoomID"] + '/messages">List of messages </a> &nbsp '
                    s += '</p>'
            else:
                s += '<h3>No Room exists, Yet</h3>'
        except Exception as e:
            if DEBUG:
                print e

        self.response.write(s)

###################### WebClient #####################

class UsersCount(webapp2.RequestHandler):
    def get(self, RoomID = None):
        if RoomID:
            users_in_room = database.users.count(RoomID = RoomID)
            if users_in_room:
                self.response.write('<p>There are ' + str(users_in_room) + ' users in room: ' + str(RoomID) + '</p>')
            else:
                self.response.write('<p>There is no user in this room, yet</p>')
        else:
            number_of_users = database.users.count()
            if number_of_users:
                self.response.write('<p>There are ' + str(number_of_users) + ' connected</p>')
            else:
                self.response.write('<p>There are no users, yet</p>')

class UsersList(webapp2.RequestHandler):
    def get(self, RoomID = None):
        s = ''
        if RoomID:
            users = database.users.get(RoomID = RoomID)
            if users:
                s += '<h3>Users in room ' + str(RoomID) + '</h3>'
                for user in users:
                    s += '<h4>' + str(user["Username"])+'</h4>'
            else:
                s += '<p>There is no user in this room, yet</p>'
        else:
            users = database.users.get()
            if users:
                s += '<h3>Active Users</h3>'
                for user in users:
        			s += '<h4>' + str(user["Username"]) + '</h4>'
            else:
                s += '<p>There is no user connected, yet</p>'
        self.response.write(s)

class MessagesCount(webapp2.RequestHandler):
    def get(self, RoomID = None, Username = None):
        if RoomID:
            try:
                number_of_messages = database.messages.count(RoomID = RoomID)
                if number_of_messages:
                    self.response.write('<p>Number of messages sent: ' + str(number_of_messages) + '</p>')
                else:
                    self.response.write('<p>No message has been sent in this room, yet</p>')
            except Exception as e:
                if DEBUG:
                    print e
                self.response.write("<p>This group doesn't exists, yet</p>")
        elif Username:
            try:
                number_of_messages = database.messages.count(Username = Username)
                if number_of_messages:
                    self.response.write('<p>Number of messages sent: ' + str(number_of_messages)+'</p>')
                else:
                    self.response.write('<p>No message has been sent by this user, yet</p>')
            except Exception as e:
                print e
                self.response.write("</p>User doesn't exists, yet</p>")
        else:
            number_of_messages = database.messages.count()
            if number_of_messages:
                self.response.write('<p>Number of messages sent: ' + str(number_of_messages) + '</p>')
            else:
                self.response.write('<p>No message has been sent, yet</p>')

class MessagesList(webapp2.RequestHandler):
    def get(self, RoomID = None, Username = None):
        s = ''
        if RoomID:
            try:
                message_list = database.messages.count(RoomID = RoomID)
                if message_list:
                    s += '<h3>List of messages of room: ' + str(RoomID) + '</h3>'
                    s += '<form action=/html/rooms/' + RoomID + '/listmessages method="get">'
                    s += '<h4>List of Messages between given indexes</h4>'
                    s += '<p>Start Index '
                    s += '<select name = "begin_index">'
                    for begin in range(1, message_list+1):
                        s +='<option value="%s">%s</option>' %( begin, begin)

                    s +='</select></p>'
                    s += '<p>End Index '
                    s += '<select name="end_index">'

                    for end in range(1, message_list+1):
                        s +='<option value="%s">%s</option>' %(end, end)

                    s += '</select></p>'
                    s += '<p><input type= "submit" name="Submit" value="submit"/></p>'
                    s += '<hr/>'
                else:
                    s += '<p>No message has been sent in this room, yet</p>'
            except Exception as e:
                if DEBUG:
                    print e
                s += "<p>Room doesn't exist, yet</p>"
        elif Username:
            try:
                message_list = database.messages.count(Username = Username)
                if message_list != 0:
                    s += '<h3>List of messages of user: ' + str(Username) + '</h3>'
                    s += '<form action=/html/users/' + Username + '/listmessages method="get">'
                    s += '<h4>List of Messages between given indexes</h4>'
                    s += '<p>Start Index '
                    s += '<select name="begin_index">'
                    for begin in range(1, message_list+1):
                        s +='<option value="%s">%s</option>' %( begin, begin)

                    s +='</select></p>'
                    s += '<p>End Index '
                    s += '<select name="end_index">'

                    for end in range(1, message_list+1):
                        s +='<option value="%s">%s</option>' %(end, end)

                    s += '</select></p>'
                    s += '<p><input type= "submit" name="Submit" value="submit"/></p>'
                    s += '<hr/>'
                else:
                    s += '<p>No message has been sent by this user, yet</p>'
            except Exception as e:
                if DEBUG:
                    print e
                s += "<p>User doesn't exist, yet</p>"
        else:
            message_list = database.messages.count()
            if message_list:
                s += '<form action=/html/listmessages method="get">'
                s += '<h4>List of Messages between given indexes</h4>'
                s += '<p>Start Index '
                s += '<select name="begin_index">'
                for begin in range(1, message_list+1):
                    s +='<option value="%s">%s</option>' %( begin, begin)

                s += '</select></p>'
                s += '<p>End Index '
                s += '<select name="end_index">'

                for end in range(1, message_list+1):
                    s += '<option value="%s">%s</option>' %(end, end)

                s += '</select></p>'
                s += '<p><input type= "submit" name="Submit" value="submit"/></p>'
                s += '<hr/>'
            else:
                s += '<p>No message has been sent, yet</p>'
        self.response.write(s)

class MessageListHandler(webapp2.RequestHandler):
    def get(self, RoomID = None, Username = None):
        s = ''
        if RoomID:
            message_list = database.messages.get(RoomID = RoomID)
            if message_list:
                s += '<h4> Room %s </h4>' %(RoomID)
            else:
                s += '<p>No message was sent in this room, yet</p>'
        elif Username:
            message_list = database.messages.get(Username = Username)
            if message_list:
                s += '<h4> User %s </h4>' %(Username)
            else:
                s += '<p>No message was sent by this user, yet</p>'
        else:
            message_list = database.messages.get()
            if message_list:
                s += '<h4> Messages </h4>'
            else:
                s += '<p>No message was sent, yet</p>'

        if message_list:
    		begin_index = self.request.GET["begin_index"]
    		end_index = self.request.GET["end_index"]
    		begin = int(begin_index)
    		end = int(end_index)
    		messages = message_list[(begin-1):end]

    		s += '<h5>List of messages between indexes %s and %s</h5>' %(begin_index, end_index)
    		for message in messages:
    			s+='<p>' + message["Message"] + ' by:' + message["From"] + '</p>'

		self.response.write(s)



####################### Servers ########################

class Servers(webapp2.RequestHandler):
    def get(self, ServerID = None):
        try:
            data = database.servers.get(ServerID)
            self.response.write(json.dumps(data))
        except Exception as e:
            if DEBUG:
                print "GET Server"
                print e
            self.response.write(json.dumps({}))

    def post(self, ServerID = None):
        try:
            data = json.loads(self.request.body)
            new_server = {}
            new_server["ServerID"] = data["ServerID"]
            new_server["host"] = data["host"]
            new_server["pub_port"] = data["pub_port"]
            new_server["pull_port"] = data["pull_port"]
            if database.servers.insert(new_server):
                self.response.write('OK')
            else:
                self.response.write('FAIL')
        except Exception as e:
            if DEBUG:
                print "POST Server"
                print e
            self.response.write('FAIL')

    def delete(self, ServerID):
        try:
            rooms = database.rooms.get(ServerID = str(ServerID))
            database.servers.remove(str(ServerID))
            for room in rooms:
                new_server = database.servers.get_best()
                if new_server:
                    data = {"server": new_server["ServerID"]}
                else:
                    data = {"server": None}
                if not database.rooms.update(room["RoomID"], data):
                    raise

            self.response.write('OK')
        except Exception as e:
            if DEBUG:
                print "Delete Server"
                print e
            self.response.write('FAIL')

class BestServer(webapp2.RequestHandler):
    def get(self):
        try:
            best_server = database.servers.get_best()
            if best_server:
                self.response.write(json.dumps(best_server))
            else:
                self.response.write(json.dumps({}))
        except Exception as e:
            if DEBUG:
                print "Best server"
            	print e
            self.response.write(json.dumps({}))

####################### Rooms ##########################

class Rooms(webapp2.RequestHandler):
    def get(self, RoomID = None, ServerID = None):
        try:
            if RoomID:
                room = database.rooms.get(RoomID = RoomID)
                self.response.write(json.dumps(room))
            elif ServerID:
                room = database.rooms.get(ServerID = ServerID)
                self.response.write(json.dumps(room))
            else:
                rooms = database.rooms.get()
                self.response.write(json.dumps(rooms))
        except Exception as e:
            if DEBUG:
                print "GET Rooms"
                print e
            self.response.write(json.dumps({}))

    def post(self, RoomID = None):
        try:
            data = json.loads(self.request.body)
            RoomID = str(data["RoomID"])
            new_room = {}
            new_room["RoomID"] = RoomID
            new_room["server"] = data["server"]
            database.rooms.insert(new_room)
            self.response.write('OK')
        except Exception as e:
            if DEBUG:
                print e
            self.response.write('FAIL')

    def put(self, RoomID):
        try:
            data = json.loads(self.request.body)
            room = database.rooms.get(str(RoomID))
            data = {"server": data.get("server")}
            if database.rooms.update(RoomID, data):
                self.response.write('OK')
            else:
                self.response.write('FAIL')
        except Exception as e:
            if DEBUG:
                print "PUT Rooms"
                print e
            self.response.write('FAIL')

####################### Users ###########################

class Users(webapp2.RequestHandler):
    def get(self, UserName = None):
        try:
            if UserName:
                user = database.users.get(Username = UserName)
                self.response.write(json.dumps(user))
            else:
                users = database.users.get()
                self.response.write(json.dumps(users))
        except Exception as e:
            if DEBUG:
                print "GET Users"
                print e
            self.response.write(json.dumps({}))

    def post(self, UserName = None):
        try:
            data = json.loads(self.request.body)
            username = str(data["username"])
            new_user = {}
            new_user["username"] = username
            new_user["current_room"] = None
            new_user["status"] = "ON"
            if database.users.insert(new_user):
                self.response.write('OK')
            else:
                self.response.write('FAIL')
        except Exception as e:
            if DEBUG:
                print "POST Users"
                print e
            self.response.write('FAIL')

    def put(self, UserName):
        try:
            data = json.loads(self.request.body)
            command = data["command"]
            if command == "login":
                data = {"status": "ON"}
                if database.users.update(UserName, data):
                    self.response.write('OK')
                else:
                    self.response.write('FAIL')
            elif command == "logout":
                data = {"status": "OFF"}
                if database.users.update(UserName, data):
                    self.response.write('OK')
                else:
                    self.response.write('FAIL')
            elif command == "enter":
                RoomID = data["RoomID"]
                data = {"current_room": RoomID}
                if database.users.update(UserName, data):
                    self.response.write('OK')
                else:
                    self.response.write('FAIL')
            elif command == "exit":
                data = {"current_room": None}
                if database.users.update(UserName, data):
                    self.response.write('OK')
                else:
                    self.response.write('FAIL')
        except Exception as e:
            if DEBUG:
                print "PUT Users"
                print e
            self.response.write('FAIL')

################## Mensages #######################

class Messages(webapp2.RequestHandler):
    def get(self):
        try:
            messages = database.messages.get()
            self.response.write(messages)
        except Exception as e:
            if DEBUG:
                print "GET Message"
                print e
            self.response.write([])

    def post(self):
        try:
            new_message = {}
            data = json.loads(self.request.body)
            new_message["from"] = data["from"]
            new_message["message"] = data["message"]
            RoomID = data["RoomID"]
            new_message["RoomID"] = RoomID
            InnerID = database.messages.count(RoomID = RoomID)
            OuterID =  database.messages.count()
            new_message["InnerID"] = InnerID
            new_message["OuterID"] = OuterID
            if database.messages.insert(new_message):
                self.response.write('OK')
            else:
                self.response.write('FAIL')
        except Exception as e:
            if DEBUG:
                print "POST Messages"
                print e
            self.response.write('FAIL')

app = webapp2.WSGIApplication([
    webapp2.Route(r'/', MainPage),

    webapp2.Route(r'/html/users/', UsersList),
    webapp2.Route(r'/html/users/count', UsersCount),
    webapp2.Route(r'/html/messages', MessagesList),
    webapp2.Route(r'/html/listmessages', MessageListHandler),
    webapp2.Route(r'/html/messages/count', MessagesCount),

    webapp2.Route(r'/html/rooms/<RoomID:\w+>/users', UsersList),
    webapp2.Route(r'/html/rooms/<RoomID:\w+>/users/count', UsersCount),
    webapp2.Route(r'/html/rooms/<RoomID:\w+>/messages', MessagesList),
    webapp2.Route(r'/html/rooms/<RoomID:\w+>/listmessages',MessageListHandler),
    webapp2.Route(r'/html/rooms/<RoomID:\w+>/messages/count', MessagesCount),

    webapp2.Route(r'/html/users/<Username:\w+>/messages', MessagesList),
    webapp2.Route(r'/html/users/<Username:\w+>/listmessages',MessageListHandler),
    webapp2.Route(r'/html/users/<Username:\w+>/messages/count', MessagesCount),

    webapp2.Route(r'/nameserver/servers/<ServerID:[\w-]*>', Servers),
    webapp2.Route(r'/nameserver/servers/<ServerID:[\w-]+>/rooms', Rooms),
    webapp2.Route(r'/nameserver/bestserver', BestServer),
    webapp2.Route(r'/nameserver/rooms/<RoomID:\w*>', Rooms),
    webapp2.Route(r'/nameserver/users/<UserName:\w*>', Users),

    webapp2.Route(r'/server/messages', Messages),

], debug=True)

def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='7000')

if __name__ == '__main__':
    main()
