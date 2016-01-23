#!/usr/bin/env python
from google.appengine.ext import ndb
DEBUG = True

class Server(ndb.Model):
	serverID = ndb.StringProperty()
	host = ndb.StringProperty()
	pub_port = ndb.IntegerProperty()
	pull_port = ndb.IntegerProperty()

class Room(ndb.Model):
	roomID = ndb.StringProperty()
	server = ndb.StringProperty()

class User(ndb.Model):
	userID = ndb.StringProperty()
	Current_room = ndb.StringProperty()
    state = ndb.StringProperty()

class Message(ndb.Model):
	innerID = ndb.IntegerProperty()
	outerID = ndb.IntegerProperty()
	text = ndb.TextProperty()
	room = ndb.StringProperty()
	from_user = ndb.StringProperty()

class Servers():
    def get(self, ServerID = None):
        if ServerID:
            server = Server.query(Server.serverID == ServerID)
            return server.content
        else:
            servers = Server.query()
            return servers.content

    def insert(self, server):
        try:
            new_server = Server(serverID = server.get("ServerID"), host = server.get("host"), pub_port = server.get("pub_port"), pull_port = server.get("pull_port"))
            new_server.put()
            return True
        except:
            return False

    def update(self, ServerID, data):
        if ServerID:
            server = Server.query(Server.serverID == ServerID)
            try:
                if data.get("host"):
                    server.host = data.get("host")
                if data.get("pub_port"):
                    server.pub_port = data.get("pub_port")
                if data.get("pull_port"):
                    server.pull_port = data.get("pull_port")
                server.put()
                return True
            except:
                return False
        else:
            return False

	def delete(self, ServerID):
        try:
    		if ServerID:
    			server = Server.query(Server.serverID == ServerID)
    		else:
    			servers = Server.query()
            return True
        except:
            return False

class Rooms():
	def get(self, RoomID = None):
        try:
    		if RoomID:
    			room = Rooms.query(Room.roomID == RoomID)
                return room.content
    		else:
    			rooms = Rooms.query()
                return rooms.content
        except:
            return None

	def insert(self, room):
		try:
            new_room = Room(roomID = room.get("RoomID"), server = room.get("server"))
            new_room.put()
            return True
		except:
		    return False

	def update(self, RoomID, data):
		if RoomID:
			try:
	            room = Room(Room.roomID == RoomID)
                if data.get("server"):
                    room.server = data.get("server")
			except:
				pass
        return False

	def delete(self, RoomID):
        try:
    		if RoomID:
                room = Room.query(Room.roomID == RoomID)
                delete room
    		else:
                rooms = Room.query()
                delete rooms
            return True
        except:
            return False

class Users():
	def get(self, Username = None):
		if Username:
			user = User.query(User.username == Username)
            return user.content
		else:
			users = User.query()
            return users.content
	def insert(self, user):
		try:
            new_user = User(username = user.get("username"), current_room = user.get("current_room"), state = user.get("state"))
            new_user.put()
            return True
		except:
			return False

	def update(self, Username, data):
		if Username:
			try:
                user = User(User.username == Username)
                if data.get("current_room"):
                    user.current_room = data.get("current_room")
                if data.get("state"):
                    user.current_room = data.get("state")
                user.put()
	            return True
			except:
				pass
        return False

	def delete(self, Username):
        try:
    		if Username:
    			pass
    		else:
    			pass
        except:
            pass
        return False

class Messages():
	def get(self, RoomID = None, LoweLimit = -1, UpperLimit = -1, InnerID = None, OuterID = None):
        try:
    		if RoomID:
    			if InnerID:
    				message = Message.query(Message.roomID == RoomID, Message.innerID == InnerID)
                    return message.content
                else:
                    if LoweLimit != -1:
                        if UpperLimit != 1:
                            messages = Message.query( ndb.AND(
                                                        ndb.OR(Message.innerID > LowerLimit, Message.innerID < UpperLimit)),
                                                        Message.room == RoomID
                                                    ).order(Message.innerID)
                        else:
                            messages = Message.query(ndb.AND(
                                                        Message.innerID > LowerLimit,
                                                        Message.room == RoomID
                                                    ).order(Message.innerID)
                    else:
                        if LowerLimit != -1:
                            messages = Message.query(ndb.AND(
                                                        Message.innerID < UpperLimit,
                                                        Message.room == RoomID
                                                    ).order(Message.innerID)
                        else:
                            messages = Message.query(Message.room == RoomID).order(Message.innerID)
                    return messages.content
    		elif OuterID:
    			message = Message.query(Message.outerID == OuterID)
                return message.content
    		else:
    			messages = Message.query().order(Message.outerID)
                return messages.content
            except:
                return None

	def insert(self, message):
		try:
			new_message = Message(outerID = message.get("OuterID"), innerID = message.get("InnerID"), text = message.get("message"), from_user = message.get("from"))
            new_message.put()
            return True
		except:
			return False

	def update(self, RoomID = None, InnerID = None, OuterID = None, data):
        try:
    		if RoomID:
    			if InnerID:
                    message = Message.query(ndb.AND(Message.room == RoomID, Message.innerID == InnerID)
                    if data.get("from"):
                        message.from_user = data.get("from")
                    if data.get("message"):
                        message.from_user = data.get("text")
                    return True
    		elif OuterID:
                message = Room.query(Message.outerID == OuterID)
                if data.get("from"):
                    message.from_user = data.get("from")
                if data.get("message"):
                    message.from_user = data.get("text")
                return True
    		else:
    			pass
        except:
            pass
        return False

	def delete(self, RoomID = None, InnerID = None, OuterID = None):
		if RoomID:
			if InnerID:
				pass
		elif OuterID:
			pass
		else:
			pass

 class DataBase(object):
     def __init__(self):
         self.servers = Servers()
         self.rooms = Rooms()
         self.users = Users()
         self.messages = Messages()
