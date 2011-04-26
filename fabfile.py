"""
The tutorial's fabfile.

This starts out pretty simple -- just automating deployment on a single
server with a few commands. Then it gets a bit more complex (a basic
provisioning example).
"""

import contextlib
from fabric.api import env, run, cd, sudo, put, require, settings, hide 
from fabric.contrib import project, files
import time

# This is a bit more complicated than needed because I'm using Vagrant
# for the examples.
env.key_filename = '/usr/lib/ruby/gems/1.8/gems/vagrant-0.7.3/keys/vagrant.ppk'

from fab_utils import _put_template
# import settings
from fab_settings import global_settings, group_settings, servers

# prepare settings
groupmapping = {}
roledefs = {}
for role, servers in servers.items():
    roledefs[role] = []
    for server in servers:
       roledefs[role].append(server[0])
       groupmapping[server[0]] = server[1]
       
env.roledefs = roledefs

def config():
    """ Utility: Setup settings """
    for key, setting in global_settings.items():
        env[key] = setting % env
    for key, setting in group_settings[groupmapping[env.host_string]].items():
        env[key] = setting % env

def manage(cmd):
    """  Utility: return manage.py oneliner """
    cmdstr = "/home/%(user)s/%(project_name)s/bin/python /home/%(user)s/%(project_name)s/django-carpool/carpool/manage.py %%s" % env
    return cmdstr % cmd
     
def python(cmd):
    """  Utility: return python one liner """
    cmdstr = "DJANGO_SETTINGS_MODULE=settings /home/%(user)s/%(project_name)s/bin/python -c \"import sys;sys.path.append('/home/%(user)s/%(project_name)s/django-carpool/');sys.path.append('/home/%(user)s/%(project_name)s/django-carpool/carpool/');%%s\"" % env
    return cmdstr % cmd
    
def deploy(first=False):
    """Full deploy: push, pip and reload."""
    push()
    update_dependencies()
    run(manage("collectstatic --noinput"))
    reload(first=first)

def push_project():
    """ Push out new code to the server """
    with settings(warn_only=True):
        with cd("/tmp/"):
            project.upload_project()
            run("rm -rf /home/%(user)s/%(project_name)s/django-carpool" % env)
            run("cp -rf apps/django-carpool /home/%(user)s/%(project_name)s/django-carpool" % env)
            
def push_django_settings():
    _put_template("config/local_settings.py",
        "%(root)s/django-carpool/carpool/local_settings.py" % env, env)
               
def push_wsgi():
    _put_template("config/app.wsgi", "%(wsgipath)s" % env, env, use_sudo=True)

def push():
    push_project()
    push_django_settings()
    if not hasattr(env, 'use_nginx'):
        push_wsgi()

def update_dependencies():    
    """ Update requirements remotely """
    put("config/requirements.txt", "%(root)s/requirements.txt" % env)
    run("%(root)s/bin/pip install -r %(root)s/requirements.txt" % env)
        
def reload(first=False):
    """ Reload webserver/webapp """
    if hasattr(env, 'use_nginx'):
        if first==True:
            run("bash /home/%(user)s/%(project_name)s/bin/django_gunicorn start" % env)
        else:
            sudo("kill -QUIT `cat %(nginx_pidfile)s`" % env)
            run("bash /home/%(user)s/%(project_name)s/bin/django_gunicorn restart" % env)
        sudo("%(nginx_bin)s" % env)
    else:
        "Reload Apache to pick up new code changes."
        sudo("invoke-rc.d apache2 reload")

# OK, simple stuff done. Here's a more complex example: provisioning
# a server the simplistic way.

def patch_django():
    put("googlemapsv3.diff", "%(root)s/googlemapsv3.diff" % env)
    run("cd %(root)s/src/django && patch -p0 < %(root)s/googlemapsv3.diff" % env)


def setup_all():
    """ Setup all parts on one single server adds a fully running setup if run with -w """
    setup_webserver()
    setup_webapp()
    update_dependencies()
    push()
    setup_dbserver()
    configure_db()
    deploy(first=True)
    syncdb()
    add_site()
    add_superuser()

