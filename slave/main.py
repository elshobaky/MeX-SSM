"""
main file for Slave portion of MeXtriple project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""
import logging
import os
import sys
import json
import requests
import time
from config import (SLAVE_ID, KEY, MASTER_ID,
                    BASE_URL, MIN_DATE,
                    update_min_date,
                    config_logging)
from cmds_handlers import get_cmd, update_cmd, exec_all

def validate_slave():
    "validates slave data"
    req_data = {'slave_id':SLAVE_ID, 'key':KEY, 'master_id':MASTER_ID}
    req_url = BASE_URL+'/slave/%s/validate'%SLAVE_ID
    req = requests.post(req_url, req_data)
    if not req.status_code == 200:
        logging.error(req.reason)
        return False
    data =  json.loads(req.text)
    if not data['success']:
        logging.error('slave validation failed, msg: %s'%data['msg'])
        return
    logging.info('slave %s validated'%SLAVE_ID)
    return True

def listen():
    print "listning ......."
    while True:
        exec_all()
        time.sleep(0.5)
        



def test():
    #cmd_id = 6368371348078592
    #MIN_DATE = update_min_date("0:59PM, 26. October 2015")
    #print get_cmd(min_date=MIN_DATE)
    exec_all()


if __name__ == '__main__':
    config_logging()
    logging.info('validating slave data ...')
    if not validate_slave():
        sys.exit()
    #test()
    listen()