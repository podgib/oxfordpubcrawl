from google.appengine.api import memcache
from models.user import User
from models.visit import Visit

def get_user_counts():
  users = memcache.get('user-counts')
  if users:
    return users
  users = User.all().run()
  user_counts = []
  for u in users:
    count = Visit.all().ancestor(u).filter('visited =', True).count()
    user_counts.append({'name':u.name,'id':u.key().id(),'count':count})
  user_counts = sorted(user_counts, key=lambda c: -c['count'])
  memcache.set('user-counts', user_counts)
  return user_counts