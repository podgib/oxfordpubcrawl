#!/usr/bin/env python

import webapp2
import jinja2
import os

from models.pub import *

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class PubsHandler(webapp2.RequestHandler):
  def get(self):
    pubs = Pub.all().run()
    values = {'pubs' : pubs}
    template = jinja_environment.get_template('templates/pubs.html')
    self.response.out.write(template.render(values))
    
    
class PubHandler(webapp2.RequestHandler):
  def get(self, pub_id):
    pub = Pub.get_by_id(int(id))
    self.response.out.write(pub.name)
    
    
app = webapp2.WSGIApplication([
  ('/',PubsHandler),
  ('/pubs',PubsHandler),
  webapp2.Route('/pub/<id>',handler=PubHandler)],debug=True)