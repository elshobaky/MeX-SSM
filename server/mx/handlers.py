"""
Frequently Used request handlers.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""

# import app engine frameworks
import webapp2, jinja2
# import app settings
from settings import *
# importing libs and modules for Intenationalization
from webapp2_extras import i18n
from webapp2_extras.i18n import gettext as _
# user login
from google.appengine.api import users
from user.data_models import LocalUser
# importing modules for handling file uploads
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
# session handler for flash messages
from webapp2_extras.sessions import SessionDict

from assets.misc import *
# get text for translations and internationalization
def t(text):
    return _(text)
# initialize jinja template envionment
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(TEMPLATE_DIR),
                               extensions=['jinja2.ext.i18n'],
                               autoescape = True)
jinja_env.install_gettext_translations(i18n)



# function used to prepare the template file
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


# main class used for handling requests
class MainHandler(webapp2.RequestHandler, SessionDict):
    """
    used for handlig requests and building responses
    using basic webapp2 requesthandler plus some helper functions:
     -- sending response options:
      - plain text response:
        self.write(text_response)
      - HTML response:
        self.render("path_to _html _file",**optional_kw_args_to_use_with_jinj2_templates)
      - JSON response:
        self.write_json(dict_or_json_object)
     -- dealing with cookies:
       - self.set_secure_cookie(name,value,remember=False)
       - self.read_secure_cookie(name)

    ready to use with user app
    """
    def write(self, *a, **kw):
        "function for sending string response to user"
        self.response.out.write(*a, **kw)

    # functions for building a response using template file
    def render_str(self, template, **params):
        params['user'] = self.local_user
        params['admin'] = self.admin
        params['author'] = self.author
        params['google_user'] = self.google_user
        params['locale'] = self.locale
        params['flashes'] = self.get_flashes()
        return render_str(template, **params)

    def render(self, template, **kw):
        "used to send a response using a template file"
        self.write(self.render_str(template, **kw))

    def write_json(self, data):
        "used to respond with json for ajax requests"
        self.response.headers['Content-Type'] = 'application/json'
        if type(data) is dict: data = json.dumps(data, default=date_handler)
        if is_json(data): self.write(data)

    def set_secure_cookie(self, name, val,remember=False):
        cookie_val = make_secure_val(val)
        if remember :
            expires = cookies_expiry_date()
            self.response.headers.add_header(
                'Set-Cookie',
                '%s=%s; Path=/; expires=%s' % (name, cookie_val,expires))
        else :
            self.response.headers.add_header(
                'Set-Cookie',
                '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def switch_locale(self, locale, remember=True):
        try:
            locale = str(locale)
            self.set_secure_cookie('locale', locale,remember=remember)
            return True
        except:
            return False

    def login(self, user, remember=False):
        self.set_secure_cookie('user_id', str(user.key.id()),remember=remember)

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def signup(self):
        role = 'u'
        if self.admin: role='admin'
        u = LocalUser.register(self.google_user.user_id(), self.google_user.email(), self.google_user.nickname(), role=role)
        u.put()
        self.login(u)
        self.add_flash(t('thanks! for signing up please, go to ') +\
                         '<a href="/user/profile">%s</a>'% t('your profile') +\
                         t(' to update your info'),'success')
        return u


    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        self.locale = self.read_secure_cookie('locale')
        if self.locale is None :
            self.locale = LOCALE
        self.local_user = None; self.admin = None; self.author = None
        # check if user logged in from cookies and grapping user entity from database
        uid = self.read_secure_cookie('user_id')
        if uid:
            self.local_user = LocalUser.by_id(int(uid))
        # check if user logged in with google account
        self.google_user = users.get_current_user()
        if self.google_user and self.local_user:
            # check if google_user matches the local_user
            if self.local_user.user_id != self.google_user.user_id():
                self.local_user.user_id = self.google_user.user_id()
                self.local_user.put()
            elif users.is_current_user_admin():
                if self.local_user.role != 'admin':
                    self.local_user.role = 'admin'
                    self.local_user.put()
                self.admin = self.author = self.local_user
        elif self.google_user:
            u = LocalUser.by_google_id(self.google_user.user_id())
            if u :
                self.login(u)
                self.local_user = u
                if u.role == 'admin':
                    self.admin = self.author = self.local_user
                if u.role == 'author':
                    self.author = self.local_user
            else:
                u = LocalUser.by_email(self.google_user.email())
                if u :
                    u.user_id = self.google_user.user_id()
                    u.put()
                else:
                    u = self.signup()
                    self.local_user = u
        if self.local_user:
            if self.locale != self.local_user.locale:
                self.switch_locale(self.local_user.locale)
                self.locale = self.local_user.locale
        self.user = self.local_user
        #self.locale = str(self.locale)
        i18n.get_i18n().set_locale(self.locale)


# handlers for file upload and download
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler, MainHandler):
    """UploadHandler containg main function to upload and download files"""
    def create_upload_url(self,url):
        return blobstore.create_upload_url(url)

    def get_info(self,value):
        return blobstore.BlobInfo.get(value)

class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler, MainHandler):
    def get_file(self,file_key):
        if blobstore.get(file_key):
            return True
        else:
            return False

    def send_file(self, file_key):
        if not self.get_file(file_key):
            self.error(404)
            self.write('file not found')
        else:
            self.send_blob(file_key)
