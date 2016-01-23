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
	roomId = ndb.StringProperty()
	serverID = ndb.StringProperty()

class User(ndb.Model):
	UserID = ndb.IntegerProperty()
	Current_room=ndb.IntegerProperty()
	Current_server=ndb.IntegerProperty()

class Message(ndb.Model):
	innerID = ndb.IntegerProperty()
	outerID = ndb.IntegerProperty()
	text = ndb.StringProperty()
	roomID = ndb.StringProperty()
	from_user = ndb.StringProperty()

#Servidor REST

class Servers(webapp2.RequestHandler):
	def get(self, ServerID = None):
		try:
			if ServerID:
				server = Server.query(Server.serverID == ServerID)
				self.response.write(server.content)
			else:
				servers = Server.query()
				for server in servers:
					print server
				self.response.write(servers.content)
		except:
			self.response.write({})
	def post(self):
		try:
			server = json.loads(self.request.body)
			print server
			new_server = Server(serverID = server.get("ServerID"), host = server.get("host"), pub_port = server.get("pub_port"), pull_port = server.get("pull_port"))
			print new_server
			new_server.put()
			self.response.write("OK")
		except Exception as e:
			if DEBUG:
				print e
			self.response.write("FAIL")

	def put(self, ServerID):
		if ServerID:
			server = Server.query(Server.serverID == ServerID)
			try:
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
				server = Server.query(Server.serverID == ServerID)
				print server
				print server.fetch
			else:
				ndb.delete_multi(
				    Server.query().fetch()
				)
			self.response.write("OK")
		except Exception as e:
			if DEBUG:
				print e
			self.response.write("FAIL")

class Rooms(webapp2.RequestHandler):
	def get(self, RoomID = None):
		if RoomID:
			pass
		else:
			pass

	def post(self, RoomID = None):
		if RoomID:
			pass
		else:
			try:
				room = json.loads(self.request.body)
			except:
				pass

	def put(self, RoomID):
		if RoomID:
			try:
				data = json.loads(self.request.body)
			except:
				pass
		else:
			pass

	def delete(self, RoomID):
		if RoomID:
			pass
		else:
			pass


class Users(webapp2.RequestHandler):
	def get(self, Username = None):
		if Username:
			pass
		else:
			pass

	def post(self, Username = None):
		if Username:
			pass
		else:
			try:
				user = json.loads(self.request.body)
			except:
				pass

	def put(self, Username):
		if Username:
			try:
				data = json.loads(self.request.body)
			except:
				pass
		else:
			pass

	def delete(self, Username):
		if Username:
			pass
		else:
			pass

class Messages(webapp2.RequestHandler):
	def get(self, RoomID = None, InnerID = None, OuterID = None):
		if RoomID:
			if InnerID:
				pass
		elif OuterID:
			pass
		else:
			pass

	def post(self, RoomID = None, InnerID = None, OuterID = None):
		try:
			message = json.loads(self.request.body)
		except:
			pass

	def put(self, RoomID = None, InnerID = None, OuterID = None):
		if RoomID:
			if InnerID:
				data = json.loads(self.request.body)
		elif OuterID:
			data = json.loads(self.request.body)
		else:
			pass

	def delete(self, RoomID  = None, InnerID = None, OuterID = None):
		if RoomID:
			if InnerID:
				pass
		elif OuterID:
			pass
		else:
			pass

app = webapp2.WSGIApplication([
				(r'/servers', Servers),
				(r'/servers/<ServerID:[\w-]*>', Servers),
				(r'/rooms/<RoomID:\w*>', Rooms),
				(r'/users/<ServerID:\w*>', Users),
				(r'/messages/<OuterID:\w*>', Messages),
				(r'/messages/<RoomID:\w+>/<InnerID:\w*>', Messages),
            ], debug = True)

def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='7000')

if __name__ == "__main__":
    main()
