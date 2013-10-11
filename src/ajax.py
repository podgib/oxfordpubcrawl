from google.appengine.api import memcache
import webapp2

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

app = webapp2.WSGIApplication([
  ('/ajax/visitpub',SetVisitHandler)],debug=True)