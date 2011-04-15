"""
The tutorial's fabfile.

This starts out pretty simple -- just automating deployment on a single
server with a few commands. Then it gets a bit more complex (a basic
provisioning example).
"""

import contextlib
from fabric.api import env, run, cd, sudo, put, require, settings, hide 
from fabric.contrib import project, files
import os
import time
from tempfile import NamedTemporaryFile as _NamedTemporaryFile

env.project_name = 'carpool'

# This is a bit more complicated than needed because I'm using Vagrant
# for the examples.
env.key_filename = '/usr/lib/ruby/gems/1.8/gems/vagrant-0.7.2/keys/vagrant.ppk'

env.roledefs = {
    'develop': ['vagrant@127.0.0.1:22'],
    'staging': ['vagrant@10.0.2.2:5522'],
    'production': ['vagrant@10.0.2.2:6622']
} 

# utility functions
def _manage(cmd):
    cmdstr = "/home/%(user)s/%(project_name)s/bin/python /home/%(user)s/%(project_name)s/django-carpool/carpool/manage.py %%s" % env
    return cmdstr % cmd
     
def _python(cmd):
    cmdstr = "DJANGO_SETTINGS_MODULE=settings /home/%(user)s/%(project_name)s/bin/python -c \"import sys;sys.path.append('/home/%(user)s/%(project_name)s/django-carpool/');sys.path.append('/home/%(user)s/%(project_name)s/django-carpool/carpool/');%%s\"" % env
    return cmdstr % cmd
    
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
    
def _config():
    env.root = "/home/%(user)s/%(project_name)s" % env
    env.wsgipath = "/home/%(user)s/%(project_name)s.wsgi" % env
    env.wsgi_user = env.user
    env.wsgi_group = 'www-data'
    env.apache_pid_file = '/var/run/apache2.pid'
    env.apache_run_user = 'www-data'
    env.apache_run_group = 'www-data'
    env.servername = 'carpool.com'
    env.db_user =  "carpool"
    env.db_password = "carpool"
    env.db_name = "carpool"
    env.db_host = "localhost"
    
def deploy():
    _config()
    "Full deploy: push, buildout, and reload."
    push()
    update_dependencies()
    run(_manage("collectstatic --noinput"))
    reload()
    
def push():
    _config()
    "Push out new code to the server."
    #with cd("%(root)s/django-carpool" % env):
    #    sudo("git pull")
    # project.rsync_project("/home/%(user)s/%(project_name)s/django-carpool/" % env, "apps/django-carpool/", extra_opts="--password-file=rsync_pw")
    project.upload_project()
    run("rm -rf /home/%(user)s/%(project_name)s/django-carpool" % env)
    run("cp -rf apps/django-carpool /home/%(user)s/%(project_name)s/django-carpool" % env)
    _put_template("config/local_settings.py",
        "%(root)s/django-carpool/carpool/local_settings.py" % env, env,
        use_sudo=True)
    _put_template("config/app.wsgi", "%(wsgipath)s" % env, env, use_sudo=True)
        
def update_dependencies():
    _config()
    "Update Mingus' requirements remotely."
    put("config/requirements.txt", "%(root)s/requirements.txt" % env)
    run("%(root)s/bin/pip install -r %(root)s/requirements.txt" % env)
        
def reload():
    "Reload Apache to pick up new code changes."
    sudo("invoke-rc.d apache2 reload")

#
# OK, simple stuff done. Here's a more complex example: provisioning
# a server the simplistic way.
#

def setup_all():
    setup_webserver()
    setup_webapp()
    update_dependencies()
    setup_dbserver()
    configure_db()
    deploy()
    syncdb()
    add_site()
    add_superuser()
    
def setup_dbserver():
    _config()
    sudo("aptitude update")
    sudo("aptitude -y install git-core  "
                              "build-essential "
                              "libpq-dev subversion mercurial apache2 "
                              "binutils libgeos-dev "
                              "postgresql-8.4-postgis postgresql-server-dev-8.4")
    put("postgresql/pg_hba.conf",
        "/etc/postgresql/8.4/main/pg_hba.conf" % env,
        use_sudo=True)
    put("postgresql/postgresql.conf",
        "/etc/postgresql/8.4/main/postgresql.conf" % env,
        use_sudo=True)
    sudo("invoke-rc.d postgresql-8.4 restart")
    time.sleep(7)
    add_postgis_db()

def setup_webserver():
    _config()
    """
    Set up (bootstrap) a new server.
    
    This essentially does all the tasks in the script done by hand in one
    fell swoop. In the real world this might not be the best way of doing
    this -- consider, for example, what the various creation of directories,
    git repos, etc. will do if those things already exist. However, it's
    a useful example of a more complex Fabric operation.
    
    Dev setup:

    """
    # Initial setup and package install.
    sudo("aptitude update")
    sudo("aptitude -y install git-core python-dev python-setuptools "
                              "postgresql-dev postgresql-client build-essential "
                              "libpq-dev subversion mercurial apache2 "
                              "binutils gdal-bin "
                              "libapache2-mod-wsgi")

    with cd("/etc/apache2"):
        sudo("rm -rf apache2.conf conf.d/ httpd.conf magic mods-* sites-* ports.conf")
    _put_template("apache/apache2.conf", "/etc/apache2/apache2.conf", env, use_sudo=True)
    sudo("mkdir -m777 -p /var/www/.python-eggs")
    
def setup_webapp():
    _config()
    # Create the virtualenv.
    sudo("easy_install virtualenv")
    run("virtualenv /home/%(user)s/%(project_name)s" % env)
    run("/home/%(user)s/%(project_name)s/bin/pip install -U pip" % env)
    run("mkdir -p /home/%(user)s/%(project_name)s" % env)
    run("mkdir -p /home/%(user)s/static" % env)
    sudo("mkdir -p /etc/apache2/sites-enabled" % env)
    _put_template("apache/site.conf", "/etc/apache2/sites-enabled/%(project_name)s.conf" % env, env, use_sudo=True)

def add_postgis_db():
	put("create_template_postgis-debian.sh", "/home/%(user)s/create_template_postgis-debian.sh" % env)
	sudo("su postgres -c 'bash /home/%(user)s/create_template_postgis-debian.sh'" % env)
 
def _add_db(dbname, owner, template=''):
    if template:
        template = ' TEMPLATE %s' % template
    sudo('psql -c "CREATE DATABASE %s%s ENCODING \'unicode\' OWNER %s" -d postgres -U postgres' % (dbname, template, owner))

def _add_dbuser(user, passwd):
    sudo('psql -c "CREATE USER %s WITH NOCREATEDB NOCREATEUSER PASSWORD \'%s\'" -d postgres -U postgres' % (user, passwd))
    
def configure_db():
    _config()
    _add_dbuser(env.db_user, env.db_password)
    _add_db(env.db_name, env.db_user, 'template_postgis')
    add_srs()
    
def syncdb():
    _config()
    run(_manage("syncdb --noinput"))

def migrate():
    _config()
    run(_manage("migrate"))
    
def add_srs():
    _config()                            
    run(_python("from django.contrib.gis.utils import add_srs_entry;add_srs_entry(900913)"))
    
def add_site():
    _config()                            
    run(_python("from django.contrib.sites.models import Site;Site.objects.create(domain='example.com', name='example')"))
    
def add_superuser():
    _config()                            
    run(_python("from django.contrib.auth.models import User;User.objects.create_superuser('carpool', 'testuser@test.com', 'carpool')"))
