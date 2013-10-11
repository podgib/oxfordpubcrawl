#!/usr/bin/env python

import webapp2
import jinja2
import os

from models.pub import *
from models.visit import Visit
from models.user import *

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class PubsHandler(webapp2.RequestHandler):
  def show_all_pubs(self):
    pubs = Pub.all().run()
    values = {'pubs' : pubs, 'user' : user}
    template = jinja_environment.get_template('templates/pubs.html')
    self.response.out.write(template.render(values))

  def get(self):
    user = get_current_user()
    if not user:
      return self.show_all_pubs()
    visited = Visit.all().ancestor(user).filter('visited =', True).fetch(10)
    not_visited = Visit.all().ancestor(user).filter('visited =',False).fetch(10)
    values = {'visited' : visited, 'not_visited' : not_visited}
    template = jinja_environment.get_template('templates/user_pubs.html')
    self.response.out.write(template.render(values))  
    
    
class PubHandler(webapp2.RequestHandler):
  def get(self, pub_id):
    pub = Pub.get_by_id(int(pub_id))
    visits = db.GqlQuery('SELECT __key__ FROM Visit WHERE visited = :1 AND pub = :2', True, pub).count()
    self.response.out.write(pub.name)
    self.response.out.write(visits)

class LoginHandler(webapp2.RequestHandler):
  def get(self):
    self.redirect('/_ah/login')
    
    
app = webapp2.WSGIApplication([
  ('/',PubsHandler),
  ('/pubs',PubsHandler),
  ('/login',LoginHandler),
  webapp2.Route('/pub/<pub_id>',handler=PubHandler)],debug=True)