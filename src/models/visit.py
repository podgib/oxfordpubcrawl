from google.appengine.ext import db

from user import User
from pub import Pub

class Visit(db.Model):
  pub = db.ReferenceProperty(Pub)
  visited = db.BooleanProperty(default=False)
  date = db.DateTimeProperty()