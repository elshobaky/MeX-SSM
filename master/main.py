"""
main file for Master portion of MeXtriple project.
By : Mahmoud Elshobaky (mahmoud.elshobaky@gmail.com).
"""
import os
import sys
import logging
from cmd2 import Cmd 
import json
from config import config_logging, C
from master import validate_master
from slave import (create_slave, delete_slave,
                   validate_slave, send_cmd, get_cmd,
                   upload_file, view_file, download_file,
                   connect_to_slave, wait_for_cmd_out)


class MasterCmd(object, Cmd):
    """class for haldling command line interface"""
    def __init__(self):
        Cmd.__init__(self)
        self.intro = self.colorize(self.intro_msg, 'cyan')

    prompt = '(MeX-SSM-Master)$ '
    intro_msg = """Welcome to MeX-SSM-Master interactive shell.
    type help or ? to list commands."""

    slave_id = 0
    settable = Cmd.settable + '''slave_id id of the slave you wanna connect to'''

    def do_create_slave(self, line):
        "Create new slave"
        slave = create_slave()
        if slave:
            out =  'slave created with id (%s) '%slave['slave_id']
            out += 'slave data saved at (%s)'%slave['fn']
            print self.colorize(out, 'green')
        else:
            out = 'slav creation failed refer to logs for more info!'
            print self.colorize(out, 'red')

    def do_connect(self, slave_id):
        """connec to slave with the given id
        >>> set slave_id <slave_id>  >>> connect
        or >>> connect <slave_id>"""
        if not isinstance(self.slave_id, int):
            self.slave_id = int(self.slave_id)
        if (not self.slave_id) and (not slave_id):
            print '''please set a slave_id:
            set slave_id <id>'''
            return
        if slave_id:
            self.slave_id = slave_id
        if validate_slave(self.slave_id):
            print 'validating slave ...'
            SlaveCmd(slave_id=self.slave_id).cmdloop()
        else:
            print 'invalid slave id!'

    def do_upload(self, file_path):
        "uploads file to the server and prints out file_id"
        f = upload_file(file_path)
        if f :
            print self.colorize('file uploaded, file id = %s'%f, 'green')
        else:
            print self.colorize('file upload failed!', 'red')

    def do_view_file(self, file_id):
        "retrieves file info from the server and prints it out"
        f = view_file(file_id)
        if not f:
            print self.colorize('failed to retrieve file info', 'red')
        else :
            for k in f:
                print '%s : %s'%(self.colorize(k, 'blue'),
                                 self.colorize(str(f[k]), 'green'))

    def do_download(self, file_id):
        f = download_file(file_id)
        if not f:
            print self.colorize('failed to download file', 'red')
        else:
            print self.colorize('file saved at (%s)'%f, 'green')


    def do_shell(self, line):
        "Run a shell command"
        print "running shell command:", line
        output = os.popen(line).read()
        print output

    def do_EOF(self, line):
        return True


class SlaveCmd(object, Cmd):
    def __init__(self, slave_id):
        #super(self.__class__, self).__init__()
        Cmd.__init__(self)
        self.slave_id = slave_id
        self.prompt = '(slave-%s)$ '%slave_id
        self.intro = self.colorize(self.intro_msg, 'cyan')

    intro_msg = '''    usage : exec <command_type> <command>
    examples for supporteed command types : 
       - shell <command> : executes shell command on slave side
       - file upload <file_path> : uploads file located on given path on slave side
                                   and retuns fle id and url
       - file download <file_id> : downloads file with the given id to Downloads dir on slave side. 
    End with ``Ctrl-D`` (Unix) / ``Ctrl-Z`` (Windows)'''

    def do_exec(self, line):
        cmd_id = send_cmd(self.slave_id, line)['id']
        output = wait_for_cmd_out(cmd_id)
        #print C.OB+"(output) :"
        print self.colorize(" %s"%output[0], 'green')
        if output[1]:
            print self.colorize("(error)  : %s"%output[1], 'red')

    def do_shell(self, line):
        "Run a shell command"
        print "running shell command:", line
        output = os.popen(line).read()
        print output

    def do_EOF(self, line):
        return True

def test():
    #slave_id = create_slave()['slave_id']
    slave_id = 4785074604081152
    #validate_slave(slave_id)
    #print send_cmd(slave_id, "echo hellok")
    connect_to_slave(slave_id)

if __name__ == '__main__':
    config_logging()
    logging.info('validating master data ...')
    if not validate_master():
        sys.exit()
    if len(sys.argv) > 1:
        MasterCmd().onecmd(' '.join(sys.argv[1:]))
    else:
        MasterCmd().cmdloop()