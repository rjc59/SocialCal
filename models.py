#import datetime
import logging
import os
import webapp2
#import json
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb


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
	
	user = ndb.StringProperty()
	
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