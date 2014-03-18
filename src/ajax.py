from google.appengine.api import memcache
import webapp2
import json

from models.pub import *
from models.visit import Visit
from models.user import *

class SetVisitHandler(webapp2.RequestHandler):
  def post(self):
    user = get_current_user()
    if not user and False:
      return self.redirect('/')
    pub_id = self.request.get('pub_id')
    pub = Pub.get_by_id(int(pub_id))

    visit = Visit.all().ancestor(user).filter('pub =', pub).get()

    visited = bool(self.request.get('visited'))
    visit.visited = visited
    visit.put()
    memcache.delete('visited-' + str(user.key().id()))
    memcache.delete('not-visited-' + str(user.key().id()))
    memcache.delete('user-counts')

class ClosestHandler(webapp2.RequestHandler):
  def get(self):
    user = get_current_user()
    lat=float(self.request.get('lat'))
    long=float(self.request.get('long'))
    if self.request.get('show-colleges'):
      if not user.show_colleges:
        memcache.delete('not-visited-' + str(user.key().id()))
        user.show_colleges = True
        user.put()
    elif user.show_colleges:
      memcache.delete('not-visited-' + str(user.key().id()))
      user.show_colleges = False
      user.put()
    if self.request.get('hide-visited'):
      if not user.hide_visited:
        user.hide_visited = True
        user.put()
    elif user.hide_visited:
      user.hide_visited = False
      user.put()

    if user and user.hide_visited:
      visits = memcache.get('not-visited-' + str(user.key().id()))
      if not visits:
        visits = Visit.all().ancestor(user).filter('visited =', False).fetch(500)
        visits = sorted(visits, key = lambda v: v.pub.name.lower())
        memcache.set('not-visited-' + str(user.key().id()), visits)
      if user.show_colleges:
        pubs = [v.pub for v in visits]
      else:
        pubs = [v.pub for v in visits if not v.pub.is_college]
      pubs = sorted(pubs, key=lambda p: p.distance(lat, long))[0:20]
      pubs = [pub.toDictionary() for pub in pubs]
    else:
      pubs = memcache.get('all-pubs-list')
      if not pubs:
        pubs = Pub.all().fetch(500)
        pubs = sorted(pubs, key = lambda p: p.name.lower())
        memcache.set('all-pubs-list', pubs)
      if user and not user.show_colleges:
        pubs = [p for p in pubs if not p.is_college]
      pubs = sorted(pubs, key=lambda p: p.distance(lat, long))[0:20]
      pubs = [p.toDictionary() for p in pubs]

    self.response.out.write(json.dumps(pubs))


app = webapp2.WSGIApplication([
  ('/ajax/visitpub',SetVisitHandler),
  ('/ajax/nearby', ClosestHandler)],debug=True)
