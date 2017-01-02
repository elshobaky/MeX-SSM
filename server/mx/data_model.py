import json, random, hashlib, datetime
from string import letters
# importing google ndb datastor api
from google.appengine.ext import ndb

# Generate Parent ndb Key
def generate_key(name , group = 'default'):
    return ndb.Key(name, group)

#date_fmt = "%I:%M%p, %d. %B %Y"
date_fmt = '%Y-%m-%d %H:%M:%S:%f'
# parse DateTime Property
def date_handler(obj):
    return obj.strftime(date_fmt) if hasattr(obj, 'isoformat') else obj

# conver string (date_handler string) to datetime
def reverse_date_handler(s):
    return datetime.datetime.strptime(s, date_fmt)

# password hashing and validation
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(email, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(email + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(email, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(email, password, salt)

#Base Class for ndb DataStore
class BaseNDB(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, uid, group='default'):
        return cls.get_by_id(uid, parent = generate_key(cls.own_key_name,group=group))

    def make_dict(cls,include=None, exclude=None):
        if cls.dict_exclude and not exclude: exclude=cls.dict_exclude
        if cls.dict_include and not include: include=cls.dict_include
        dic = cls.to_dict(include=include, exclude=exclude)
        dic['id'] = cls.key.id()
        return dic

    def make_json(cls,include=None, exclude=None):
        js = cls.make_dict(include=include, exclude=exclude)
        return json.dumps(js,default=date_handler)

    def delete(cls):
        cls.key.delete()


class RandomIndexedModel(BaseNDB):
    """Abstracts how we do randomness in the other models."""
    random_index = ndb.FloatProperty('ri')
     
    @classmethod
    def random(cls, count=10, exclude=None, ancestor=None, filters=None):
        exclude = exclude or []
        filters = filters or []
        # Get the count requested plus the excluded size and programatically
        # remove the exclude list and return exactly the count requested.
        extra_count = count+len(exclude)
        query = cls.query(ancestor=ancestor) if ancestor else cls.query()
        # If any filters is passed add it to the query.
        for query_filter in filters:
            query = query.filter(query_filter)
         
        entities = query.filter(
            cls.random_index >= random.random()).fetch(extra_count)
         
        # If that fetch got less than count, get entities from the top of the list.
        if not entities or len(entities) < extra_count:
            entities = query.order(cls.random_index).fetch(extra_count)
         
        # Remove exclude and return exact count.
        entities = list(entity for entity in entities if not entity.key in exclude)
        return entities[:count]
     
    def _pre_put_hook(self):
        self.random_index = random.random()       