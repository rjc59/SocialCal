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


class calendar:

	def __init__(self):
		self.event = {
		'summary': 'This is a summary',
		'location': 'This is a location',
		'description': 'This is a description',
		'start': {
			'dateTime': '2015-10-6T09:00:00-07:00',
			'timeZone': 'America/Los_Angeles',
			},
		'end': {
			'dateTime': '2015-10-6T17:00:00-07:00',
			'timeZone': 'America/Los_Angeles',
		},
		'recurrence': [
				'RRULE:FREQ=DAILY;COUNT=2'
		],
		'attendees': [
		{'email': 'lpage@example.com'},
		{'email': 'sbrin@example.com'},
		],
		'reminders': {
				'useDefault': False,
				'overrides': [
		{'method': 'email', 'minutes': 24 * 60},
		{'method': 'popup', 'minutes': 10},
		],
	  },
	}
	
	def get_event(self):
		return self.event

class ProcessForm(webapp2.RequestHandler):
	def post(self):
		store = calendar()
		event = store.get_event()
		#logging.info(event)
		event["summary"] = self.request.get("summary")
		event["location"] =	self.request.get("location")
		event["attendees"][0] = self.request.get("attendees")
		startdate = self.request.get("startdate")
		starttime = self.request.get("starttime")
		enddate = self.request.get("enddate")
		endtime = self.request.get("endtime")
		event["start"]["dateTime"] = str(startdate) + " at " + str(starttime)
		event["end"]["dateTime"] = str(enddate) + " at " + str(endtime)
		render_template(self, "formresults.html", {
		"dongs": json.dumps(event),
		"summary": event["summary"],
		"location": event["location"],
		"attendees": event["attendees"][0],
		"start": event["start"]["dateTime"],
		"end": event["end"]["dateTime"],
		})
		


	
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

mappings = [
  ('/', MainPageHandler),
  ('/processform', ProcessForm),
]
app = webapp2.WSGIApplication(mappings, debug = True)
	