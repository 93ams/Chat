 #!/usr/bin/env python
from google.appengine.ext import ndb
import webapp2, json

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
	username = ndb.StringProperty()
	current_room = ndb.StringProperty()
	state = ndb.StringProperty()

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
		print e
		return {}
	return parsed_item

#Servidor REST

class Servers(webapp2.RequestHandler):
	def get(self, ServerID = None):
		try:
			if ServerID:
				server = Server.query(Server.serverID == ServerID).get()
				server = parser("server", server)
				self.response.write(server)
			else:
				servers = Server.query().fetch()
				server_list = []
				for server in servers:
					server = parser("server", server)
					if server:
						server_list.append(server)
				self.response.write(server_list)
		except Exception as e:
			print e
			self.response.write({})

	def post(self, ServerID = None):
		if ServerID:
			self.response.write("FAIL")
		else:
			try:
				server = json.loads(self.request.body)
				new_server = Server(serverID = server.get("ServerID"), host = server.get("host"), pub_port = server.get("pub_port"), pull_port = server.get("pull_port"))
				new_server.put()
				self.response.write("OK")
			except Exception as e:
				if DEBUG:
					print e
				self.response.write("FAIL")

	def put(self, ServerID = None):
		if ServerID:
			try:
				server = Server.query(Server.serverID == ServerID).get()
				data = json.loads(self.request.body)
				if data.get("host"):
					server.host = data.get("host")
				if data.get("pub_port"):
					server.pub_port = data.get("pub_port")
				if data.get("pull_port"):
					server.pull_port = data.get("pull_port")
				server.put()
				self.response.write("OK")
			except:
				self.response.write("FAIL")
		else:
			self.response.write("FAIL")

	def delete(self, ServerID = None):
		try:
			if ServerID:
				server = Server.query(Server.serverID == ServerID).get()
				server.key.delete()
			else:
				servers = Server.query().fetch()
				for server in servers:
					print server.key.delete()
			self.response.write("OK")
		except Exception as e:
			if DEBUG:
				print e
			self.response.write("FAIL")

class Rooms(webapp2.RequestHandler):
	def get(self, RoomID = None):
		if RoomID:
			room = Room.query(Room.roomID == RoomID).get()
			room = parser("room", room)
			self.response.write(room)
		else:
			rooms = Room.query().fetch()
			room_list = []
			for room in rooms:
				room = parser("room", room)
				if room:
					room_list.append(room)
			self.response.write(room_list)

	def post(self, RoomID = None):
		try:
			room = json.loads(self.request.body)
			new_room = Room(roomID= room.get("RoomID"), server = room.get("ServerID"))
			new_room.put()
			self.response.write("OK")
		except Exception as e:
			if DEBUG:
				print e
			self.response.write("FAIL")


	def put(self, RoomID = None):
		if RoomID:
			room = Room.query(Room.roomID == RoomID).get()
			try:
				data = json.loads(self.request.body)
				if data.get("ServerID"):
					room.server = data.get("ServerID")
				room.put()
				self.response.write("OK")
			except:
				self.response.write("FAIL")
		else:
			self.response.write("FAIL")

	def delete(self, RoomID = None):
		try:
			if RoomID:
				room = Room.query(Room.roomID == RoomID).get()
				room.key.delete()
			else:
				rooms = Room.query().fetch()
				for room in rooms:
					room.key.delete()
			self.response.write("OK")
		except Exception as e:
			if DEBUG:
				print e
			self.response.write("FAIL")


class Users(webapp2.RequestHandler):
	def get(self, Username = None):
		if Username:
			user = User.query(User.username == Username).get()
			user = parser("user", user)
			self.response.write(user)
		else:
			user_list = []
			users = User.query().fetch()
			for user in users:
				user = parser("user", user)
				if user:
					user_list.append(user)
			self.response.write(user_list)

	def post(self, Username = None):
		try:
			user = json.loads(self.request.body)
			new_user = User(username = user.get("Username"), current_room = user.get("Current_room"), state = user.get("State"))
			new_user.put()
			self.response.write("OK")
		except Exception as e:
			if DEBUG:
				print e
			self.response.write("FAIL")

	def put(self, Username = None):
		if Username:
			try:
				user = User.query(User.username == Username).get()
				data = json.loads(self.request.body)
				if data.get("Current_room"):
					user.current_room = data.get("Current_room")
				if data.get("State"):
					user.current_room = data.get("State")
				user.put()
				self.response.write("OK")
			except Exception as e:
				if DEBUG:
					print e
				self.response.write("FAIL")
		else:
			self.response.write("FAIL")

	def delete(self, Username = None):
		try:
			if Username:
				user = User.query(User.UserID == Username).get()
				user.key.delete()
			else:
				users = User.query().fetch()
				for user in users:
					user.key.delete()
			self.response.write("OK")
		except Exception as e:
			if DEBUG:
				print e
			self.response.write("FAIL")

