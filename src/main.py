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
    values = {'pubs' : pubs, 'user' : None}
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

class UserHandler(webapp2.RequestHandler):
  def get(self, user_id=None):
    if user_id:
      user = User.get_by_id(int(user_id))
    else:
      user = get_current_user()
    visits = db.GqlQuery('SELECT __key__ FROM Visit WHERE ANCESTOR IS :1 AND visited = :2', user, True).count()
    values = {'visits' : visits, 'user' : user}
    template = jinja_environment.get_template('templates/user.html')
    self.response.out.write(template.render(values))
    
    
class PubHandler(webapp2.RequestHandler):
  def get(self, pub_id):
    user = get_current_user()
    pub = Pub.get_by_id(int(pub_id))
    visits = db.GqlQuery('SELECT __key__ FROM Visit WHERE visited = :1 AND pub = :2', True, pub).count()
    values = {'pub' : pub, 'visits' : visits, 'user' : user}
    if user:
      visit = Visit.all().ancestor(user).filter('pub =', pub).get()
      values['visited'] = visit.visited

    template = jinja_environment.get_template('templates/pub.html')
    self.response.out.write(template.render(values))

class LoginHandler(webapp2.RequestHandler):
  def get(self):
    self.redirect('/_ah/login')
    
    
app = webapp2.WSGIApplication([
  ('/',PubsHandler),
  ('/pubs',PubsHandler),
  ('/login',LoginHandler),
  ('/user',UserHandler),
  ('/profile',UserHandler),
  webapp2.Route('/user/<user_id>',handler=UserHandler),
  webapp2.Route('/profile/<user_id>',handler=UserHandler),
  webapp2.Route('/pub/<pub_id>',handler=PubHandler)],debug=True)