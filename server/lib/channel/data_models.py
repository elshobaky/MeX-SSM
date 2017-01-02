"""
Database Models for channel app apart of MeXelearn project.
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

from mx.assets.misc import valid_key

def masters_key(group = 'default'):
    return generate_key(name='masters', group=group)

class Master(BaseNDB):
	user_id = ndb.IntegerProperty()
	key_hash = ndb.TextProperty()

	own_key_name = 'masters'
	dict_include = None
	dict_exclude = ['created', 'last_modified', 'key_hash']

	@classmethod
	def register(cls, user_id, key_hash, group = 'default'):
		return cls(parent = masters_key(group=group),
			       user_id = user_id,
			       key_hash = key_hash)

	@classmethod
	def validate(cls, master_id, user_id, key):
		master = cls.by_id(master_id)
		if master and valid_key(user_id, key, master.key_hash):
			return master




def slaves_key(group = 'default'):
    return generate_key(name='slaves', group=group)

class Slave(BaseNDB):
	master_id = ndb.IntegerProperty(required=True)
	key_hash = ndb.TextProperty()

	own_key_name = 'slaves'
	dict_include = None
	dict_exclude = ['created', 'last_modified']

	@classmethod
	def register(cls, master_id, key_hash, group = 'default'):
		return cls(parent = slaves_key(group=group),
			       master_id = master_id,
			       key_hash = key_hash)

	@classmethod
	def validate(cls, slave_id, master_id, key):
		slave = cls.by_id(slave_id)
		if slave and valid_key(master_id, key, slave.key_hash):
			return slave


def cmds_key(group = 'default'):
    return generate_key(name='cmds', group=group)

class Cmd(BaseNDB):
	master_id = ndb.IntegerProperty(required=True)
	slave_id = ndb.IntegerProperty(required=True)
	cmd = ndb.TextProperty(required=True)
	executed = ndb.BooleanProperty(default=False)
	output = ndb.TextProperty()


	own_key_name = 'cmds'
	dict_include = None
	dict_exclude = []

	@classmethod
	def add(cls, master_id, slave_id, cmd, group = 'default'):
		return cls(parent = cmds_key(group=group),
			       master_id = master_id,
			       slave_id = slave_id,
			       cmd = cmd)

	@classmethod
	def get(cls, master_id=None, slave_id=None, executed=None, min_date=None, n=10, s=0):
		filters = []
		if master_id: filters.append(cls.master_id == master_id)
		if slave_id: filters.append(cls.slave_id == slave_id)
		if executed is not None : filters.append(cls.executed == executed)
		if min_date: filters.append(cls.created > min_date)
		cmds = cls.query()
		for f in filters:
			cmds = cmds.filter(f)
		return cmds.order(cls.created).fetch(n,offset=s)


def chfiles_key(group = 'default'):
    return generate_key(name='chfiles', group=group)

class ChFile(BaseNDB):
	user_type = ndb.StringProperty()
	master_id = ndb.IntegerProperty()
	slave_id = ndb.IntegerProperty()
	cmd_id = ndb.IntegerProperty()
	blob = ndb.BlobKeyProperty()
	name = ndb.StringProperty()
	size = ndb.IntegerProperty()
	content_type = ndb.StringProperty()

	own_key_name = 'chfiles'
	dict_include = None
	dict_exclude = ['blob']

	@classmethod
	def add_file(cls,user_type,master_id,slave_id,cmd_id,blob,name,size,content_type,group='default'):
		return cls(parent = chfiles_key(group=group),
			       user_type=user_type,
			       master_id=master_id,
				   slave_id=slave_id,
				   cmd_id=cmd_id,
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