from google.appengine.ext import db
from google.appengine.api import users

class User(db.Model):
  name = db.StringProperty(required=True)
  fb_id = db.StringProperty()
  google_user = db.UserProperty()
  
def get_current_user():
  gu = users.get_current_user()
  if not gu:
    return None
  user = User.all().filter('google_user =',gu).get()
  if not user:
    user = User(name='a user', google_user=gu)
    user.put()
  return user
  