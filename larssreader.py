import cgi
import datetime
import json
import logging
import os
import time
from time import mktime
from datetime import timedelta
import traceback
import xml.etree.ElementTree as ET

# app engine
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp import template
import webapp2

# local libraries
import feedparser

# local files
from models.models import LFeed
from models.models import User
from models.models import LFeedItem

HTML_HEADER = """\
<!DOCTYPE html>
<html>
<head>
<style>
table,th,td
{
border:1px solid black;
border-collapse:collapse;
}
th,td
{
padding:5px;
}
th
{
text-align:left;
}
tr:nth-child(even) {
    background-color: #999999;
}
</style>
</head>
<body>
<script language="javascript"> 
function toggle(elem) {
	var ele = document.getElementById(elem);
	var text = document.getElementById("displayText");
	if(ele.style.display == "block") {
    		ele.style.display = "none";
		text.innerHTML = "show";
  	}
	else {
		ele.style.display = "block";
		text.innerHTML = "hide";
	}
} 
</script>
"""

ADD_FEED_HTML = """\
    <form action="/add_feed" method="post">
      <div><input type="text" name="feed"></div>
      <div><input type="submit" value="Add Feed"></div>
    </form>
"""

UPLOAD_OPML_HTML = """\
    <form action="/upload_opml" method="post" enctype='multipart/form-data' action='process'>
      <div><input type="file" name="opml_file"></div>
      <div><input type="submit" value="Upload OPML"></div>
    </form>
"""

# html header and top of page
def header(fn):
	def wrapper(self):
		user = users.get_current_user()
		
		#self.response.out.write(HTML_HEADER)
		#self.response.out.write('Welcome, %s! (<a href="%s">sign out</a>)' % (user.nickname(), users.create_logout_url('/')))
		#self.response.out.write(ADD_FEED_HTML)
		#self.response.out.write(UPLOAD_OPML_HTML)
		return fn(self)
	return wrapper
	
# bottom of page
def footer(fn):
	def wrapper(self):
		ret = fn(self)
		self.response.out.write('</body></html>')
		return ret
	return wrapper

def get_feed_user(google_user):
	u = User.gql("WHERE id = :1", google_user.user_id())
	if u.count() > 0:
		user_obj = u.get()
		logging.info("User " + google_user.nickname() + " logged in")
	else:
		logging.info("New user:" + google_user.nickname() + ", creating User")
		u = User()
		u.name = google_user.nickname()
		u.id = google_user.user_id()
		u.put()
		user_obj = u
	
	return user_obj


class MainPage(webapp2.RequestHandler):
	@login_required
	@header
	@footer
	def get(self):
		user = get_feed_user(users.get_current_user())
		
		path = os.path.join(os.path.dirname(__file__), 'views' ,'index.html')
		self.response.out.write(		
			template.render( path,{
				"name"	: users.get_current_user().nickname(),
				"signout_url"	: users.create_logout_url('/'),
				"domain": "www.socs.se",
				"year": "2014",
				"title": "LO Industries"
			})
		)

	
class AddFeed(webapp2.RequestHandler):
	def post(self):
		user = get_feed_user(users.get_current_user())
		
		all_feeds = [f.url for f in user.feeds]
		
		#f = feed.LFeed.gql("WHERE url = :1", self.request.get('feed'))
		if self.request.get('feed') not in all_feeds:
			f = LFeed()
			f.url = self.request.get('feed')
			f.added_time = datetime.datetime.now()
			f.user = user
			f.put()

		time.sleep(1)
		self.redirect('/')


class UpdateFeed(webapp2.RequestHandler):	
	@staticmethod
	def update_feed(f, self):
		try:
			f.last_update = datetime.datetime.now()
			f.put()
			logging.info("Updating " + f.url)
			frss=feedparser.parse(f.url)
			f.last_successful_update = datetime.datetime.now()
			f.put()
			logging.info("Done updating " + f.url)
			# add the the title to the feed if we don't have it
			if not f.title:
				if hasattr(frss.feed, 'title'):
					f.title = frss.feed.title
				else:
					f.title = frss.url
				f.put()
			logging.info("size:" + str(len(frss.entries)))
			for i in frss.entries:
				
				it = i.title.replace('\n', ' ').replace('\r', '')
				if f.items.filter('title = ', it).count() == 0:
					# check if there is a published date
					d = datetime.datetime.now()
					if hasattr(i, 'published_parsed'):
						d = datetime.datetime.fromtimestamp(mktime(i.published_parsed))
					if d < (datetime.datetime.now() - timedelta(days=7)):
						logging.info("too old, continuing")
						continue
					LFeedItem(feed=f, title=it, summary=i.summary, date=d, link=i.link, read=False).put()
					logging.info("Adding item " + it)
				else:
					logging.info("Item " + it + " already found")		
		
			# finally delete items we don't want anymore
			old_items = [i for i in f.items if i.date < (datetime.datetime.now() - timedelta(days=7))]
			
			for i in old_items:
				i.delete()
		
			logging.info("Old items3:%d" % (len(old_items)))
		
		except Exception, e:
			self.response.out.write("Failed to parse:%s" % (e))
			self.response.out.write(traceback.format_exc())
			
			
	def get(self):
		logging.info("Updating feed " + self.request.get('id'))
		f = LFeed.get_by_id(int(self.request.get('id')))
		if f:		
			logging.info("Updating feed " + self.request.get('id') + " with url " + str(f.url))
			UpdateFeed.update_feed(f, self)
		
		# wait until consistent hack
		time.sleep(1)
		self.redirect('/')


