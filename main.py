#import datetime
import logging
import os
import webapp2
import time
#import json
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb
#from google.appengine.api import images
#from google.appengine.ext import blobstore
#from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import mail
import models

class VoteHandler(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")

		event = models.get_event_info(id)

		self.redirect("/event?id=" + id)

class CommentHandler(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")
		event = models.get_event_info(id)
		email = get_user_email()
		if not email:
			email = "Anonymous"

		text = self.request.get("comment")
		event.create_comment(email,text)
		self.redirect("/event?id=" + id)

		if event.user != "Anonymous":
			mail.send_mail(sender="socialeventcal@socialeventcal.appspotmail.com", to=event.user, subject="Someone commented on your post!", body="Someone commented on your post! Click here to see it: gdh12-socal-test.appspot.com/event?id=" + id)


class UpVoteHandler(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")
		logging.warning(id)
		event = models.get_event_info(id)
		event.votes = event.votes + 1
		event.put()
		self.redirect("/event?id=" + id)

class DownVoteHandler(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")
		logging.warning(id)
		event = models.get_event_info(id)
		if event.votes != 0:
			event.votes = event.votes - 1
			event.put()
		self.redirect("/event?id=" + id)

class DeleteEvent(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")
		event = models.get_event_info(id)
		event.delete_comments()
		event.key.delete()
		
		time.sleep(0.1)
		self.redirect('/')

class ProcessForm(webapp2.RequestHandler):
	def post(self):
		email = get_user_email()
		if not email:
			email = "Anonymous"

		title = self.request.get("title")
		summary = self.request.get("summary")
		location = self.request.get("location")
		information = self.request.get("information")
		start_date = self.request.get("startdate")
		end_date = self.request.get("enddate")
		start_time = self.request.get("starttime")
		end_time = self.request.get("endtime")
		attendance = int(self.request.get("attendance"))
		
		event_number = models.create_event(title, summary, information, start_date, end_date, start_time, end_time, attendance, location, email)

		self.redirect("/event?id=" + str(event_number))

class EditHandler(webapp2.RequestHandler):
	def get(self):
		id = self.request.get("id")

		page_params = {
		"user_email": get_user_email(),
		'login_url': users.create_login_url(),
		'logout_url': users.create_logout_url('/'),
		'event': models.get_event_info(id),
		'user_id': get_user_id(),
		}
		render_template(self, 'editEventPage.html', page_params)
		
	def post(self):
		id = self.request.get("id")
		
		title = self.request.get("title")
		summary = self.request.get("summary")
		location = self.request.get("location")
		information = self.request.get("information")
		start_date = self.request.get("startdate")
		end_date = self.request.get("enddate")
		start_time = self.request.get("starttime")
		end_time = self.request.get("endtime")
		attendance = int(self.request.get("attendance"))

		event_number = models.edit_event(title, summary, information, start_date, end_date, start_time, end_time, attendance, location, id)

		self.redirect("/event?id=" + str(event_number))		
		
class display_event(webapp2.RequestHandler):
	
	def get(self):
		id = self.request.get("id")
		delete = 0
		event = models.get_event_info(id)
		email = get_user_email()
		comments = event.get_comments()

		if event.user == email:
			delete = 1

		page_params = {
		  'user_email': email,
		  'login_url': users.create_login_url(),
		  'logout_url': users.create_logout_url('/'),
		  "event": event,
		  "comments": comments,
		  "delete": delete,
		  'user_id': get_user_id(),
		}

		render_template(self, 'event.html', page_params)

class event_list(webapp2.RequestHandler):
	def get(self):
	
		page_params = {
      'user_email': get_user_email(),
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/'),
	  "list": models.obtain_events(),
	  'user_id': get_user_id(),
    }

		render_template(self, 'table.html', page_params)
	
###############################################################################
# We'll just use this convenience function to retrieve and render a template.
def render_template(handler, templatename, templatevalues={}):
  path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
  html = template.render(path, templatevalues)
  handler.response.out.write(html)

###############################################################################
# We'll use this convenience function to retrieve the current user's email.
def get_user_email():
  result = None
  user = users.get_current_user()
  if user:
    result = user.email()
  return result

def get_user_id():
	result = None
	user = users.get_current_user()
	if user:
		result = user.user_id()
	return result
	
class MainPageHandler(webapp2.RequestHandler):
	def get(self):
		id = get_user_id()
		location_list = ""
		
		q = models.check_if_user_profile_exists(id)
		if q != []:
			location_list = models.get_by_location(q[0].location)
		
		page_params = {
		'user_email': get_user_email(),
		'login_url': users.create_login_url(),
		'logout_url': users.create_logout_url('/'),
		"list": models.sort_by_votes(),
		"featured": models.get_featured(),
		"location_list": location_list,
		"user_id": id,
		}
		render_template(self, 'frontPage.html', page_params)

class ProfileHandler(webapp2.RequestHandler):
	def get(self):
		id = self.request.get("id")
		q = models.check_if_user_profile_exists(id)
		if q == []:
			models.create_profile(id)
			
		page_params = {
			'user_email': get_user_email(),
			'login_url': users.create_login_url(),
			'logout_url': users.create_logout_url('/'),
			'user_id': get_user_id(),
			'profile': models.get_user_profile(id),
		}
		render_template(self, 'profile.html', page_params)
	
	def post(self):
		id = get_user_id()
		profile = models.get_user_profile(id)
		name = self.request.get("name")
		location = self.request.get("location")
		interests = self.request.get("interests")
		
		profile.populate(name = name, location = location, interests = interests)
		profile.put()
		self.redirect('/profile?id=' + id)
	
class AddEventPageHandler(webapp2.RequestHandler):
  def get(self):
  
    page_params = {
      'user_email': get_user_email(),
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/'),
	  'user_id': get_user_id(),
    }
    render_template(self, 'addEventPage.html', page_params)

	
class calendar(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    page_params = {
    }
    render_template(self, 'calendar.html', page_params)

	
class test(webapp2.RequestHandler):
	def get(self):
		id = models.global_id()
		id.next_id = 1
		id.key = ndb.Key(models.global_id, "number")
		id.put()
		
		page_params = {
		'user_email': get_user_email(),
		'login_url': users.create_login_url(),
		'logout_url': users.create_logout_url('/'), 
		'user_id': get_user_id(),
		}
		render_template(self, 'blanktest.html', page_params)
		
mappings = [
  ('/', MainPageHandler),
  ('/processform', ProcessForm),
  ('/event', display_event),
  ('/list', event_list),
  ('/addevent', AddEventPageHandler),
  ('/CommentHandler', CommentHandler),
  ('/UpVote', UpVoteHandler),
  ('/DownVote', DownVoteHandler),
  ('/DeleteEvent', DeleteEvent),
  ('/calendar', calendar),
  ('/edit', EditHandler),
  ('/profile', ProfileHandler),
  ('/test', test),
]
app = webapp2.WSGIApplication(mappings, debug = True)
