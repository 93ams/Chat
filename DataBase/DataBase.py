 #!/usr/bin/env python
from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class Server(ndb.Model):
	serverID=ndb.StringProperty()
	host=ndb.IntegerProperty()
	pub_port=ndb.IntegerProperty()
	post_port=ndb.IntegerProperty()

class Room(ndb.Model):
	roomId = ndb.StringProperty()
	serverID = ndb.StringProperty()

class User(ndb.Model):
	UserID = ndb.IntegerProperty()
	Current_room=ndb.IntegerProperty()
	Current_server=ndb.IntegerProperty()

class Message(ndb.Model):
	messageID = ndb.IntegerProperty()
	text = ndb.StringProperty()
	roomID = ndb.StringProperty()
	from_user = ndb.StringProperty()



#Servidor REST

class Servers(webapp2.RequestHandler):
	def get(self, ServerID = None):
		if ServerID:
			pass
		else:
			pass

	def post(self, ServerID = None):
		if ServerID:
			pass
		else:
			try:
	            data = self.request.json
			except:
				pass

	def put(self, ServerID):
		if ServerID:
			try:
	            data = self.request.json
			except:
				pass
		else:
			pass

	def delete(self, ServerID):
		if ServerID:
			pass
		else:
			pass

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
	            data = self.request.json
			except:
				pass

	def put(self, RoomID):
		if RoomID:
			try:
	            data = self.request.json
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
	            data = self.request.json
			except:
				pass

	def put(self, Username):
		if Username:
			try:
	            data = self.request.json
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
			data = self.request.json
		except:
			pass

	def put(self, RoomID = None, InnerID = None, OuterID = None):
		if RoomID:
			if InnerID:
				pass
		elif OuterID:
			pass
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

application = webapp2.WSGIApplication([
				(r'/servers/<ServerID:[\w-]*>', Servers),
				(r'/rooms/<RoomID:\w*>', Rooms),
				(r'/users/<ServerID:\w*>', Users),
				(r'/messages/<OuterID:\w*>', Messages),
				(r'/messages/<RoomID:\w+>/<InnerID:\w*>', Messages),
            ], debug = True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
