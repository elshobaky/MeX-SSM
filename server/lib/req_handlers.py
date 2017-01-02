
from mx.handlers import MainHandler

# handler for changing app language
class Locale(MainHandler):
    """
    handles requests to change LOCALE or language for internationalization.
    """
    def get(self):
        locale = self.request.get('locale')
        if not locale :
          locale = LOCALE
        locale = locale[:2].lower()+'_'+locale[-2:].upper()
        if self.switch_locale(locale):
            if self.local_user and self.local_user.locale != locale:
                u = LocalUser.by_id(self.local_user.key.id())
                u.locale = locale
                u.put()
            self.write_json({'done':True})
        else:
            self.write_json({'done':False})


# home page handler
class MainPage(MainHandler):
    def get(self):
        self.render('home.html')

    def post(self):
        pw = self.request.get('pw')
        
