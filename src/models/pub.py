from google.appengine.ext import db

class Pub(db.Model):
  name = db.StringProperty(required=True)
  address = db.TextProperty(default=None)