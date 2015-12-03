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

		event = ndb.Key(models.event_info, int(id)).get()

		#email = get_user_email()
		#text = self.request.get("comment")
		#event.create_comment(email,text)
		self.redirect("/event?id=" + id)

class CommentHandler(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")
		#logging.warning("AYYYYYYYY")
		#logging.warning(id)
		event = ndb.Key(models.event_info, int(id)).get()
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
		event = ndb.Key(models.event_info, int(id)).get()
		event.votes = event.votes + 1
		event.put()
		self.redirect("/event?id=" + id)

class DownVoteHandler(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")
		logging.warning(id)
		event = ndb.Key(models.event_info, int(id)).get()
		if event.votes != 0:
			event.votes = event.votes - 1
			event.put()
		self.redirect("/event?id=" + id)

class DeleteEvent(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")
		event = ndb.Key(models.event_info, int(id)).get()
		event.delete_comments()
		event.key.delete()
		# time.sleep prevents it from showing on the front page due to redirect happening before the item is deleted
		# Will look into a better solution
		time.sleep(0.1)
		self.redirect('/')

class ProcessForm(webapp2.RequestHandler):
	def post(self):
		email = get_user_email()
		if not email:
			email = "Anonymous"

		form_title = self.request.get("title")
		form_summary = self.request.get("summary")
		form_location = self.request.get("location")
		form_information = self.request.get("information")
		form_start_date = self.request.get("startdate")
		form_end_date = self.request.get("enddate")
		form_start_time = self.request.get("starttime")
		form_end_time = self.request.get("endtime")
		#logging.warning("HELLO WORLD")
		#logging.warning(self.request.get("attendance"))
		form_attendance = int(self.request.get("attendance"))
		event_number = get_global_id()
		
		event = models.event_info()
		event.populate(title=form_title,
		summary=form_summary,
		information=form_information,
		start_date=form_start_date,
		end_date=form_end_date,
		start_time=form_start_time,
		end_time=form_end_time,
		attendance=form_attendance,
		location=form_location,
		votes=0,
		user=email,
		event_number = event_number,)

		# This is probably a bad key. Need to figure out a better way to do this. These aspects of the event are uneditable now
		key_data = event_number
		#key_data = key_data.urlsafe()
		event.key = ndb.Key(models.event_info, key_data)
		event.put()
		self.redirect("/event?id=" + str(key_data))

class EditHandler(webapp2.RequestHandler):
	def get(self):
		id = self.request.get("id")
		logging.warning("Hello")
		event = ndb.Key(models.event_info, int(id)).get()
		email = get_user_email()
		page_params = {
		"user_email": email,
		'login_url': users.create_login_url(),
		'logout_url': users.create_logout_url('/'),
		'event': event,
		}
		render_template(self, 'editEventPage.html', page_params)
		
	def post(self):
		logging.warning("Hello2")
		id = self.request.get("id")
		
		form_title = self.request.get("title")
		form_summary = self.request.get("summary")
		form_location = self.request.get("location")
		form_information = self.request.get("information")
		form_start_date = self.request.get("startdate")
		form_end_date = self.request.get("enddate")
		form_start_time = self.request.get("starttime")
		form_end_time = self.request.get("endtime")
		form_attendance = int(self.request.get("attendance"))

		event = ndb.Key(models.event_info, int(id)).get()
		
		event.populate(title=form_title,
		summary=form_summary,
		information=form_information,
		start_date=form_start_date,
		end_date=form_end_date,
		start_time=form_start_time,
		end_time=form_end_time,
		attendance=form_attendance,
		location=form_location)
		
		
		
		event.key = ndb.Key(models.event_info, int(id))
		event.put()
		
		
		self.redirect('/event?id=' + id)
		
class display_event(webapp2.RequestHandler):
	
	def get(self):
		id = self.request.get("id")
		delete = 0
		event = ndb.Key(models.event_info, int(id)).get()
		logging.warning(event)
		email = get_user_email()
		comments = event.get_comments()
		#logging.warning("AYYYYYYY")
		#logging.warning(event.user)
		#logging.warning(email)
		if event.user == email:
			delete = 1

		page_params = {
		  'user_email': email,
		  'login_url': users.create_login_url(),
		  'logout_url': users.create_logout_url('/'),
		  "event": event,
		  "comments": comments,
		  "delete": delete
		}

		render_template(self, 'event.html', page_params)

class event_list(webapp2.RequestHandler):
	def get(self):
		list = models.obtain_events()
		email = get_user_email()
		page_params = {
      'user_email': email,
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/'),
	  "list": list
    }

		render_template(self, 'table.html', page_params)

##
# This gets and increases the global id value. Don't go calling it unless you are adding something
def get_global_id():
	id = ndb.Key(models.global_id, "number").get()
	value = id.next_id
	id.increase_id()
	id.put()
	return value
	
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
    email = get_user_email()
    list = models.sort_by_votes()
    featured = models.get_featured()
    user_id = get_user_id()
    page_params = {
      'user_email': email,
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/'),
	  "list": list,
	  "featured": featured,
	  'user_id': user_id,
    }
    render_template(self, 'frontPage.html', page_params)

class ProfileHandler(webapp2.RequestHandler):
	def get(self):
		id = self.request.get("id")
		q = models.get_user_profile(id)
		if q == []:
			create_profile(id)
		profile = ndb.Key(models.user_profile, id).get()
		page_params = {
			'user_email': get_user_email(),
			'login_url': users.create_login_url(),
			'logout_url': users.create_logout_url('/'),
			'user_id': id,
		}
		render_template(self, 'profile.html', page_params)

def create_profile(id):
	profile = models.user_profile()
	profile.user_id = id
	profile.key = ndb.Key(models.user_profile,id)
	profile.put()
	logging.warning("profile created!")
	
class AddEventPageHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    page_params = {
      'user_email': email,
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/')
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
		logging.warning("WORLD")
		email = get_user_email()
		logging.warning("hello")
		id = models.global_id()
		id.next_id = 1
		id.key = ndb.Key(models.global_id, "number")
		id.put()
		
		page_params = {
		'user_email': email,
		'login_url': users.create_login_url(),
		'logout_url': users.create_logout_url('/'), 
		'profile_id': users.user_id(),
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
