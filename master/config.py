"""
config file for Master portion of MeXtriple project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""
import sys
import json
import logging

#load master and user info
with open('master_data.json', 'r') as master:
    master = json.loads(master.read())
    MASTER_ID = master['master_id']
    MASTER_KEY = master['master_key']
    USER_ID = master['user_id']
# base channel url
BASE_URL = 'http://localhost:8080/ch'

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


# colors definitions for CLI
class C:
    H = '\033[95m' # HEADER
    OB = '\033[94m' # OKBLUE
    OG = '\033[92m' # OKGREEN
    W = '\033[93m' # WARNING
    F = '\033[91m' # FAIL
    E = '\033[0m' # ENDC
    B = '\033[1m' # BOLD
    U = '\033[4m' # UNDERLINE