#import datetime
import logging
import os
import webapp2
#import json
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb

class global_id(ndb.Model):
	next_id = ndb.StringProperty()
	
	def increase_id(self):
		self.next_id = self.next_id + 1

class user_profile(ndb.Model):
	user_id = ndb.StringProperty()
	
	
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
		#logging.warning("test")
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
	
def obtain_events():
	result = list()
	q = event_info.query()
	for event in q.fetch(100):
		result.append(event)
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
	
def get_user_profile(id):
	logging.warning("start!")
	result = list()
	q = event_info.query(user_profile.user_id == id)
	q = q.fetch(1)
	logging.warning("This is q")
	logging.warning(q)
	if q == []:
		logging.warning("empty!")
	return q