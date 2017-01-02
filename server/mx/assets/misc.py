
import os, hashlib, hmac, datetime, logging, sys, json, re, random
from string import letters, digits
# import app settings
from settings import SECRET_KEY

# secret key for cookies
secret = SECRET_KEY
# functions used for making, storing, checking cookies
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

def cookies_expiry_date():
    expires = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    return expires.strftime("%a, %d %b %Y %H:%M:%S GMT")

#################################################
# Functions used frequently for DataModels file #
# rendering query object as json
#date_fmt = "%I:%M%p, %d. %B %Y"
date_fmt = '%Y-%m-%d %H:%M:%S:%f'
# parse DateTime Property
def date_handler(obj):
    return obj.strftime(date_fmt) if hasattr(obj, 'isoformat') else obj

# conver string (date_handler string) to datetime
def reverse_date_handler(s):
    return datetime.datetime.strptime(s, date_fmt)

def gql_json_parser(query_obj):
    if type(query_obj) is list:
        res = [k.make_dict() for k in query_obj]
    else:
        res = query_obj.to_dict()
    return json.dumps(res,default=date_handler)

def class_json_parser(class_object):
    return json.dumps(class_object, default=lambda o: o.__dict__)

# hashing user passowrd
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

#################################################

# checking json data for api requests
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False
    return True

# authentication handling generating keys and hashes
# this temporary implementation until providing more secure one

def make_key(length = 255):
    return ''.join(random.choice(letters+digits) for x in xrange(length))

def make_key_hash(user, key, salt=None):
    if not salt:
        salt = make_salt(length=10)
    h = hashlib.sha256(user + key + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_key(user, key, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(user, key, salt)