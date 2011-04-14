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
from tempfile import NamedTemporaryFile

env.project_name = 'myblog'

# This is a bit more complicated than needed because I'm using Vagrant
# for the examples.
env.key_filename = '/usr/lib/ruby/gems/1.8/gems/vagrant-0.7.2/keys/vagrant.ppk'

env.roledefs = {
    'develop': ['vagrant@127.0.0.1:22'],
    'staging': ['vagrant@10.0.2.2:5522'],
    'production': ['vagrant@10.0.2.2:6622']
} 


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


def _put_template(localpath, remotepath, templatevars, **kwargs):
    template = open(localpath).read()
    output = str(template) % templatevars
    tmpfile = NamedTemporaryFile(delete=False)
    tmpfile.write(output)
    tmpfile.close()
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
    env.servername = 'blog.com'
    
    
 
def deploy():
    _config()
    "Full deploy: push, buildout, and reload."
    push()
    update_dependencies()
    reload()
    
def push():
    "Push out new code to the server."
    with cd("%(root)s/django-mingus" % env):
        sudo("git pull")
        
    _put_template("config/local_settings.py",
        "%(root)s/django-mingus/mingus/local_settings.py" % env, env,
        use_sudo=True)
    _put_template("config/app.wsgi", "%(wsgipath)s" % env, env, use_sudo=True)
        
def update_dependencies():
    "Update Mingus' requirements remotely."
    put("config/requirements.txt", "%(root)s/requirements.txt" % env, use_sudo=True)
    sudo("%(root)s/bin/pip install -r %(root)s/requirements.txt" % env)
        
def reload():
    "Reload Apache to pick up new code changes."
    sudo("invoke-rc.d apache2 reload")

#
# OK, simple stuff done. Here's a more complex example: provisioning
# a server the simplistic way.
#

def setup_all():
    setup_webserver()
    setup_dbserver()
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
    sudo("chown -R postgres:postgres /etc/postgresql/8.4/main")    
    sudo("invoke-rc.d postgresql-8.4 restart")
    
    configure_db()

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
    sudo apt-get install build-essential python-dev python-setuptools python-pip ruby git-core
    sudo pip install fabric
    sudo gem install vagrant
    """
    # Initial setup and package install.
    sudo("aptitude update")
    sudo("aptitude -y install git-core python-dev python-setuptools "
                              "postgresql-dev postgresql-client build-essential "
                              "libpq-dev subversion mercurial apache2 "
                              "binutils libgdal1-1.5.0 "
                              "libapache2-mod-wsgi")

    with cd("/etc/apache2"):
        sudo("rm -rf apache2.conf conf.d/ httpd.conf magic mods-* sites-* ports.conf")
    _put_template("apache/apache2.conf", "/etc/apache2/apache2.conf", env, use_sudo=True)
    sudo("mkdir -m777 -p /var/www/.python-eggs")
    setup_webapp()
    
def setup_webapp():
    _config()
    # Create the virtualenv.
    sudo("easy_install virtualenv")
    run("virtualenv /home/%(user)s/%(project_name)s" % env)
    run("/home/%(user)s/%(project_name)s/bin/pip install -U pip" % env)

    # Check out Mingus
    with cd("/home/%(user)s/%(project_name)s" % env):
        run("git clone git://github.com/montylounge/django-mingus.git")

    run("mkdir -p /home/%(user)s/static" % env)
    sudo("mkdir -p /etc/apache2/sites-enabled" % env)
    
    _put_template("apache/site.conf", "/etc/apache2/sites-enabled/%(project_name)s.conf" % env, env, use_sudo=True)
    run('ln -s /home/%(user)s/%(project_name)s/django-mingus/mingus/media/mingus /home/%(user)s/static/mingus' % env)
    run('ln -s /home/%(user)s/%(project_name)s/lib/python2.6/site-packages/django/contrib/admin/media /home/%(user)s/static/admin_media' % env)
    # Now do the normal deploy.
    deploy()
    
    
def add_db(dbname, owner, template=''):
    if template:
        template = ' TEMPLATE %s'
    sudo('psql -c "CREATE DATABASE %s %s ENCODING \'unicode\' OWNER %s" -d postgres -U postgres' % (dbname, template, owner))
    
def configure_db():
    _config()                            
    add_dbuser('mingus', 'mingus')
    add_db('mingus', 'mingus')

def add_dbuser(user, passwd):
    sudo('psql -c "CREATE USER %s WITH NOCREATEDB NOCREATEUSER PASSWORD \'%s\'" -d postgres -U postgres' % (user, passwd))

def syncdb():
    _config()
    run("/home/%(user)s/%(project_name)s/bin/python /home/%(user)s/%(project_name)s/django-mingus/mingus/manage.py syncdb --noinput" % env)

def migrate():
    _config()
    run("/home/%(user)s/%(project_name)s/bin/python /home/%(user)s/%(project_name)s/django-mingus/mingus/manage.py migrate" % env)
    
def add_site():
    _config()                            
    run("DJANGO_SETTINGS_MODULE=settings /home/%(user)s/%(project_name)s/bin/python -c \"import sys;sys.path.append('/home/%(user)s/%(project_name)s/django-mingus/mingus');from django.contrib.sites.models import Site;Site.objects.create(domain='example.com', name='example')\"" % env)
    
def add_superuser():
    _config()                            
    run("DJANGO_SETTINGS_MODULE=settings /home/%(user)s/%(project_name)s/bin/python -c \"import sys;sys.path.append('/home/%(user)s/%(project_name)s/django-mingus/mingus');from django.contrib.auth.models import User;User.objects.create_superuser('mingus', 'test@test.com', 'mingus')\"" % env)



   