"""
Database Models for user app apart of MeXelearn project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""
import random, hashlib, datetime, logging, json
# importing google ndb datastor api
from google.appengine.ext import ndb
# user login
from google.appengine.api import users
# project settings
from settings import LOCALE
# base ndb class
from mx.data_model import *
from mx.assets.misc import valid_pw


def users_key(group = 'default'):
    return generate_key(name='users', group=group)


class UserSocialContact(ndb.Model):
    f = ndb.StringProperty()
    t = ndb.StringProperty()
    g = ndb.StringProperty()
    i = ndb.StringProperty()


class LocalUser(BaseNDB):
	user_id = ndb.StringProperty()
	role = ndb.StringProperty(default='u')
	email = ndb.StringProperty()
	pw_hash = ndb.StringProperty()
	firstname = ndb.StringProperty()
	lastname = ndb.StringProperty()
	nickname = ndb.StringProperty()
	username = ndb.StringProperty()
	locale = ndb.StringProperty(default=LOCALE)
	about = ndb.TextProperty()
	country = ndb.StringProperty()
	avatar = ndb.IntegerProperty()
	contact = ndb.StructuredProperty(UserSocialContact)

	own_key_name = 'users'
	dict_include = None
	dict_exclude = ['pw_hash', 'user_id', 'role','created', 'last_modified']

	@classmethod
	def by_google_id(cls, uid):
		return cls.query().filter(cls.user_id == uid).get()

	@classmethod
	def by_email(cls, email):
		return cls.query().filter(cls.email == email).get()

	@classmethod
	def register(cls, user_id, email, nickname, role = 'u', group = 'default'):
		"register with goole account info"
		return cls(parent = users_key(group=group),
			       user_id = user_id,
			       email = email,
			       nickname = nickname,
			       role = role)

	@classmethod
	def signup(cls, firstname, lastname, nickname, pw_hash, email, role, group = 'default'):
		"reister local user with email and password"
		return cls(parent = users_key(group=group),
			       firstname = firstname,
			       lastname = lastname,
			       nickname = nickname,
			       pw_hash = pw_hash,
			       email = email,
			       role = role)

	@classmethod
	def login(cls, email, pw):
		u = cls.by_email(email)
		if u and valid_pw(email, pw, u.pw_hash):
			return u

	@classmethod
	def update_info(cls, locale='ar-EG'):
		return cls(locale=locale)

	@classmethod
	def update_contact(cls,user_id,f=None,t=None,g=None,i=None):
		c = UserSocialContact(f=f,t=t,g=g,i=i)
		u = cls.by_id(user_id)
		u.contact = c
		u.put()
