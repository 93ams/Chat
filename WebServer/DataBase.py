#!/usr/bin/env python
from google.appengine.ext import ndb

DEBUG = True
REMOTE = False

if REMOTE:
	from google.appengine.api import urlfetch

class Server(ndb.Model):
	serverID = ndb.StringProperty(required = True)
	host = ndb.StringProperty()
	pub_port = ndb.IntegerProperty()
	pull_port = ndb.IntegerProperty()

class Room(ndb.Model):
	roomID = ndb.StringProperty(required = True)
	server = ndb.StringProperty()

class User(ndb.Model):
	username = ndb.StringProperty(required = True)
	current_room = ndb.StringProperty()
	status = ndb.StringProperty()

class Message(ndb.Model):
	innerID = ndb.IntegerProperty()
	outerID = ndb.IntegerProperty()
	text = ndb.StringProperty()
	room = ndb.StringProperty()
	from_user = ndb.StringProperty()

def parser(type, item = None):
	if item:
		parsed_item = {}
		try:
			if type == "server":
				parsed_item["ServerID"] = item.serverID
				parsed_item["host"] = item.host
				parsed_item["pub_port"] = item.pub_port
				parsed_item["pull_port"] = item.pull_port
			elif type == "room":
				parsed_item["RoomID"] = item.roomID
				parsed_item["server"] = item.server
			elif type == "user":
				parsed_item["Username"] = item.username
				parsed_item["Current_room"] = item.current_room
				parsed_item["status"] = item.status
			elif type == "message":
				parsed_item["InnerID"] = item.innerID
				parsed_item["OuterID"] = item.outerID
				parsed_item["Message"] = item.text
				parsed_item["RoomID"] =	item.room
				parsed_item["From"] = item.from_user
			else:
				return {}
			return parsed_item
		except Exception as e:
			if DEBUG:
				print e
	return {}


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
			if DEBUG:
				print e
			return {}

	def count(self):
		try:
			count = Server.query().count()
		except Exception as e:
			if DEBUG:
				print e
			count = -1
		return count

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

	def remove(self, ServerID = None):
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
	def get(self, RoomID = None, ServerID = None):
		if RoomID and ServerID:
			return {}
		try:
			if RoomID:
				room = Room.query(Room.roomID == RoomID).get()
				room = parser("room", room)
				return room
			elif ServerID:
				rooms = Room.query(Room.server == ServerID).fetch()
				room_list = []
				for room in rooms:
					room = parser("room", room)
					if room:
						room_list.append(room)
				return room_list
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

	def count(self, ServerID = None):
		count = -1
		try:
			if ServerID:
				count = Room.query(Room.server == ServerID).count()
			else:
				count = Room.query().count()
		except Exception as e:
			if DEBUG:
				print e
		return count

	def insert(self, room):
		try:
			new_room = Room(roomID = room.get("RoomID"), server = room.get("server"))
			new_room.put()
			return True
		except Exception as e:
			if DEBUG:
				print e
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

	def remove(self, RoomID = None):
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
	def get(self, Username = None, RoomID = None):
		try:
			if Username:
				user = User.query(User.username == Username).get()
				user = parser("user", user)
				return user
			elif RoomID:
				users = User.query(User.current_room == RoomID).fetch()
				user_list = []
				for user in users:
					user = parser("user", user)
					if user:
						user_list.append(user)
				return user_list
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

	def count(self, RoomID = None):
		count = -1
		try:
			if RoomID:
				count = User.query(User.current_room == RoomID).count()
				print "User count: " + str(count)
			else:
				count = User.query().count()
		except Exception as e:
			if DEBUG:
				print e
		return count

	def insert(self, user):
		try:
			new_user = User(username = user.get("username"), current_room = user.get("current_room"), status = user.get("status"))
			new_user.put()
			return True
		except Exception as e:
			if DEBUG:
				print e
			return False

	def update(self, Username, data):
		if Username:
			try:
				user = User.query(User.username == Username).get()
				if data.get("current_room"):
				    user.current_room = data.get("current_room")
				if data.get("status"):
				    user.status = data.get("status")
				user.put()
				return True
			except Exception as e:
				if DEBUG:
					print e
		return False

	def remove(self, Username = None):
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
	def get(self, RoomID = None, LowerLimit = -1, UpperLimit = -1, InnerID = None, OuterID = None, Username = None):
		try:
			if RoomID:
				if InnerID:
					message = Message.query(ndb.AND(Message.room == RoomID, Message.innerID == InnerID)).get()
					message = parser("message", message)
				else:
					if LowerLimit != -1:
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
						message = parser("message", message)
						if message:
							message_list.append(message)
					return message_list
			elif Username:
				messages = Message.query(Message.from_user == Username).order(Message.outerID).fetch()
				message_list = []
				for message in messages:
					message = parser("message", message)
					if message:
						message_list.append(message)
				return message_list
			elif OuterID:
				message = Message.query(Message.outerID == OuterID).get()
				message = parser("message", message)
				return message
			else:
				messages = Message.query().order(Message.outerID).fetch()
				print messages
				message_list = []
				for message in messages:
					message = parser("message", message)
					if message:
						message_list.append(message)
				return message_list
		except Exception as e:
			if DEBUG:
				print "MERDA"
				print e
			return {}

	def count(self, RoomID = None, Username = None):
		count = -1
		try:
			if RoomID:
				count = Message.query(Message.room == RoomID).count()
			elif Username:
				count = Message.query(Message.from_user == Username).count()
			else:
				count = Message.query().count()
		except Exception as e:
			if DEBUG:
				print e
		return count

	def insert(self, message):
		try:
			new_message = Message(outerID = message.get("OuterID"), innerID = message.get("InnerID"), text = message.get("message"), from_user = message.get("from"), room = message.get("RoomID"))
			new_message.put()
			print "should be chill"
			return True
		except Exception as e:
			if DEBUG:
				print e
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
				message = Message.query(Message.outerID == OuterID).get()
				if data.get("from"):
					message.from_user = data.get("from")
				if data.get("message"):
					message.from_user = data.get("message")
				return True
			else:
				pass
		except Exception as e:
			if DEBUG:
				print e
		return False

	def remove(self, RoomID = None, InnerID = None, OuterID = None):
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

	def reset(self):
		try:
			self.messages.remove()
			self.users.remove()
			self.rooms.remove()
			self.servers.remove()
		except Exception as e:
			if DEBUG:
				print e
