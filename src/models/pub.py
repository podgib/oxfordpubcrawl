from google.appengine.ext import db

class Pub(db.Model):
  name = db.StringProperty(required=True)
  address = db.TextProperty(default=None)
  latitude = db.FloatProperty()
  longitude = db.FloatProperty()
  is_college = db.BooleanProperty(default=False)

  def distance(self, lat, long):
    if not self.latitude or not self.longitude:
      return 10**9
    return (self.latitude - lat)**2 + (self.longitude - long)**2

  def toDictionary(self):
    return {'name' : self.name, 'id' : self.key().id()}