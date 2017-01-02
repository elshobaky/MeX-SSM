"""
cmd file for Slave portion of MeXtriple project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""
import os
import sys
import subprocess as sp
import logging
import json
import requests
import urllib
import datetime
import re
from config import (SLAVE_ID, KEY, MASTER_ID, BASE_URL,
                    MIN_DATE, update_min_date)

def update_cmd(cmd_id, cmd_output):
    "sends cmd output"
    req_data = {'slave_id' : SLAVE_ID,
                'key' : KEY, 
                'master_id' : MASTER_ID,
                'cmd_id' : cmd_id,
                'cmd_output' : cmd_output}
    req_url = BASE_URL+'/cmd/%s/update'%cmd_id
    req = requests.post(req_url, req_data)
    if not req.status_code == 200:
        logging.error(req.reason)
        return False
    data =  json.loads(req.text)
    if not data['success']:
        logging.error('cmd update failed, msg: %s'%data['msg'])
        return
    logging.info('cmd %s updated'%cmd_id)
    return True

def get_cmd(cmd_id=None, executed=None, min_date=None, n=None, s=None):
    'gets cmd by id'
    req_data = {'user_type': 'slave',
                'slave_id' : SLAVE_ID,
                'key' : KEY, 
                'master_id' : MASTER_ID,
                'cmd_id' : cmd_id,
                'executed' : executed,
                'min_date' : min_date,
                'n' : n,
                's' : s}
    req_url = BASE_URL+'/cmd/get'
    req = requests.post(req_url, req_data)
    if not req.status_code == 200:
        logging.error(req.reason)
        return []
    data =  json.loads(req.text)
    if not data['success']:
        logging.error('cmd query failed, msg: %s'%data['msg'])
        return []
    return data['cmds']


class Cmd(object):
    """class for retrieving cmds from server , parsing and executing it
    """
    def __init__(self, cmd):
        self.cmd = cmd['cmd']
        self.cmd_id = cmd['id']

    def _parse(self):
        c = self.cmd.split()
        cmd_type = c[0]
        parsed_cmd = ' '.join(c[1:])
        return cmd_type, parsed_cmd

    def _shell_exec(self, parsed_cmd):
        #return os.popen(cmd).read()
        #proc = sp.Popen(parsed_cmd, stdout=sp.PIPE, shell=True)
        #(out, err) = proc.communicate()
        out, err = Bash().execute(parsed_cmd)
        return out, err

    def _file_cmd(self, parsed_cmd):
        split_cmd = parsed_cmd.split() 
        action = split_cmd[0]
        f = ' '.join(split_cmd[1:])
        #print parsed_cmd+'+'+action+'+'+f
        if action in ['upload', 'up', 'send']:
            return send_file(f, cmd_id=self.cmd_id)
        if action in ['download', 'down', 'receive']:
            return download_file(f, naming='')
        return '', 'Not supported file action'

    def _exec(self):
        cmd_type , parsed_cmd = self._parse()
        if cmd_type == 'shell':
            return self._shell_exec(parsed_cmd)
        elif cmd_type == 'file':
            return self._file_cmd(parsed_cmd)
        return 'ERROR', 'Not Supported Command.'

    def execute(self):
        out, err = self._exec()
        output = json.dumps([out, err])
        print ' - command (%s) executed'%self.cmd_id
        update_cmd(self.cmd_id, output)
        return output

class Bash(object):
    """creates a bash/terminal/cmd session"""
    def __init__(self):
        if os.name == 'nt':
            self.sys_bash = 'cmd'
        elif os.name == 'posix':
            self.sys_bash = '/bin/bash'
        self.proc = sp.Popen([self.sys_bash],
                              stdin=sp.PIPE,
                              stdout=sp.PIPE)

    def execute(self, cmd):
        logging.info('executing command (%s)'%cmd)
        return self.proc.communicate(cmd)

def exec_all():
    global MIN_DATE
    cmds = get_cmd(min_date=MIN_DATE)
    for c in cmds:
        cmd_obj = Cmd(c).execute()
    dates = [c['created'] for c in cmds]
    if dates:
        MIN_DATE = max(dates, key=reverse_date_handler)
        update_min_date(MIN_DATE)


#date_fmt = "%I:%M%p, %d. %B %Y"
date_fmt = '%Y-%m-%d %H:%M:%S:%f'
# parse DateTime Property
def date_handler(obj):
    return obj.strftime(date_fmt) if hasattr(obj, 'isoformat') else obj

# conver string (date_handler string) to datetime
def reverse_date_handler(s):
    return datetime.datetime.strptime(s, date_fmt)


# File transfer
def send_file(file_path, cmd_id=None):
    out, err = None, None
    req_data = {'user_type':'slave',
                'slave_id':SLAVE_ID,
                'key':KEY,
                'master_id':MASTER_ID,
                'cmd_id': cmd_id}
    req_url = BASE_URL+'/file/upload'
    get_url = urllib.urlopen(req_url).read()
    upload_url = json.loads(get_url)['upload_url']

    with open(file_path, 'rb') as my_file:
        req = requests.post(upload_url,
            files = {'file' : my_file},
            data = req_data)
    if not req.status_code == 200:
        logging.error(req.reason)
        err = req.reason
    data =  json.loads(req.text)
    if not data['success']:
        logging.error('send file failed, msg: %s'%data['msg'])
        err = data['msg']
    out = 'file uploaded , file_id = %s'%data['file_id']
    return out, err

def view_file(file_id):
    req_data = {'user_type':'slave',
                'slave_id':SLAVE_ID,
                'key':KEY,
                'master_id':MASTER_ID}
    req_url = BASE_URL+'/file/%s/view'%file_id
    req = requests.post(req_url, req_data)
    if not req.status_code == 200:
        logging.error(req.reason)
        return False
    data =  json.loads(req.text)
    if not data['success']:
        logging.error('view file failed, msg: %s'%data['msg'])
        return
    return data['file']


def download_file(file_id, naming='name+id'):
    out, err = None, None
    try:
        os.mkdir('Downloads')
    except Exception as e:
        #logging.error(e)
        pass
    file_info = view_file(file_id)
    if not file_info :
        return out, 'file not found!'
    if naming == 'name+id':
        file_name = '%s (%s)'%(file_info['name'], file_id)
    else:
        file_name = file_info['name']
    file_path = 'Downloads/%s'%file_name
    req_data = {'user_type':'slave',
                'slave_id':SLAVE_ID,
                'key':KEY,
                'master_id':MASTER_ID}
    req_url = BASE_URL+'/file/%s/download'%file_id
    req = requests.post(req_url, data=req_data, stream=True)
    if not req.status_code == 200:
        logging.error(req.reason)
        err = req.reason
    with open(file_path, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    out = 'file downloaded at (%s)'%file_path
    return out, err

def test():
    #execute('echo hello')
    #exec_all()
    #print send_file('main.py', cmd_id=4547580092481536)
    #print view_file(5743848743501824)
    print download_file(5743848743501824, naming='')
    print 'test done!'

if __name__ == '__main__':
    test()