"""
url mapping for MelshoX project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""

# import app engine frameworks
import webapp2
from webapp2_extras import routes
# import app settings
from settings import *

#import project modules /apps and request handlers
from req_handlers import MainPage, Locale
# Mapping
_u = URLS_PREFIX
urls = [
    webapp2.Route(_u+'/', MainPage, 'home-page'),
    webapp2.Route(_u+'/switch-lang', Locale, 'language-switsh'),
]

# importing project apps urls
import user, files
# importing urls from each app
from user import urls as users_urls
from files import urls as files_urls
from channel import urls as ch_urls

urls += users_urls.urls
urls += files_urls.urls
urls += ch_urls.urls

# rendring urls
app = webapp2.WSGIApplication(urls,
	config=INTERNATIONAL_CFG, debug=DEBUG)
