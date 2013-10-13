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
    if user:
      visits = memcache.get('not-visited-' + str(user.key().id()))
      if not visits:
        visits = Visit.all().ancestor(user).filter('visited =', False).fetch(500)
        visits = sorted(visits, key = lambda v: v.pub.name.lower())
        memcache.set('not-visited-' + str(user.key().id()), visits)
      visits = sorted(visits, key=lambda v: v.pub.distance(lat, long))[0:10]
      pubs = [v.pub.toDictionary() for v in visits]
    else:
      pubs = memcache.get('all-pubs-list')
      if not pubs:
        pubs = Pub.all().fetch(500)
        pubs = sorted(pubs, key = lambda p: p.name.lower())
        memcache.set('all-pubs-list', pubs)
      pubs = sorted(pubs, key=lambda p: p.distance(lat, long))[0:10]
      pubs = [p.toDictionary() for p in pubs]

    self.response.out.write(json.dumps(pubs))


app = webapp2.WSGIApplication([
  ('/ajax/visitpub',SetVisitHandler),
  ('/ajax/nearby', ClosestHandler)],debug=True)