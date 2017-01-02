"""
master file for Master portion of MeXtriple project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""
import os
import json
import logging
import requests
import urllib
import time
from config import MASTER_ID, MASTER_KEY, USER_ID, BASE_URL, C

def create_slave():
    "creates new slave and saves data to json file"
    req_data = {'master_id':MASTER_ID, 'key':MASTER_KEY, 'user_id':USER_ID}
    req_url = BASE_URL+'/slave/new'
    req = requests.post(req_url, req_data)
    if not req.status_code == 200:
        logging.error(req.reason)
        return False
    slave_data = json.loads(req.text)
    if not slave_data['success']:
        logging.error('new slave creation failed, msg: '%slave_data['msg'])
        return False
    slave_fn = 'slaves/slave_%s_data.json'%slave_data['slave_id']
    with open(slave_fn, 'w') as slave_f:
        del slave_data['success']
        del slave_data['msg']
        slave_f.write(json.dumps(slave_data))
    logging.info('slave created! data saved at "%s"'%slave_fn)
    slave_data['fn'] = slave_fn
    return slave_data

def delete_slave(slave_id):
    "deletes slave with the given id"
    req_data = {'master_id':MASTER_ID, 'key':MASTER_KEY, 'user_id':USER_ID}
    req_url = BASE_URL+'/slave/%s/delete'%slave_id
    req = requests.post(req_url, req_data)
    if not req.status_code == 200:
        logging.error(req.reason)
        return False
    data =  json.loads(req.text)
    if not data['success']:
        logging.error('slave deletion failed, msg: %s'%data['msg'])
        return
    slave_fn = 'slaves/slave_%s_data.json'%slave_id
    os.remove(slave_fn)
    logging.info('slave deleted successfully!')
    return True

def validate_slave(slave_id):
    "validates slave data"
    slave_fn = 'slaves/slave_%s_data.json'%slave_id
    with open(slave_fn, 'r') as slave_f:
        slave_data = json.loads(slave_f.read())

    req_data = {'slave_id':slave_data['slave_id'], 'key':slave_data['slave_key'], 'master_id':slave_data['master_id']}
    req_url = BASE_URL+'/slave/%s/validate'%slave_id
    req = requests.post(req_url, req_data)
    if not req.status_code == 200:
        logging.error(req.reason)
        return False
    data =  json.loads(req.text)
    if not data['success']:
        logging.error('slave validation failed, msg: %s'%data['msg'])
        return
    logging.info('slave %s validated'%slave_id)
    return True

def send_cmd(slave_id, cmd):
    req_data = {'master_id':MASTER_ID,
                'key':MASTER_KEY, 
                'user_id':USER_ID,
                'slave_id':slave_id,
                'cmd': cmd}
    req_url = BASE_URL+'/cmd/add'
    req = requests.post(req_url, req_data)
    if not req.status_code == 200:
        logging.error(req.reason)
        return False
    data =  json.loads(req.text)
    return data['cmd']

def get_cmd(cmd_id=None, slave_id=None, executed=None, min_date=None, n=None, s=None):
    'gets cmd by id'
    req_data = {'user_type': 'master',
                'master_id' : MASTER_ID,
                'key' : MASTER_KEY,
                'user_id':USER_ID, 
                'slave_id' : slave_id,
                'cmd_id' : cmd_id,
                'executed' : executed,
                'min_date' : min_date,
                'n' : n,
                's' : s}
    req_url = BASE_URL+'/cmd/get'
    req = requests.post(req_url, req_data)
    if not req.status_code == 200:
        logging.error(req.reason)
        return False
    data =  json.loads(req.text)
    if not data['success']:
        logging.error('cmd query failed, msg: %s'%data['msg'])
        return
    return data['cmds']


# File transfer
def upload_file(file_path, slave_id=None, cmd_id=None):
    req_data = {'user_type':'master',
                'master_id':MASTER_ID,
                'key':MASTER_KEY, 
                'user_id':USER_ID,
                'slave_id':slave_id,
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
        return False
    data =  json.loads(req.text)
    if not data['success']:
        logging.error('send file failed, msg: %s'%data['msg'])
        return
    return data['file_id']

def view_file(file_id):
    req_data = {'user_type':'master',
                'master_id':MASTER_ID,
                'key':MASTER_KEY, 
                'user_id':USER_ID}
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


def download_file(file_id, naming=''):
    try:
        os.mkdir('Downloads')
    except Exception as e:
        #logging.error(e)
        pass
    file_info = view_file(file_id)
    if not file_info :
        return
    if naming == 'name+id':
        file_name = '%s (%s)'%(file_info['name'], file_id)
    else:
        file_name = file_info['name']
    file_path = 'Downloads/%s'%file_name
    req_data = {'user_type':'master',
                'master_id':MASTER_ID,
                'key':MASTER_KEY, 
                'user_id':USER_ID}
    req_url = BASE_URL+'/file/%s/download'%file_id
    req = requests.post(req_url, data=req_data, stream=True)
    if not req.status_code == 200:
        logging.error(req.reason)
        return False
    with open(file_path, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return file_path



# connect to slave (send comands and wait for response)
def wait_for_cmd_out(cmd_id):
    output = None
    stop = False
    start = time.time()
    while not output:
        cmd = get_cmd(cmd_id)[0]
        output = cmd['output']
        if not output and ((time.time()-start)>180):
            output = json.dumps(["ERROR TIME OUT !","ERROR TIME OUT !"])
            break
        time.sleep(0.5)
    return json.loads(output)

def connect_to_slave(slave_id):
    print 'validating slave ....'
    if not validate_slave(slave_id):
        sys.exit()
    while True:
        cmd = raw_input(C.H + 'slave (%s) >>> '%slave_id + C.E)
        cmd_id = send_cmd(slave_id, cmd)['id']
        output = wait_for_cmd_out(cmd_id)
        #print C.OB+"(output) :"
        print C.OG +" %s"%output[0]
        if output[1]:
            print (C.F+"(error)  :"+C.F+" %s"%output[1])



def test():
    #print send_file('main.py')
    #print view_file(5814217487679488)
    #print download_file(5814217487679488)
    print 'test done!'


if __name__ == '__main__':
    test()