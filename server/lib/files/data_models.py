"""
Database Models for file app apart of MeXelearn project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""
import random, hashlib, datetime, logging, json
# importing google ndb datastor api
from google.appengine.ext import ndb
# user login
from google.appengine.api import users
# base ndb class
from mx.data_model import *
# blobstore api
from google.appengine.ext import blobstore

def files_key(group = 'default'):
    return generate_key(name='files', group=group)

class File(BaseNDB):
	user_id = ndb.IntegerProperty()
	user_nickname = ndb.StringProperty()
	blob = ndb.BlobKeyProperty()
	name = ndb.StringProperty()
	size = ndb.IntegerProperty()
	content_type = ndb.StringProperty()

	own_key_name = 'files'
	dict_include = None
	dict_exclude = ['blob']

	@classmethod
	def add_file(cls,user_id,user_nickname,blob,name,size,content_type,group='default'):
		return cls(parent = files_key(group=group),
			       user_id=user_id,
				   user_nickname=user_nickname,
				   blob=blob,
				   name=name,
				   size=size,
				   content_type=content_type)

	@classmethod
	def delete_file(cls, fid):
		f = cls.by_id(fid)
		if f:
			f.delete_me()

	def delete_me(cls):
		blob = blobstore.BlobInfo.get(cls.blob)
		blob.delete()
		cls.key.delete()
