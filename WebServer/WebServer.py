import webapp2
from webapp2_extras import routes
import json

users    = {}
messages = {}
rooms    = {}
servers  = {}

class MainPage(webapp2.RequestHandler):
    def get(self):
        if rooms:
            s = '<h3>Please pick a Room:</h3>'
            for RoomID in rooms.keys():
                s += '<p>'
                s += '<h4>Room: ' + RoomID + ' </h4>'
                s += '<a href="html/' + RoomID + '/users/count">Number of users in room: ' + RoomID + ' </a> &nbsp '
                s += '<a href="html/' + RoomID + '/users">List of users in room: ' + RoomID + ' </a> &nbsp '
                s += '<a href="html/' + RoomID + '/messages/count">Number of messages in room: ' + RoomID + ' </a> &nbsp '
                s += '<a href="html/' + RoomID + '/messages">List of messages in room: ' + RoomID + ' </a> &nbsp '
                s += '</p>'
        else:
            s = '<h3>No Rooms Exist, Yet</h3>'
        self.response.write(s)

######################WebClient#####################

class UsersCount(webapp2.RequestHandler):
    def get(self, RoomID = None):
        if RoomID:
            users_in_room = 0
            for username, user in users.iteritems():
                if user["current_room"] == str(RoomID):
                    users_in_room += 1
            self.response.write('There are ' + str(users_in_room) + ' users in room: ' + str(RoomID))
        else:
            pass

class UsersList(webapp2.RequestHandler):
    def get(self, RoomID = None):
        if RoomID:
        	users_in_room = []
        	for username, user in users.iteritems():
        		if user["current_room"] == RoomID:
        			users_in_room.append(username)
        	self.response.write('Users in room ' + RoomID + ': ')
        	self.response.write(users_in_room)
        else:
            self.response.write('Active Users: ')
            self.response.write(users)

class MessagesCount(webapp2.RequestHandler):
    def get(self, RoomID):
    	room = rooms[RoomID]
    	number_of_messages = len(room["messages"])
        print
        if number_of_messages != 0:
            self.response.write('Number of messages sent: ' + str(number_of_messages))
        else:
            self.response.write('No message has been sent in this room, yet')

class MessagesList(webapp2.RequestHandler):
    def get(self, RoomID):
        room = rooms[RoomID]
        if room["messages"]:
            self.response.write('List of messages: ')
            self.response.write(room["messages"])
        else:
            self.response.write('No message has been sent in this room, yet')


#######################Salas##########################

class Rooms(webapp2.RequestHandler):

    def get(self, RoomID = None):
        self.response.write(json.dumps(rooms))

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
            print e
            self.response.write('FAIL')

    def put(self, RoomID = None):
        pass

#######################Servers########################

class Servers(webapp2.RequestHandler):
    def get(self, ServerID = None):
        if ServerID:
            self.response.write(json.dumps(servers[ServerID]))
        else:
            self.response.write(json.dumps(servers))

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
            print e
            self.response.write('FAIL')

#######################Users###########################

class Users(webapp2.RequestHandler):
    def get(self, UserName = None):
        if UserName:
            self.response.write(json.dumps(users[UserName]))
        else:
            self.response.write(json.dumps(users))

    def post(self, UserName = None):
        try:
            data = self.request.json
            username = data["username"]
            new_user = {}
            new_user["current_server"] = None
            new_user["current_room"]   = None
            new_user["active"]         = True
            users[username] = new_user

            self.response.write('OK')
        except:
            self.response.write('FAIL')

    def put(self, UserName = None):
        if not UserName:
            self.response.write('FAIL')
        else:
            try:
                user = users[UserName]
                data = self.request.json
                RoomID = data["RoomID"]
                if RoomID:
                    room = rooms[RoomID]
                    room["users"].append(UserName)

                    user["current_room"]   = data["RoomID"]
                    user["current_server"] = data["server"]
                else:
                    user["current_room"]   = None
                    user["current_server"] = None

                self.response.write('OK')
            except:
                self.response.write('FAIL')

##################Para as Mensagens#######################

class Messages(webapp2.RequestHandler):
    def get(self, MessageID = None):
        self.response.write(json.dumps(messages))

    def post(self, MessageID = None):
        try:
            data = self.request.json
            RoomID = data["RoomID"]
            room = rooms[RoomID]
            #inserir id da mensagem
            room["messages"].append(data["message"])

            self.response.write('OK')
        except:
            self.response.write('FAIL')

app = webapp2.WSGIApplication([
    webapp2.Route(r'/', MainPage),

    webapp2.Route(r'/html/users', UsersList),
    webapp2.Route(r'/html/users/count', UsersCount),
    webapp2.Route(r'/html/<RoomID>/users/count', UsersCount),
    webapp2.Route(r'/html/<RoomID>/users', UsersList),
    webapp2.Route(r'/html/<RoomID>/messages/count', MessagesCount),
    webapp2.Route(r'/html/<RoomID>/messages', MessagesList),

    webapp2.Route(r'/server/messages/<MessageID:w*>', Messages),

    webapp2.Route(r'/nameserver/users/<UserName:w*>', Users),
    webapp2.Route(r'/nameserver/rooms/<RoomID:w*>', Rooms),
    webapp2.Route(r'/nameserver/servers/<ServerID:w*>', Servers),

], debug=True)

def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='7000')

if __name__ == '__main__':
    main()
