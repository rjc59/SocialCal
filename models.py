#import datetime
import logging
import os
import webapp2
#import json
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache


class global_id(ndb.Model):
	next_id = ndb.IntegerProperty()
	
	def increase_id(self):
		#logging.warning(self.next_id)
		self.next_id = self.next_id + 1

class user_profile(ndb.Model):
	user_id = ndb.StringProperty()
	name = ndb.StringProperty()
	location = ndb.StringProperty()
	interests = ndb.StringProperty()
	
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
	votes = ndb.IntegerProperty()
	event_number = ndb.IntegerProperty()
	user = ndb.StringProperty()
	
	featured = ndb.BooleanProperty()

	def create_comment(self, xuser, xtext):
		comment = event_comment(parent=self.key)
		comment.populate(user=xuser, text=xtext)
		comment.put()
		return comment
		
	def get_comments(self):
		result = list()
		q = event_comment.query(ancestor=self.key)
		q = q.order(-event_comment.time_created)
		for i in q.fetch(100):
			result.append(i)
		return result
	
	def delete_comments(self):
		result = list()
		q = event_comment.query(ancestor=self.key)
		for i in q.fetch(100):
			i.key.delete()
		
class event_comment(ndb.Model):
	user = ndb.StringProperty()
	text = ndb.TextProperty()
	time_created = ndb.DateTimeProperty(auto_now_add=True)

def create_event(title, summary, information, start_date, end_date, start_time, end_time, attendance, location, email):

	event_number = get_global_id()
	event = event_info()
	event.populate(title=title,
		summary=summary,
		information=information,
		start_date=start_date,
		end_date=end_date,
		start_time=start_time,
		end_time=end_time,
		attendance=attendance,
		location=location,
		votes=0,
		user=email,
		event_number = event_number,)
		
	event.key = ndb.Key(event_info, event_number)
	event.put()
	
	memcache.delete('events')
	memcache.set(str(event.number), event, namespace='event')
	
	return event_number

def edit_event(title, summary, information, start_date, end_date, start_time, end_time, attendance, location, event_number):
	
	event = get_event_info(event_number)
	event.populate(title=title,
		summary=summary,
		information=information,
		start_date=start_date,
		end_date=end_date,
		start_time=start_time,
		end_time=end_time,
		attendance=attendance,
		location=location,)
		
	##event.key = ndb.Key(event_info, event_number)
	event.put()
	
	memcache.delete('events')
	memcache.set(str(event.key), event_info, namespace='event')	
	
	return event_number

def obtain_events():
	result = memcache.get("events")
	if not result:
		result = list()
		q = event_info.query()
		for event in q.fetch(100):
			result.append(event)
		memcache.set('events', result)
	return result
	
def sort_by_votes():
	result = list()
	q = event_info.query()
	q = q.order(-event_info.votes)
	for i in q.fetch(5):
		result.append(i)
	return result

def get_featured():
	result = list()
	q = event_info.query(event_info.featured == True)
	for i in q.fetch(4):
		result.append(i)
	return result

def get_by_location(location):
	result = list()
	q = event_info.query(event_info.location == location)
	q = q.order(-event_info.time_created)
	for i in q.fetch(5):
		result.append(i)
	return result
	

def get_event_info(id):
	result = memcache.get(id, namespace="event")
	if not result:
		#logging.warning("AYYYYYYLMAO")
		result = ndb.Key(event_info, int(id)).get()
	#	logging.warning(result)
		memcache.set(id, result, namespace='event')
	#logging.warning(result)
	return result

def get_user_profile(id):
	result = ndb.Key(user_profile, id).get()
	return result
	
def check_if_user_profile_exists(id):
	result = list()
	q = user_profile.query(user_profile.user_id == id)
	q = q.fetch(1)
	
	##if q == []:
	return q
	
def get_global_id():
	id = ndb.Key(global_id, "number").get()
	
	value = id.next_id
	
	id.increase_id()
	id.put()
	return value
	
def create_profile(id):
	profile = user_profile()
	profile.user_id = id
	profile.key = ndb.Key(user_profile,id)
	profile.put()
