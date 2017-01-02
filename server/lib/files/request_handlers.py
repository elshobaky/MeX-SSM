"""
Request handlers for file app a part of MeXelearn project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""
# importing frequently used handlers
from mx.handlers import MainHandler, UploadHandler, DownloadHandler, t
# Data Models
from data_models import *

class UploadFile(UploadHandler):
	"""File Upload Handler"""
	def get(self):
		if not self.admin:
			self.redirect_to('user-login',ref=self.request.path)
			return
		upload_url = self.create_upload_url(self.request.path)
		self.render('/file/upload-file.html', upload_url=upload_url)

	def post(self):
		if not self.admin:
			self.redirect_to('user-login',ref=self.request.path)
			return
		try:
			uploaded_file = self.get_uploads()[0]
			file_key = uploaded_file.key()
			file_info = self.get_info(file_key)
			file_name = file_info.filename
			file_size = file_info.size
			content_type = file_info.content_type
			f = File.add_file(self.local_user.key.id(),
				     self.local_user.nickname,
				     file_key,
				     file_name,
				     file_size,
				     content_type)
			f.put()
			self.redirect('/file/view/%s'%f.key.id())
		except:
			self.write('upload failed!')

class ViewFile(MainHandler):
	"""File Info Viewer Handler"""
	def get(self, fid):
		try:
			f = File.by_id(int(fid))
			self.write_json(f.make_dict())
		except:
			self.write('File Not Found')


class DownloadFile(DownloadHandler):
	"""Serve File Handler"""
	def get(self, fid):
		try:
			f = File.by_id(int(fid))
			self.send_blob(f.blob)
		except:
			self.write('File Not Found')
