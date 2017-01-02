"""
url mapping for file app a part of MeXelearn project.
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
_u = URLS_PREFIX + '/file' # you can add prefix for app ex. -u = URLS_PREFIX + '/page'
urls = [
   webapp2.Route(_u+'/upload', UploadFile, 'upload-file'),
   (_u+r'/view/([0-9]+)', ViewFile),
   (_u+r'/download/([0-9]+)', DownloadFile),
]

# rendring urls
#app = webapp2.WSGIApplication(urls,
#	config=INTERNATIONAL_CFG, debug=DEBUG)
