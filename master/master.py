"""
master file for Master portion of MeXtriple project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""
import json
import logging
import requests
from config import MASTER_ID, MASTER_KEY, USER_ID, BASE_URL

def validate_master():
    "validates given master key and id with use id"
    req_data = {'user_id':USER_ID, 'key':MASTER_KEY}
    req_url = BASE_URL+'/master/%s/validate'%MASTER_ID
    req = requests.post(req_url, req_data)
    if not req.status_code == 200:
        logging.error(req.reason)
        return False
    valid = True if json.loads(req.text)['success'] else False
    if valid:
        logging.info('master data validated successfully!')
    else:
        logging.error('invalid master data!')
    return valid