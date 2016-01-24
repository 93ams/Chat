#!/usr/bin/env python
from google.appengine.ext import ndb

DEBUG = True
REMOTE = False

if REMOTE:
	from google.appengine.api import urlfetch



class Server(ndb.Model):
	serverID = ndb.StringProperty()
	host = ndb.StringProperty()
	pub_port = ndb.IntegerProperty()
	pull_port = ndb.IntegerProperty()

class Room(ndb.Model):
	roomID = ndb.StringProperty()
	server = ndb.StringProperty()

class User(ndb.Model):
	username = ndb.StringProperty()
	current_room = ndb.StringProperty()

class Message(ndb.Model):
	innerID = ndb.IntegerProperty()
	outerID = ndb.IntegerProperty()
	text = ndb.StringProperty()
	room = ndb.StringProperty()
	from_user = ndb.StringProperty()

def parser(type, item):
	parsed_item = {}
	try:
		if type == "server":
			print item
			parsed_item["ServerID"] = item.serverID
			parsed_item["host"] = item.host
			parsed_item["pub_port"] = item.pub_port
			parsed_item["pull_port"] = item.pull_port
		elif type == "room":
			parsed_item["RoomID"] = item.roomID
			parsed_item["current_server"] = item.server
		elif type == "user":
			parsed_item["Username"] = item.username
			parsed_item["Current_room"] = item.current_room
			parsed_item["State"] = item.state
		elif type == "message":
			parsed_item["InnerID"] = item.innerID
			parsed_item["OuterID"] = item.outerID
			parsed_item["Message"] = item.text
			parsed_item["RoomID"] =	item.room
			parsed_item["From"] = item.from_user
		else:
			return {}
	except Exception as e:
		if DEBUG:
			print e
		return {}
	return parsed_item

class Servers():
    def get(self, ServerID = None):
		try:
			if ServerID:
				server = Server.query(Server.serverID == ServerID).get()
				server = parser("server", server)
				return server
			else:
				servers = Server.query().fetch()
				server_list = []
				for server in servers:
					server = parser("server", server)
					if server:
						server_list.append(server)
				return server_list
		except Exception as e:
			print e
			return {}

    def insert(self, server):
        try:
            new_server = Server(serverID = server.get("ServerID"), host = server.get("host"), pub_port = server.get("pub_port"), pull_port = server.get("pull_port"))
            new_server.put()
            return True
        except Exception as e:
			if DEBUG:
				print e
			return False

    def update(self, ServerID, data):
        try:
			server = Server.query(Server.serverID == ServerID).get()
			if data.get("host"):
			    server.host = data.get("host")
			if data.get("pub_port"):
			    server.pub_port = data.get("pub_port")
			if data.get("pull_port"):
			    server.pull_port = data.get("pull_port")
			server.put()
			return True
        except Exception as e:
			if DEBUG:
				print e
			return False

	def delete(self, ServerID = None):
		try:
			if ServerID:
				server = Server.query(Server.serverID == ServerID).get()
				server.key.delete()
			else:
				servers = Server.query().fetch()
				for server in servers:
					print server.key.delete()
			return True
		except Exception as e:
			if DEBUG:
				print e
			return False

class Rooms():
	def get(self, RoomID = None):
		try:
			if RoomID:
				room = Room.query(Room.roomID == RoomID).get()
				room = parser("room", room)
				return room
			else:
				rooms = Room.query().fetch()
				room_list = []
				for room in rooms:
					room = parser("room", room)
					if room:
						room_list.append(room)
				return room_list
		except Exception as e:
			if DEBUG:
				print e
			return {}

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
				room = Room(Room.roomID == RoomID).get()
				if data.get("server"):
				    room.server = data.get("server")
			except Exception as e:
				if DEBUG:
					print e
				pass
		return False

	def delete(self, RoomID):
		try:
			if RoomID:
			    room = Room.query(Room.roomID == RoomID).get()
			    room.key.delete()
			else:
				rooms = Room.query().fetch()
				for room in rooms:
					room.key.delete()
			return True
		except Exception as e:
			if DEBUG:
				print e
			return False

