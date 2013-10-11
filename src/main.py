#!/usr/bin/env python
from google.appengine.api import memcache

import webapp2
import jinja2
import os

from models.pub import *
from models.visit import Visit
from models.user import *

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class PubsHandler(webapp2.RequestHandler):
  def show_all_pubs(self):
    pubs = memcache.get('all-pubs-list')
    if not pubs:
      pubs = Pub.all().order('name').fetch(500)
      memcache.set('all-pubs-list', pubs)
    values = {'pubs' : pubs, 'logged_in' : False}
    template = jinja_environment.get_template('templates/pubs.html')
    self.response.out.write(template.render(values))

  def get(self):
    user = get_current_user()
    if not user:
      return self.show_all_pubs()
    visited = Visit.all().ancestor(user).filter('visited =', True).fetch(500)
    visited = sorted(visited, key = lambda v: v.pub.name.lower())
    not_visited = Visit.all().ancestor(user).filter('visited =',False).fetch(500)
    not_visited = sorted(not_visited, key = lambda v: v.pub.name.lower())
    values = {'visited' : visited, 'not_visited' : not_visited, 'logged_in' : True, 'own_page' : True}
    template = jinja_environment.get_template('templates/user_pubs.html')
    self.response.out.write(template.render(values)) 

class UserHandler(webapp2.RequestHandler):
  def get(self, user_id=None):
    current_user = get_current_user()
    user = None
    if user_id:
      user = User.get_by_id(int(user_id))
    elif current_user:
      return self.redirect('/profile/' + str(current_user.key().id()))
    if not user:
      return self.redirect('/')
    visits = db.GqlQuery('SELECT __key__ FROM Visit WHERE ANCESTOR IS :1 AND visited = :2', user, True).count()
    values = {'visits' : visits, 'user' : user, 'logged_in' : current_user is not None}
    template = jinja_environment.get_template('templates/user.html')
    self.response.out.write(template.render(values))

class VisitedHandler(webapp2.RequestHandler):
  def get(self, user_id=None):
    current_user = get_current_user()
    if user_id:
      user = User.get_by_id(int(user_id))
    else:
      user = current_user
    if not user:
      return self.redirect('/')
    visits = Visit.all().ancestor(user).filter('visited =', True).fetch(500)
    visits = sorted(visits, key = lambda v: v.pub.name.lower())
    values = {'visited' : visits, 'user' : user, 'logged_in' : current_user is not None, 'own_page' : user_id is None}
    template = jinja_environment.get_template('templates/user_pubs.html')
    self.response.out.write(template.render(values))

class NotVisitedHandler(webapp2.RequestHandler):
  def get(self, user_id=None):
    current_user = get_current_user()
    if user_id:
      user = User.get_by_id(int(user_id))
    else:
      user = current_user
    if not user:
      return self.redirect('/')
    visits = Visit.all().ancestor(user).filter('visited =', False).fetch(500)
    visits = sorted(visits, key = lambda v: v.pub.name.lower())
    values = {'not_visited' : visits, 'user' : user, 'logged_in' : current_user is not None}
    template = jinja_environment.get_template('templates/user_pubs.html')
    self.response.out.write(template.render(values))
    
    
class PubHandler(webapp2.RequestHandler):
  def get(self, pub_id):
    user = get_current_user()
    pub = Pub.get_by_id(int(pub_id))
    visit_count = db.GqlQuery('SELECT __key__ FROM Visit WHERE visited = :1 AND pub = :2', True, pub).count()
    values = {'pub' : pub, 'visit_count' : visit_count, 'user' : user}
    if user:
      visit = Visit.all().ancestor(user).filter('pub =', pub).get()
      values['visited'] = visit.visited
      values['logged_in'] = True

    template = jinja_environment.get_template('templates/pub.html')
    self.response.out.write(template.render(values))

class PubVisitsHandler(webapp2.RequestHandler):
  def get(self, pub_id):
    current_user = get_current_user()
    pub = Pub.get_by_id(int(pub_id))
    visits = Visit.all().filter('pub =', pub).filter('visited =', True).fetch(10000)
    visits = sorted(visits, key = lambda v: v.parent().name.lower())
    values = {'pub' : pub, 'visits' : visits, 'logged_in' : current_user is not None}
    template = jinja_environment.get_template('templates/visitors.html')
    self.response.out.write(template.render(values))

class LandingHandler(webapp2.RequestHandler):
  def get(self):
    if get_current_user():
      self.redirect('/profile')
    else:
      self.redirect('/pubs')
    
    
app = webapp2.WSGIApplication([
  ('/',LandingHandler),
  ('/pubs',PubsHandler),
  ('/visited', VisitedHandler),
  ('/notvisited', NotVisitedHandler),
  ('/user',UserHandler),
  ('/profile',UserHandler),
  webapp2.Route('/pub/<pub_id>/visitors', handler=PubVisitsHandler),
  webapp2.Route('/visited/<user_id>', handler=VisitedHandler),
  webapp2.Route('/user/<user_id>',handler=UserHandler),
  webapp2.Route('/profile/<user_id>',handler=UserHandler),
  webapp2.Route('/pub/<pub_id>',handler=PubHandler)],debug=True)