class Messages(webapp2.RequestHandler):
	def get(self, RoomID = None, InnerID = None, OuterID = None):
		try:
			if RoomID:
				if InnerID:
					message = Message.query(ndb.AND(Message.room == RoomID, Message.innerID == InnerID)).get()
					message = parser("message", message)
					self.response.write(message)
				else:
					messages = Message.query(Message.room == RoomID).fetch()
					message_list = []
					for message in messages:
						message = parser("message", message)
						if message:
							message_list.append(message)
					self.response.write(message_list)
			elif OuterID:
				message = Message.query(Message.outerID == OuterID).get()
				message = parser("message", message)
				self.response.write(message)
			else:
				Message = Message.query().fetch()
				message_list = []
				for message in messages:
					message = parser("message", message)
					if message:
						message_list.append(message)
				self.response.write(message_list)
		except Exception as e:
			if DEBUG:
				print e
			self.response.write({})

	def post(self, RoomID = None, InnerID = None, OuterID = None):
		try:
			message = json.loads(self.request.body)
			new_message = Message(innerID = message.get("InnerID"), outerID = message.get("OuterID"), roomID = message.get("RoomID"), from_user= message.get("From"), text=message.get("Text"))
			new_message.put()
			self.response.write("OK")
		except Exception as e:
			if DEBUG:
				print e
			self.response.write("FAIL")

	def put(self, RoomID = None, InnerID = None, OuterID = None):
		try:
			if RoomID:
				if InnerID:
					message = Message.query(ndb.AND(Message.room == RoomID, Message.innerID == InnerID)).get()
					data = json.loads(self.request.body)
					if data.get("innerID"):
						message.innerId = data.get("innerID")
					if data.get("roomID"):
						message.roomID = data.get("roomID")
					if data.get("text"):
						message.text = data.get("text")
					if data.get("from_user"):
						message.from_user = data.get("from_user")
					self.response.write("OK")
				else:
					self.response.write("FAIL")
			elif OuterID:
				message = Message.query(Message.outerID == OuterID).get()
				data = json.loads(self.request.body)
				if data.get("innerID"):
					message.innerId = data.get("innerID")
				if data.get("roomID"):
					message.roomID = data.get("roomID")
				if data.get("text"):
					message.text = data.get("text")
				if data.get("from_user"):
					message.from_user = data.get("from_user")
				self.response.write("OK")
			else:
				self.response.write("FAIL")
		except Exception as e:
			if DEBUG:
				print e
			self.response.write("FAIL")


	def delete(self, RoomID  = None, InnerID = None, OuterID = None):
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
			self.response.write("OK")
		except Exception as e:
			if DEBUG:
				print e
			self.response.write("FAIL")

app = webapp2.WSGIApplication([
				webapp2.Route(r'/servers/<ServerID>', Servers),
				webapp2.Route(r'/servers', Servers),

				webapp2.Route(r'/rooms/<RoomID:\w+>', Rooms),
				webapp2.Route(r'/rooms', Rooms),

				webapp2.Route(r'/users/<Username:\w+>', Users),
				webapp2.Route(r'/users', Users),

				webapp2.Route(r'/messages/<RoomID:\w+>/<InnerID:\w+>', Messages),
				webapp2.Route(r'/messages/<RoomID:\w+>', Messages),
				webapp2.Route(r'/messages/<OuterID:\w+>', Messages),
				webapp2.Route(r'/messages', Messages),
            ], debug = True)

def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='7000')

if __name__ == "__main__":
    main()