class Users():
	def get(self, Username = None):
		try:
			if Username:
				user = User.query(User.username == Username).get()
				user = parser(user)
				return user
			else:
				users = User.query().fetch()
				user_list = []
				for user in users:
					user = parser("user", user)
					if user:
						user_list.append(user)
				return user_list
		except Exception as e:
			if DEBUG:
				print e
			return {}

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
				user = User(User.username == Username).get()
				if data.get("current_room"):
				    user.current_room = data.get("current_room")
				if data.get("state"):
				    user.state = data.get("state")
				user.put()
				return True
			except Exception as e:
				if DEBUG:
					print e
				pass
		return False

	def delete(self, Username):
		try:
			if Username:
				user = User.query(User.UserID == Username).get()
				user.key.delete()
			else:
				users = User.query().fetch()
				for user in users:
					user.key.delete()
			return True
		except Exception as e:
			if DEBUG:
				print e
		return False

class Messages():
	def get(self, RoomID = None, LowerLimit = -1, UpperLimit = -1, InnerID = None, OuterID = None):
		try:
			if RoomID:
				if InnerID:
					message = Message.query(Message.roomID == RoomID, Message.innerID == InnerID).get()
					message = parser(message)
				else:
					if LoweLimit != -1:
						if UpperLimit != 1:
							messages = Message.query( ndb.AND( ndb.AND(Message.innerID > LowerLimit, Message.innerID < UpperLimit)), Message.room == RoomID ).order(Message.innerID).fetch()
						else:
							messages = Message.query(ndb.AND( Message.innerID > LowerLimit, Message.room == RoomID )).order(Message.innerID).fetch()
					else:
						if LowerLimit != -1:
							messages = Message.query(ndb.AND( Message.innerID < UpperLimit, Message.room == RoomID )).order(Message.innerID).fetch()
						else:
							messages = Message.query(Message.room == RoomID).order(Message.innerID).fetch()
					message_list = []
					for message in messages:
						message = parser(message)
						if message:
							message_list.append(message)
					return message_list
			elif OuterID:
				message = Message.query(Message.outerID == OuterID).get()
				message = parser(message)
				return message
			else:
				messages = Message.query().order(Message.outerID).fetch()
				message_list = []
				for message in messages:
					message = parser(message)
					if message:
						message_list.append(message)
				return message_list
		except:
			return {}

	def insert(self, message):
		try:
			new_message = Message(outerID = message.get("OuterID"), innerID = message.get("InnerID"), text = message.get("message"), from_user = message.get("from"))
			new_message.put()
			return True
		except:
			return False

	def update(self, data, RoomID = None, InnerID = None, OuterID = None):
		try:
			if RoomID:
				if InnerID:
					message = Message.query(ndb.AND(Message.room == RoomID, Message.innerID == InnerID)).get()
					if data.get("from"):
						message.from_user = data.get("from")
					if data.get("message"):
						message.from_user = data.get("text")
					return True
			elif OuterID:
				message = Room.query(Message.outerID == OuterID).get()
				if data.get("from"):
					message.from_user = data.get("from")
				if data.get("message"):
					message.from_user = data.get("message")
				return True
			else:
				pass
		except:
			pass
		return False

	def delete(self, RoomID = None, InnerID = None, OuterID = None):
		try:
			if RoomID:
				if InnerID:
					message = Message.query(ndb.AND(Message.room == RoomID, Message.innerID == InnerID)).get()
					message.key.delete()
				else:
					messages = Message.query(Message.room == RoomID).fetch()
					for message in messages:
						message.key.delete()
			elif OuterID:
				message = Message.query(Message.room == RoomID, Message.outerID == OuterID).get()
				message.key.delete()
			else:
				messages = Message.query().fetch()
				for message in messages:
					message.key.delete()
			return True
		except Exception as e:
			if DEBUG:
				print e
			return False

class DataBase(object):
	def __init__(self):
		self.servers = Servers()
		self.rooms = Rooms()
		self.users = Users()
		self.messages = Messages()