def setup_dbserver():
    """ Setup database server with postgis_template db """
    sudo("aptitude update")
    sudo("aptitude -y install git-core "
                              "build-essential "
                              "libpq-dev subversion mercurial "
                              "binutils proj gdal-bin libgeos-dev "
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
    """
    Set up (bootstrap) a new server.
    
    This essentially does all the tasks in the script done by hand in one
    fell swoop. In the real world this might not be the best way of doing
    this -- consider, for example, what the various creation of directories,
    git repos, etc. will do if those things already exist. However, it's
    a useful example of a more complex Fabric operation.
    """
    if hasattr(env, 'use_nginx'):
        server_req = "nginx"
    else:
        server_req = "apache2 libapache2-mod-wsgi"
    # Initial setup and package install.
    sudo("aptitude update")
    sudo("aptitude -y install git-core python-dev python-setuptools "
                              "postgresql-dev postgresql-client build-essential "
                              "libpq-dev subversion mercurial "
                              "binutils proj gdal-bin %s "
                              "python-pip" % server_req)
    if hasattr(env, 'use_nginx'):
        _put_template("nginx/nginx_webserver.conf", "%(nginx_confdir)snginx.conf" % env, env, use_sudo=True)
        sudo("mkdir -p %(nginx_confdir)ssites-enabled" % env)
    else:
        with cd("/etc/apache2"):
            sudo("rm -rf apache2.conf conf.d/ httpd.conf magic mods-* sites-* ports.conf")
        _put_template("apache/apache2.conf", "/etc/apache2/apache2.conf", env, use_sudo=True)
        sudo("mkdir -m777 -p /var/www/.python-eggs")
        sudo("mkdir -p /etc/apache2/sites-enabled" % env)
 
def setup_webapp():
    """ Setup virtualenv/startup scripts/configs for webapp """
    sudo("pip install -U virtualenv")
    run("virtualenv /home/%(user)s/%(project_name)s --distribute" % env)
    run("mkdir -p /home/%(user)s/%(project_name)s" % env)
    run("mkdir -p /home/%(user)s/static" % env)
    if hasattr(env, 'use_nginx'):
        _put_template("nginx/nginx_webapp.conf", "%(nginx_confdir)ssites-enabled/%(project_name)s.conf" % env, env, use_sudo=True)
        _put_template("config/django_gunicorn", "/home/%(user)s/%(project_name)s/bin/django_gunicorn" % env, env)
        run("chmod gu+rx /home/%(user)s/%(project_name)s/bin/django_gunicorn" % env)
    else:
        _put_template("apache/site.conf", "/etc/apache2/sites-enabled/%(project_name)s.conf" % env, env, use_sudo=True)

def add_postgis_db():
    """ Add the postgis_template db """
    put("create_template_postgis-debian.sh", "/home/%(user)s/create_template_postgis-debian.sh" % env)
    sudo("su postgres -c 'bash /home/%(user)s/create_template_postgis-debian.sh'" % env)
 
def add_db(dbname, owner, template=''):
    """ Add database: add_db:dbname,owner,<template> """
    if template:
        template = ' TEMPLATE %s' % template
    sudo('psql -c "CREATE DATABASE %s%s ENCODING \'unicode\' OWNER %s" -d postgres -U %s' % (dbname, template, owner, env.postgres_user or 'postgres'))

def add_dbuser(user, passwd):
    """ Add database user: add_dbuser:user,password """
    sudo('psql -c "CREATE USER %s WITH NOCREATEDB NOCREATEUSER PASSWORD \'%s\'" -d postgres -U %s' % (user, passwd, env.postgres_user or 'postgres'))
    
def configure_db():
    """ Set up webapps database """
    add_dbuser(env.db_user, env.db_password)
    add_db(env.db_name, env.db_user, 'template_postgis')
    add_srs()
    
def syncdb():
    """ Run syncdb """
    run(manage("syncdb --noinput"))

def migrate():
    """ Run migrate """
    run(manage("migrate"))
    
def add_srs():
    """ Add google srs """
    run(python("from django.contrib.gis.utils import add_srs_entry;add_srs_entry(900913)"))
    
def add_site():
    """ Add example django site """
    run(python("from django.contrib.sites.models import Site;Site.objects.create(domain='example.com', name='example')"))
    
def add_superuser():
    """ Add django superuser """
    run(python("from django.contrib.auth.models import User;User.objects.create_superuser('carpool', 'testuser@test.com', 'carpool')"))
