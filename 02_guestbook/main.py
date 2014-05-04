#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import urllib
from google.appengine.api import users
from google.appengine.ext import ndb
import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
    

MAIN_PAGE_FOOTER_TEMPLATE = """
    <form action="/sign?%s" method="post">
      <div><textarea name="content" rows="3" cols="60"></textarea></div>
      <div><input type="submit" value="Sign Guestbook"></div>
    </form>

    <hr>

    <form>Guestbook name:
      <input value="%s" name="guestbook_name">
      <input type="submit" value="switch">
    </form>

    <a href="%s">%s</a>

  </body>
</html>
"""

DEFAULT_GUESTBOOK_NAME = 'put your name here'


def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    # constructs a Datastore key for a Guestbook entity with guestbook_name
    return ndb.Key('Guestbook', guestbook_name)
    
    
class Greeting(ndb.Model):
    # create the entity Greeting
    author = ndb.UserProperty()  # there is a user type!!! with nickname() and stuff
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    
    
class MainHandler(webapp2.RequestHandler):
    def get(self):
        # self.response.write('<html><body>')
        guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
        
        greetings_query = Greeting.query(ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)
        
        # for greeting in greetings:
        #     if greeting.author:
        #        self.response.write('<b>%s - %s</b> wrote:' % 
        #                             (greeting.key, greeting.author.nickname()))
        #     else:
        #         self.response.write('An anonymous wrote this:')
        #     self.response.write('<blockquote>%s - %s</blockquote>' % 
        #                         (greeting.key, cgi.escape(greeting.content)))
        
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        # sign_query_params = urllib.urlencode({'guestbook_name': guestbook_name})
        # self.response.write(MAIN_PAGE_FOOTER_TEMPLATE % 
        #                     (sign_query_params, cgi.escape(guestbook_name), url, url_linktext))
        
        template_values = {
            'greetings': greetings,
            'guestbook_name': guestbook_name,
            'url': url,
            'url_linktext': url_linktext}
         
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        

class Guestbook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))
        
        if users.get_current_user():
            greeting.author = users.get_current_user()
        
        greeting.content = self.request.get('content')
        greeting.put()  # it's like save/commit/post etc
        
        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?'+urllib.urlencode(query_params))
    

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/sign', Guestbook)
], debug=True)
