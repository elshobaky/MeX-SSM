"""
url mapping for channel app a part of MeXelearn project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""

# import app engine frameworks
import webapp2
from webapp2_extras import routes

# import app settings
from settings import URLS_PREFIX

#import project modules and request handlers
from request_handlers import *

#URL Mapping
# ex. [webapp2.Route(_u+'/signup', SignUp, 'user-signup'),]
_u = URLS_PREFIX + '/ch' # you can add prefix for app ex. -u = URLS_PREFIX + '/page'
urls = [
   webapp2.Route(_u+'/master/new', NewMaster, 'new-master'),
   (_u+'/master/([0-9]+)/delete', DeleteMaster),
   (_u+'/master/([0-9]+)/validate', ValidateMaster),
   webapp2.Route(_u+'/slave/new', NewSlave, 'new-slave'),
   (_u+'/slave/([0-9]+)/delete', DeleteSlave),
   (_u+'/slave/([0-9]+)/validate', ValidateSlave),
   webapp2.Route(_u+'/cmd/add', AddCmd, 'add-cmd'),
   (_u+'/cmd/([0-9]+)/update', UpdateCmd),
   webapp2.Route(_u+'/cmd/get', GetCmd, 'get-cmd'),
   webapp2.Route(_u+'/file/upload', UploadFile, 'ch-upload-file'),
   (_u+r'/file/([0-9]+)/view', ViewFile),
   (_u+r'/file/([0-9]+)/download', DownloadFile),
]

# rendring urls
#app = webapp2.WSGIApplication(urls,
#	config=INTERNATIONAL_CFG, debug=DEBUG)