class UpdateFeeds(webapp2.RequestHandler):
	def get(self):
		for f in LFeed.all():
			UpdateFeed.update_feed(f, self)
		
		# wait until consistent hack
		time.sleep(1)
		self.redirect('/')


class UploadOPML(webapp2.RequestHandler):
	def post(self):
		user = get_feed_user(users.get_current_user())
		opml = self.request.get('opml_file')
		logging.info("XXX:" + opml + ":YYY")
		root = ET.fromstring(opml)
		for r in root[1]:
			for p in r:
				try:
					logging.info("Adding feed " + p.attrib["xmlUrl"])
					
					# XXX also add limit to max num of feeds
					
					# XXX first need to check if we already have it
					f = feed.LFeed()
					f.url = p.attrib["xmlUrl"]
					f.added_time = datetime.datetime.now()
					f.user = user
					f.title = p.attrib["title"]
					f.put()
				except:
					logging.info("Failed parsing OPML")
		
		self.redirect('/')

				
class DeleteFeed(webapp2.RequestHandler):
	def get(self):
		f = LFeed.get_by_id(int(self.request.get('id')))
		if f:
			f.delete()
		# hack to make datastore consistent
		time.sleep(1)
		self.redirect('/')
		
class MarkAsFeed(webapp2.RequestHandler):
	def get(self):
		if self.request.get('mark') == 'read':
			read = True
		else:
			read = False
		data = {'feeds':[]}
		f = LFeed.get_by_id(int(self.request.get('id')))
		if f:
			for i in f.items:
				logging.info("Marking as read:" + str(read))
				# only the feeds that are different to what we are setting it to
				if i.read != read:
					i.read = read
					i.put()
		# hack to make datastore consistent
		time.sleep(1)
		self.response.out.write(json.dumps(data))

		
class JSONFeeds(webapp2.RequestHandler):
	def get(self):
		user = get_feed_user(users.get_current_user())
		data = {'feeds':[]}
		for f in user.feeds.order('-title'):
			feed = {}
			if not f.title:
				ftitle = f.url
			else:
				ftitle = f.title
			feed['title'] = ftitle
			feed['key'] = str(f.key().id())
			feed['unread_items'] = len([i for i in f.items if not i.read])
			data['feeds'].append(feed)		
		self.response.out.write(json.dumps(data))

		
class JSONFeed(webapp2.RequestHandler):
	def get(self):
		user = get_feed_user(users.get_current_user())
		data = {'items':[]}
		f = LFeed.get_by_id(int(self.request.get('id')))
		data['feed'] = {'title': f.title, 'last_update': f.last_successful_update.strftime("%d%b %H:%M"), 'key':str(f.key().id()), 'unread_items': len([i for i in f.items if not i.read])}
		for i in f.items.order('-date'):
			item = {}
			item['title'] = i.title
			item['id'] = str(i.key().id())
			item['link'] = i.link
			item['summary'] = i.summary
			item['read'] = i.read
			item['date'] = i.date.strftime("%d%b %H:%M")
			data['items'].append(item)		
		self.response.out.write(json.dumps(data))		

		
class FollowLink(webapp2.RequestHandler):
	def get(self):
		user = get_feed_user(users.get_current_user())
		item_id = self.request.get('id')
		if not item_id:
			self.redirect('/')
		item = LFeedItem.get_by_id(int(item_id))
		if item:
			item.read = True
			# just in case we're out of writes should still follow link
			try:
				item.put()
			except Exception as e:
				pass
			self.redirect(str(item.link))
		else:
			self.response.out.write("Failed")
			
						
application = webapp2.WSGIApplication([
    ('/', MainPage),
	('/add_feed', AddFeed),
	('/update_feed', UpdateFeed),
	('/markas_feed', MarkAsFeed),
	('/delete_feed', DeleteFeed),
	('/read', FollowLink),
	('/update_feeds', UpdateFeeds),
	('/upload_opml', UploadOPML),
	('/json/feeds', JSONFeeds),
	('/json/feed', JSONFeed),
], debug=True)