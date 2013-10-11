from google.appengine.ext import db

class User(db.Model):
  name = db.StringProperty(required=True)
  fb_id = db.StringProperty(required=True)