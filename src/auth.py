import base64
import json
import urllib
import datetime
import webapp2
import jinja2
import os

from google.appengine.api import users

from models.pub import *
from models.visit import Visit
from models.user import *
from models.session import *

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class LoginHandler(webapp2.RequestHandler):
  def get(self):
    if get_current_user():
      return self.redirect('/')
    template = jinja_environment.get_template('templates/login.html')
    values = {'login_url':users.create_login_url('/auth/devlogin'), 'show_dev_login':DEV_USERS}
    self.response.out.write(template.render(values))

class FbLoginHandler(webapp2.RequestHandler):
  def get(self):
    if get_current_user():
      return self.redirect('/')
    fbtoken=self.request.get('token')
    if not fbtoken:
      self.redirect("/")
      return
    profile=json.load(urllib.urlopen("https://graph.facebook.com/me?"+
      urllib.urlencode({'access_token': fbtoken})))
    fb_id=profile["id"]
    first_name=profile["first_name"]
    surname=profile["last_name"]
    user=User.all().filter("fb_id =",fb_id).get()

    if user:
      rand_string=base64.urlsafe_b64encode(os.urandom(32))
      session = Session()
      session.user_id = user.key().id()
      session.token = rand_string
      session.save()
      self.response.set_cookie("session",rand_string,expires=datetime.datetime.now()+datetime.timedelta(days=30));
      user.put()
      self.redirect("/")
      return
    else:
      session = SignupSession(fb_id=fb_id)
      session.token = base64.urlsafe_b64encode(os.urandom(32))
      session.save()
      template_values={'name':first_name + ' ' + surname,'session':session.token}
      template=jinja_environment.get_template('templates/signup.html')
      self.response.out.write(template.render(template_values))

class DevLoginHandler(webapp2.RequestHandler):
  def get(self):
    if not DEV_USERS:
      return self.redirect('/login')
    if get_current_user():
      return self.redirect('/')
    devuser = users.get_current_user()
    if not devuser:
      return self.redirect('/auth/login')
    user = User.all().filter('google_user =', devuser).get()
    if not user:
      template = jinja_environment.get_template('templates/signup.html')
      self.response.out.write(template.render({}))

class SignupHandler(webapp2.RequestHandler):
  def post(self):
    if get_current_user():
      return self.redirect('/')
    token = self.request.get('session')
    if token:
      session = SignupSession.getSignupSession(token)
      if not session:
        return self.redirect('/auth/login')
      fb_id = session.fb_id
      dev_user = None
    else:
      if not DEV_USERS:
        return self.redirect('/auth/login')
      fb_id = None
      dev_user = users.get_current_user()
      if not dev_user:
        return self.redirect('/auth/login')
    name = self.request.get('name')
    email = self.request.get('email')
    if not name or not email:
      template = jinja_environment.get_template('templates/signup.html')
      values = {'name':name,'email':email,'session':token,'errormsg':'Please supply a name and email address'}
      self.response.out.write(template.render(values))
      return
    user = User(name=name,email=email,google_user=dev_user,fb_id=fb_id)
    user.put()

    pubs = Pub.all().run()
    for pub in pubs:
      v = Visit(parent=user,pub=pub)
      v.put()

    rand_string=base64.urlsafe_b64encode(os.urandom(32))
    session = Session()
    session.user_id = user.key().id()
    session.token = rand_string
    session.save()
    self.response.set_cookie("session",rand_string,expires=datetime.datetime.now()+datetime.timedelta(days=30));
    self.redirect('/')

app = webapp2.WSGIApplication([
  ('/auth/login',LoginHandler),
  ('/auth/fblogin',FbLoginHandler),
  ('/auth/signup',SignupHandler),
  ('/auth/devlogin',DevLoginHandler)],debug=True)