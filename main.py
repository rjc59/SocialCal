import datetime
import logging
import os
import webapp2
import json
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

class event_info(ndb.Model):
	title = ndb.StringProperty()
	summary = ndb.StringProperty()
	location = ndb.StringProperty()
	information = ndb.TextProperty()
	start_date = ndb.StringProperty()
	end_date = ndb.StringProperty()
	start_time = ndb.StringProperty()
	end_time = ndb.StringProperty()
	attendance = ndb.IntegerProperty() ## assuming this is a number for now
	time_created = ndb.DateTimeProperty(auto_now_add=True)
	
	
class event_comments(ndb.Model):
	pass
	
class ProcessForm(webapp2.RequestHandler):
	def post(self):
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
		
		event = event_info()
		event.populate(title=form_title, 
		summary=form_summary, 
		information=form_information, 
		start_date=form_start_date, 
		end_date=form_end_date, 
		start_time=form_start_time, 
		end_time=form_end_time,
		attendance=form_attendance,
		location=form_location)
		
		# This is probably a bad key. Need to figure out a better way to do this. These aspects of the event are uneditable now
		key_data = event.title + event.start_date + event.start_time
		#key_data = key_data.urlsafe()
		event.key = ndb.Key(event_info, key_data)
		event.put()
		#logging.warning(key_data)
		self.redirect("/event?id=" + key_data)


class display_event(webapp2.RequestHandler):
	def get(self):
		id = self.request.get("id")
		
		event = ndb.Key(event_info, id).get()
		email = get_user_email()
	#	logging.warning(event.title)
		page_params = {
		  'user_email': email,
		  'login_url': users.create_login_url(),
		  'logout_url': users.create_logout_url('/'),
		  "event": event
		}
		
		render_template(self, 'event.html', page_params)
	
class event_list(webapp2.RequestHandler):
	def get(self):
		list = obtain_events()
	
def obtain_events():
	result = list()
	q = event_info.query()
	for event in q.fetch(100):
		result.append(event)
	return result
		
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
  
class MainPageHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    page_params = {
      'user_email': email,
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/')
    }
	
    render_template(self, 'frontPage.html', page_params)

class AddEventPageHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    page_params = {
      'user_email': email,
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/')
    }
	
    render_template(self, 'addEventPage.html', page_params)	
	
mappings = [
  ('/', MainPageHandler),
  ('/processform', ProcessForm),
  ('/event', display_event),
  ('/list', event_list),
  ('/addevent', AddEventPageHandler)
]
app = webapp2.WSGIApplication(mappings, debug = True)
	