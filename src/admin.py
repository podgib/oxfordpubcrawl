import os
import webapp2
import jinja2
from models.pub import Pub
from models.user import User
from models.visit import Visit

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class AddPubHandler(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('templates/add_pub.html')
    self.response.out.write(template.render({}))

  def post(self):
    name = self.request.get('name')
    p = Pub.all().filter('name =', name).get(keys_only=True)
    if p:
      self.response.out.write('already exists')
      return
    nlat = None
    nlong = None
    lat = self.request.get('lat')
    long = self.request.get('long')
    if lat:
      nlat = float(lat)
    if long:
      nlong = float(long)
    p = Pub(name=name, latitude=nlat, longitude=nlong)
    p.put()

    users = User.all().run()
    for u in users:
      v = Visit(parent=u, pub=p)
      v.put()
    self.response.out.write('added ' + name)

class CleanVisitsHandler(webapp2.RequestHandler):
  def get(self):
    visits = Visit.all().run()
    for v in visits:
      try:
        p = v.pub
      except:
        v.delete()

    self.response.out.write('success')

class CleanPubsHandler(webapp2.RequestHandler):
  def get(self):
    for p in Pub.all().run():
      if not p.latitude:
        p.delete()
    self.response.out.write('success')

class UpdateSchemaHandler(webapp2.RequestHandler):
  def get(self):
    users = User.all().run()
    for u in users:
      u.show_colleges = True
      u.hide_visited = True
      u.put()
    self.response.out.write('success')


app = webapp2.WSGIApplication([
  ('/admin/addpub',AddPubHandler),
  ('/admin/updateschema',UpdateSchemaHandler),
  ('/admin/cleanpubs',CleanPubsHandler),
  ('/admin/clean', CleanVisitsHandler)],debug=True)