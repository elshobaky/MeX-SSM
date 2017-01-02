"""
Request handlers for channel app a part of MeXelearn project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""
# importing frequently used handlers
from mx.handlers import MainHandler, UploadHandler, DownloadHandler, t
# Data Models
from data_models import *
# Auth hlpers
from mx.assets.misc import make_key, make_key_hash, valid_key

### Master control ###
class NewMaster(MainHandler):
	"create new master"
	def get(self):
		"""creates new master returns json object with master id and its key for auth
		   - requires admin login
		   - key is not saved on the server so it must b saveed by the user as it cannot be restored"""
		if not self.admin:
			self.redirect_to('user-login', ref=self.uri_for('new-master'))
			return
		master_key = make_key()
		user_id = self.admin.key.id()
		key_hash = make_key_hash(str(user_id), master_key)
		master = Master.register(user_id=user_id, key_hash=key_hash)
		master.put()
		self.write_json({'success':True,
			             'msg': 'master created successfully',
			             'master_id':master.key.id(),
			             'master_key':master_key,
			             'user_id':user_id})

class DeleteMaster(MainHandler):
	"deletes master with id given in url"
	def get(self, master_id):
		master = Master.by_id(int(master_id))
		if not master:
			self.write_json({'success':False, 'msg':'master not exist'})
			return
		if not self.admin:
			if not self.user:
				self.write_json({'success':False, 'msg':'not authorized'})
				return
			if self.user.key.id() != master.user_id:
				self.write_json({'success':False, 'msg':'not authorized'})
				return
		master.delete()
		self.write_json({'success':True, 'msg':'master deleted'})

class ValidateMaster(MainHandler):
	"""validates master_id and key returns json object with success or error.
	   - POST requests only.
	   - requires master_id from url.
	   - request params :
	        - user_id : id of the master creator.
	        - key : master key provided at master creation"""
	def post(self, master_id):
		user_id = self.request.get('user_id')
		key = self.request.get('key')
		master = Master.validate(int(master_id), user_id, key)
		msg = {'success':True, 'msg':'valid!'} if master else {'success':False, 'msg':'invalid data'}
		self.write_json(msg)
	
### Slave control ###
class NewSlave(MainHandler):
	"""creates new slave
	   - POST request only
	   - req params:
	      master_id, user_id, key"""
	def post(self):
		master_id = self.request.get('master_id')
		master_id = int(master_id) if master_id.isdigit() else 0
		user_id = self.request.get('user_id')
		key = self.request.get('key')
		if not master_id:
			self.write_json({'success':False, 'msg':'invalid master_id'})
			return
		master = Master.validate(master_id, user_id, key)
		if not master:
			self.write_json({'success':False, 'msg':'invalid data'})
			return
		slave_key = make_key()
		key_hash = make_key_hash(str(master_id), slave_key)
		slave = Slave.register(master_id=master_id, key_hash=key_hash)
		slave.put()
		self.write_json({'success':True,
			             'msg': 'slave created successfully!',
						 'slave_id':slave.key.id(),
			             'slave_key':slave_key,
			             'master_id':master_id})

class DeleteSlave(MainHandler):
	"""deletes slave with id given in url
	   - POST request only.
	   - rquires slave_id in URL
	   - req params:
	      master_id, user_id, key"""
	def post(self, slave_id):
		master_id = self.request.get('master_id')
		master_id = int(master_id) if master_id.isdigit() else 1
		user_id = self.request.get('user_id')
		key = self.request.get('key')
		master = Master.validate(master_id, user_id, key)
		if not master:
			self.write_json({'success':False, 'msg':'invalid master data'})
			return
		slave = Slave.by_id(int(slave_id))
		if not slave:
			self.write_json({'success':False, 'msg':'slave not exist'})
			return
		if not slave.master_id==master_id:
			self.write_json({'success':False, 'msg':'not authorized'})
			return
		slave.delete()
		self.write_json({'success':True, 'msg':'slave deleted'})

class ValidateSlave(MainHandler):
	"""validates slave_id and key returns json object with success or error.
	   - POST requests only.
	   - requires slave_id from url.
	   - request params :
	        - master_id : id of the parent master.
	        - key : master key provided at master creation"""
	def post(self, slave_id):
		master_id = self.request.get('master_id')
		key = self.request.get('key')
		slave = Slave.validate(int(slave_id), master_id, key)
		msg = {'success':True, 'msg':'valid!'} if slave else {'success':False, 'msg':'invalid data'}
		self.write_json(msg)

class AddCmd(MainHandler):
	"""Adds command to be executed on slave side.
	   - POST requests only.
	   - request params :
	         - master_id, user_id, key (for validation).
	         - slave_id
	         - cmd: string containing command/s.
	   - returns json object with success status,
	     cmd details eg. id"""
	# validate master and slave.
	def post(self):
		master_id = self.request.get('master_id')
		master_id = int(master_id) if master_id.isdigit() else 1
		user_id = self.request.get('user_id')
		key = self.request.get('key')
		master = Master.validate(master_id, user_id, key)
		if not master:
			self.write_json({'success':False, 'msg':'invalid master data'})
			return
		slave_id = self.request.get('slave_id')
		slave_id = int(slave_id) if slave_id.isdigit() else 1
		slave = Slave.by_id(int(slave_id))
		if not slave:
			self.write_json({'success':False, 'msg':'slave not exist'})
			return
		if not slave.master_id==master_id:
			self.write_json({'success':False, 'msg':'not authorized'})
			return
		# adding command
		cmd = self.request.get('cmd')
		c = Cmd.add(master_id=master_id, slave_id=slave_id, cmd=cmd)
		c.put()
		self.write_json({'success':True,
			             'msg': 'cmd added successfully!',
			             'cmd' : c.make_dict()})

class UpdateCmd(MainHandler):
	"""Adds output to cmd by a slave.
	   - POST requests only.
	   - request params:
	        - slave_id, master_id, key.
	        - cmd_id
	        - cmd_output"""
	def post(self, cmd_id):
		master_id = self.request.get('master_id')
		key = self.request.get('key')
		slave_id = self.request.get('slave_id')
		slave_id = int(slave_id) if slave_id.isdigit() else 1
		slave = Slave.validate(int(slave_id), master_id, key)
		if not slave :
			self.write_json({'success':False, 'msg':'invalid data'})
			return
		cmd = Cmd.by_id(int(cmd_id))
		if not cmd:
			self.write_json({'success':False, 'msg':'cmd not exist'})
			return
		if cmd.executed == True:
			self.write_json({'success':False, 'msg':'cmd executed before!'})
			return
		cmd_output = self.request.get('cmd_output')
		cmd.executed = True
		cmd.output = cmd_output
		cmd.put()
		self.write_json({'success' : True,
			             'msg' : 'cmd updated successfully!',
			             'cmd' : cmd.make_dict()})



class GetCmd(MainHandler):
	"""queries the Cmd table and returns json objects with the data
	   - POST requests only
	   - request params:
	        - user_type : slave or master (essential for validating credentials.
	        - user_id : only if the user type is master.
	        - master_id : for quering and validating.
	        - slave_id : for quering and validatin.
	        - cmd_id : if given >> return only cmd with that id.
	        - key : for validating user.
	        - executed : for quering.
	        - min_date : datetime to get cmds newer than it.
	        - n : max number of cmds to return , default = 10
	        - s : cmd feching offset , default = 0"""
	def post(self):
		user_type = self.request.get('user_type')
		master_id = self.request.get('master_id')
		master_id = int(master_id) if master_id.isdigit() else 1
		master = Master.by_id(master_id)
		if not master:
			self.write_json({'success':False, 'msg':'master not exist'})
			return
		slave_id = self.request.get('slave_id')
		slave_id = int(slave_id) if slave_id.isdigit() else 0
		if slave_id:
			slave = Slave.by_id(slave_id)
			if not slave:
				self.write_json({'success':False, 'msg':'slave not exist'})
				return
		else: slave = None
		cmd_id = self.request.get('cmd_id')
		cmd_id = int(cmd_id) if cmd_id.isdigit() else 1
		cmd = Cmd.by_id(cmd_id)
		key = self.request.get('key')
		if user_type == 'master':
			user_id = self.request.get('user_id')
			master = Master.validate(master_id, user_id, key)
			if not master:
				self.write_json({'success':False, 'msg':'invalid master data'})
				return
			if cmd and cmd.master_id == master_id:
				self.write_json({'success':True, 'msg':'cmd found', 'cmds':[cmd.make_dict()]})
				return
			if slave and (slave.master_id != master_id):
				self.write_json({'success':False, 'msg':'not authorized'})
				return
		elif user_type == 'slave':
			if (not slave) or (not Slave.validate(slave_id, str(master_id), key)):
				self.write_json({'success':False, 'msg':'invalid slave data'})
				return
			if cmd and cmd.slave_id == slave_id:
				self.write_json({'success':True, 'msg':'cmd found', 'cmds':[cmd.make_dict()]})
				return
		else:
			self.write_json({'success':False, 'msg':'invalid user_type'})
			return
		executed = self.request.get('executed')
		if executed in [True, 'True', 'true', 'T', 't']:
			executed = True
		elif executed in [False, 'False', 'false', 'F', 'f']:
			excuted = False
		else: executed = None
		min_date = self.request.get('min_date')
		try:
			min_date = reverse_date_handler(min_date)
		except:
			min_date = None
		n = self.request.get('n')
		n = int(n) if n.isdigit() else 10
		s = self.request.get('s')
		s = int(s) if s.isdigit() else 0
		# query Cmd
		cmds = Cmd.get(master_id = master_id,
			           slave_id = slave_id,
			           executed = executed,
			           min_date = min_date,
			           n = n,
			           s = s)
		cmds = [c.make_dict() for c in cmds]
		self.write_json({'success':True,
			             'msg':'Cmd query successful!',
			             'cmds':cmds})


# handling file transfers
class UploadFile(UploadHandler):
	"""File Upload Handler"""
	def get(self):
		upload_url = self.create_upload_url(self.request.path)
		self.write_json({'upload_url':upload_url})

	def post(self):
		user_type = self.request.get('user_type')
		master_id = self.request.get('master_id')
		master_id = int(master_id) if master_id.isdigit() else 1
		master = Master.by_id(master_id)
		if not master:
			self.write_json({'success':False, 'msg':'master not exist'})
			return
		slave_id = self.request.get('slave_id')
		slave_id = int(slave_id) if slave_id.isdigit() else 0
		if slave_id:
			slave = Slave.by_id(slave_id)
			if not slave:
				self.write_json({'success':False, 'msg':'slave not exist'})
				return
		else: slave = None
		cmd_id = self.request.get('cmd_id')
		cmd_id = int(cmd_id) if cmd_id.isdigit() else 1
		cmd = Cmd.by_id(cmd_id)
		key = self.request.get('key')
		if user_type == 'master':
			user_id = self.request.get('user_id')
			master = Master.validate(master_id, user_id, key)
			if not master:
				self.write_json({'success':False, 'msg':'invalid master data'})
				return
			if cmd and not (cmd.master_id == master_id):
				self.write_json({'success':False, 'msg':'master not owner of cmd'})
				return
			if slave and (slave.master_id != master_id):
				self.write_json({'success':False, 'msg':'not authorized'})
				return
		elif user_type == 'slave':
			if (not slave) or (not Slave.validate(slave_id, str(master_id), key)):
				self.write_json({'success':False, 'msg':'invalid slave data'})
				return
			if not cmd:
				self.write_json({'success':False, 'msg':'cmd not exist'})
				return
		else:
			self.write_json({'success':False, 'msg':'invalid user_type'})
			return
		try:
			uploaded_file = self.get_uploads()[0]
			file_key = uploaded_file.key()
			file_info = self.get_info(file_key)
			file_name = file_info.filename
			file_size = file_info.size
			content_type = file_info.content_type
			f = ChFile.add_file(user_type,
							    master_id,
							    slave_id,
							    cmd_id,
							    file_key,
							    file_name,
						        file_size,
					     	    content_type)
			f.put()
			self.write_json({'success' : True,
				             'msg' : 'file uploaded!',
				             'file_id' : f.key.id()})
		except:
			self.write('upload failed!')

class ViewFile(MainHandler):
	"""File Info Viewer Handler"""
	def post(self, fid):
		user_type = self.request.get('user_type')
		master_id = self.request.get('master_id')
		master_id = int(master_id) if master_id.isdigit() else 1
		master = Master.by_id(master_id)
		if not master:
			self.write_json({'success':False, 'msg':'master not exist'})
			return
		slave_id = self.request.get('slave_id')
		slave_id = int(slave_id) if slave_id.isdigit() else 0
		if slave_id:
			slave = Slave.by_id(slave_id)
			if not slave:
				self.write_json({'success':False, 'msg':'slave not exist'})
				return
		else: slave = None
		key = self.request.get('key')
		if user_type == 'master':
			user_id = self.request.get('user_id')
			master = Master.validate(master_id, user_id, key)
			if not master:
				self.write_json({'success':False, 'msg':'invalid master data'})
				return
		elif user_type == 'slave':
			if (not slave) or (not Slave.validate(slave_id, str(master_id), key)):
				self.write_json({'success':False, 'msg':'invalid slave data'})
				return
		else:
			self.write_json({'success':False, 'msg':'invalid user_type'})
			return
		try:
			f = ChFile.by_id(int(fid))
			self.write_json({'success' : True,
				             'msg' : 'file found!',
				             'file' : f.make_dict()})
		except:
			self.write_json({'success' : False,
				             'msg' : 'file not founf'})


class DownloadFile(DownloadHandler):
	"""Serve File Handler"""
	def post(self, fid):
		user_type = self.request.get('user_type')
		master_id = self.request.get('master_id')
		master_id = int(master_id) if master_id.isdigit() else 1
		master = Master.by_id(master_id)
		if not master:
			self.write_json({'success':False, 'msg':'master not exist'})
			return
		slave_id = self.request.get('slave_id')
		slave_id = int(slave_id) if slave_id.isdigit() else 0
		if slave_id:
			slave = Slave.by_id(slave_id)
			if not slave:
				self.write_json({'success':False, 'msg':'slave not exist'})
				return
		else: slave = None
		key = self.request.get('key')
		if user_type == 'master':
			user_id = self.request.get('user_id')
			master = Master.validate(master_id, user_id, key)
			if not master:
				self.write_json({'success':False, 'msg':'invalid master data'})
				return
		elif user_type == 'slave':
			if (not slave) or (not Slave.validate(slave_id, str(master_id), key)):
				self.write_json({'success':False, 'msg':'invalid slave data'})
				return
		else:
			self.write_json({'success':False, 'msg':'invalid user_type'})
			return
		try:
			f = ChFile.by_id(int(fid))
			self.send_blob(f.blob)
		except:
			self.write_json({'success' : False,
				             'msg' : 'file not founf'})