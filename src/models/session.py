from google.appengine.ext import db
from google.appengine.api import memcache

class Session(db.Model):
  user_id=db.IntegerProperty()
  token=db.StringProperty()
  
  def save(self):
    self.put()
    memcache.set(self.token, self)
    
  def remove(self):
    memcache.delete(self.token)
    self.delete()
  
  @staticmethod
  def getSession(token):
    session = memcache.get(token)
    if session and not isinstance(session, Session):
      return None
    if session is None:
      session = Session.all().filter("token =", token).get()
      if session is not None:
        memcache.set(token, session)
    return session
    
class SignupSession(db.Model):
  token = db.StringProperty()
  fb_id=db.StringProperty()
  
  def save(self):
    self.put()
    memcache.set(self.token, self)
    
  def remove(self):
    memcache.delete(self.token)
    self.delete()
  
  @staticmethod
  def getSignupSession(token):
    if not token:
      return None
    session = memcache.get(token)
    if session and not isinstance(session, SignupSession):
      return None
    if session is None:
      session = Session.all().filter("token =", token).get()
      if session is not None:
        memcache.set(token, session)
    return session