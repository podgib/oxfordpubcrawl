from google.appengine.ext import db
from google.appengine.api import users
import webapp2
from session import Session

DEV_USERS = False

class User(db.Model):
  name = db.StringProperty(required=True)
  fb_id = db.StringProperty()
  google_user = db.UserProperty()
  email = db.EmailProperty()
  
def get_current_user():
  token = get_token()
  if token:
    session = Session.getSession(token)
    if session:
      return User.get_by_id(session.user_id)
  elif DEV_USERS:
    dev_user = users.get_current_user()
    if dev_user:
      return User.all().filter('google_user =', dev_user).get()
  return None


def get_token():
  request = webapp2.get_request()
  token = request.cookies.get("session")
  return token
  