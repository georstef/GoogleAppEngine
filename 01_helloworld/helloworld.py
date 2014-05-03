from google.appengine.api import users
import webapp2


class MainPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('Hello, ' + user.nickname())
        else:
            # self.redirect(users.create_login_url(self.request.uri))
            self.redirect(users.create_login_url()) # same same but if 'http://www.google.com' it goes there


application = webapp2.WSGIApplication([('/', MainPage),], debug=True)
