import datetime
import logging
import os
import webapp2
import time
from __future__ import print_function
import httplib2
#import json

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb
#from google.appengine.api import images
#from google.appengine.ext import blobstore
#from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import mail
import models

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


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
<<<<<<< HEAD
			mail.send_mail(sender="socialcalender1520@appspot.gserviceaccount.com", to=event.user, subject="Someone commented on your post!", body="Someone commented on your post! Click here to see it: socialcalender1520.appspot.com/event?id=" + id)
=======
			mail.send_mail(sender="socialeventcal@socialeventcal.appspotmail.com", to=event.user, subject="Someone commented on your post!", body="Someone commented on your post! Click here to see it: socialeventcal.appspot.com/event?id=" + id)
>>>>>>> 4c3c6772435dcac4ae64439cc01106b6819c970d

class FeatureEvent(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")
		models.setFeatured(id)

		self.redirect("/event?id=" + id)

class UpVoteHandler(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")
		email = get_user_email()
		models.UpVoteEvent(id, email)

		self.redirect("/event?id=" + id)

class DownVoteHandler(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")
		email = get_user_email()
		models.DownVoteEvent(id, email)

		self.redirect("/event?id=" + id)

class DeleteEvent(webapp2.RequestHandler):
	def post(self):
		id = self.request.get("id")
		models.delete_event(id)
	#	event = models.get_event_info(id)
	#	event.delete_comments()
	#	event.key.delete()

	#	time.sleep(0.1)
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
		is_admin = 0
		event = models.get_event_info(id)
		email = get_user_email()
		#logging.warning(event)
		comments = event.get_comments()

		if event.user == email:
			delete = 1

		if users.is_current_user_admin():
			delete = 1
			is_admin = 1

		page_params = {
		  'user_email': email,
		  'login_url': users.create_login_url(),
		  'logout_url': users.create_logout_url('/'),
		  "event": event,
		  "comments": comments,
		  "delete": delete,
		  "is_admin": is_admin,
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

class add_to_calendar(webapp2.RequestHandler):
	def get(self):
		id = self.request.get("id")
		event_to_store = models.get_event_info(id)
		email = get_user_email()

		credentials = get_credentials()
	    http = credentials.authorize(httplib2.Http())
	    service = discovery.build('calendar', 'v3', http=http)

	    now = datetime.datetime.utcnow().isoformat() + 'Z' # UTC time

		event = {
		  'summary': event_to_store.title,
		  'location': event_to_store.location,
		  'description': event_to_store.summary,
		  'start': {
            'dateTime': '2015-05-28T09:00:00-07:00',
            'timeZone': 'America/New_York',
          },
		  'end': {
            'dateTime': '2015-05-28T09:00:00-07:00',
            'timeZone': 'America/New_York',
          },
		  'attendees[].email': email,
		  'reminders.overrides[].method': 'popup',
		  'reminders.overrides[].minutes': '1440',
		}

		event = service.events().insert(calendarId='primary', body=event).execute()

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

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

class MainPageHandler(webapp2.RequestHandler):
	def get(self):
		id = get_user_id()
	#	location_list = ""

		q = models.check_if_user_profile_exists(id)
		#if q != []:
		#	location_list = models.get_by_location(q[0].location)

		page_params = {
		'user_email': get_user_email(),
		'login_url': users.create_login_url(),
		'logout_url': users.create_logout_url('/'),
		"list": models.sort_by_votes(),
		"featured": models.get_featured(),
		#"location_list": location_list,
		"recent_events": models.get_recent_events(),
		"user_id": id,
		}
		render_template(self, 'frontPage.html', page_params)

class ProfileHandler(webapp2.RequestHandler):
	def get(self):
		id = self.request.get("id")
		logging.warning(id)
		q = models.check_if_user_profile_exists(id)
		if q == []:
			models.create_profile(id)

		page_params = {
			'user_email': get_user_email(),
			'login_url': users.create_login_url(),
			'logout_url': users.create_logout_url('/'),
			"list": models.obtain_events(),
			'user_id': get_user_id(),
			'profile': models.get_user_profile(id),
		}
		render_template(self, 'profile.html', page_params)

	def post(self):
		id = get_user_id()
		name = self.request.get("name")
		location = self.request.get("location")
		interests = self.request.get("interests")

		models.update_profile(id, name, location, interests)

		self.redirect('/profile?id=' + id + "&search=" + get_user_email())

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

class about(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    page_params = {
	  'user_email': email,
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/'),
	  'user_id': get_user_id(),
    }
    render_template(self, 'about.html', page_params)

class test(webapp2.RequestHandler):
	def get(self):
		models.create_global_id()
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
  ('/FeatureEvent', FeatureEvent),
  ('/test', test),
  ('/about', about),

]
app = webapp2.WSGIApplication(mappings, debug = True)
