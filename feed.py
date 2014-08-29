from google.appengine.ext import db

# Each user has a list of UFeeds. 
# Each UFeed has a list of UItems.

# A UFeed has a pointer to a real feed and each UItem a pointer to a real item

# To display all feed and items for a user:
	# for all f in UFeeds:
		# print UFeed id
		# for all items in f:
			# create a UItem unless it already exists
			# print item based on UItem has been read or not
			# print UItem id
			
# To read item:
	# find UItem:
		# find real item
		# change UItem to read = True
		# redirect
		
# To update feed:
	# get real feed from UFeed id and update
	
# To delete feed
	# delete UFeed
	# if no other user has Feed delete feed
		
# To add feed:
	# check if Feed already exists, if not create
	# create UFeed and add to user

	
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
	user = db.ReferenceProperty(User, collection_name='feeds')

class LFeedItem(db.Model): 
	title = db.StringProperty(required=False)
	summary = db.TextProperty(required=False)
	link = db.StringProperty(required=False)
	date = db.DateTimeProperty(required=False)
	read = db.BooleanProperty(required=False)
	feed = db.ReferenceProperty(LFeed, collection_name='items')
				
