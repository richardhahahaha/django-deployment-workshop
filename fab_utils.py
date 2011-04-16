import os
from tempfile import NamedTemporaryFile as _NamedTemporaryFile
from fabric.api import env, run, cd, sudo, put, require, settings, hide 

def _render_template(localpath, templatevars):
    template = open(localpath).read()
    return str(template) % templatevars	

def _make_temp(data):
    tmpfile = _NamedTemporaryFile(delete=False)
    tmpfile.write(data)
    tmpfile.close()
    return tmpfile
            
def _make_template_temp(localpath, templatevars):
    return _make_temp(_render_template(localpath, templatevars))
    
def _put_template(localpath, remotepath, templatevars, **kwargs):
    tmpfile = _make_template_temp(localpath, templatevars)
    put(tmpfile.name, remotepath, **kwargs)
    os.unlink(tmpfile.name)
    
def _new_user(username, group='users', password=False):

    # Create the new admin user (default group=username); add to admin group
    sudo('adduser {username} --disabled-password --gecos ""'.format(
        username=username))
    sudo('adduser {username} {group}'.format(
        username=username,
        group=group))
        
    if password:
        # Set the password for the new admin user
        sudo('echo "{username}:{password}" | chpasswd'.format(
            username=admin_username,
            password=admin_password))    