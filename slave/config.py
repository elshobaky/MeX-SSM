"""
config file for Slave portion of MeXtriple project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""
import json
import sys
import logging

#load slave info
with open('slave_data.json', 'r') as slave:
    slave = json.loads(slave.read())
    SLAVE_ID = slave['slave_id']
    KEY = slave['slave_key']
    MASTER_ID = slave['master_id']
# base channel url
BASE_URL = 'http://localhost:8080/ch'

# min date (last date of latest executed command)
with open('config.json', 'r') as config:
    config = json.loads(config.read())
    MIN_DATE = config['min_date']

def update_min_date(min_date):
    with open('config.json', 'r') as config_file:
        config = json.loads(config_file.read())
        config['min_date'] = min_date
    with open('config.json', 'w') as config_file:
        config_file.write(json.dumps(config))
    global MIN_DATE
    MIN_DATE = min_date
    return MIN_DATE


# configuring logging
def config_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)