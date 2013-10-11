from google.appengine.ext import db

from user import User

class Visit(db.Model):
  visitor = db.ReferenceProperty(User)
  pub = db.ReferenceProperty(User)
  date = db.DateTimeProperty(required=True)