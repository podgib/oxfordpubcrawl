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
    p = Pub(name=name)
    p.put()

    users = User.all().run()
    for u in users:
      v = Visit(parent=u, pub=p)
      v.put()
    self.response.out.write('added ' + name)


app = webapp2.WSGIApplication([
  ('/admin/addpub',AddPubHandler)],debug=True)