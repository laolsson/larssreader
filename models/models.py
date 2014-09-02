from google.appengine.ext import db
	
class User(db.Model):
	name = db.StringProperty(required=False)
	id = db.StringProperty(required=False)	
	
class LFeed(db.Model):
	title = db.StringProperty(required=False)
	url = db.StringProperty(required=False)
	added_time = db.DateTimeProperty(auto_now=True, required=False)
	last_update = db.DateTimeProperty(required=False)
	last_successful_update = db.DateTimeProperty(required=False)
	failed_attempts = db.IntegerProperty(required=False)
	category = db.StringProperty(required=False)
	user = db.ReferenceProperty(User, collection_name='feeds')

class LFeedItem(db.Model): 
	title = db.StringProperty(required=False)
	summary = db.TextProperty(required=False)
	link = db.StringProperty(required=False)
	date = db.DateTimeProperty(required=False)
	read = db.BooleanProperty(required=False)
	feed = db.ReferenceProperty(LFeed, collection_name='items')
				
