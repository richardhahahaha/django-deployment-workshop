"""
The tutorial's fabfile.

This starts out pretty simple -- just automating deployment on a single
server with a few commands. Then it gets a bit more complex (a basic
provisioning example).
"""

import contextlib
from fabric.api import env, run, cd, sudo, put, require, settings, hide 
from fabric.contrib import project, files

# This is a bit more complicated than needed because I'm using Vagrant
# for the examples.
env.key_filename = '/usr/lib/ruby/gems/1.8/gems/vagrant-0.7.2/keys/vagrant.ppk'

env.roledefs = {
    'develop': ['vagrant@127.0.0.1:22'],
    'staging': ['vagrant@10.0.2.2:5522'],
    'production': ['vagrant@10.0.2.2:6622']
} 

def _config():
    env.root = "/home/%(user)s/myblog" % env

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
        
    put("mingus-config/local_settings.py",
        "%(root)s/django-mingus/mingus/local_settings.py" % env,
        use_sudo=True)
    put("mingus-config/mingus.wsgi", "%(root)s/mingus.wsgi" % env, use_sudo=True)
        
def update_dependencies():
    "Update Mingus' requirements remotely."
    put("mingus-config/requirements.txt", "%(root)s/requirements.txt" % env, use_sudo=True)
    sudo("%(root)s/bin/pip install -r %(root)s/requirements.txt" % env)
        
def reload():
    "Reload Apache to pick up new code changes."
    sudo("invoke-rc.d apache2 reload")

#
# OK, simple stuff done. Here's a more complex example: provisioning
# a server the simplistic way.
#

def setup():
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
    sudo("mkdir -p /home/%(user)s/static" % env)
    sudo("aptitude update")
    sudo("aptitude -y install git-core python-dev python-setuptools "
                              "postgresql-dev postgresql-client build-essential "
                              "libpq-dev subversion mercurial apache2 "
                              "binutils libgdal1-1.5.0 libgeos-dev "
                              "postgresql-8.4-postgis postgresql-server-dev-8.4 "
                              "libapache2-mod-wsgi")

    # Create the virtualenv.
    sudo("easy_install virtualenv")
    sudo("virtualenv /home/%(user)s/myblog" % env)
    sudo("/home/%(user)s/myblog/bin/pip install -U pip" % env)

    # Check out Mingus
    with cd("/home/%(user)s/myblog" % env):
        sudo("git clone git://github.com/montylounge/django-mingus.git")

    # Set up Apache
    with cd("/home/%(user)s/" % env):
        sudo("git clone git://github.com/fivethreeo/django-deployment-workshop.git")
    with cd("/etc/apache2"):
        sudo("rm -rf apache2.conf conf.d/ httpd.conf magic mods-* sites-* ports.conf")
        sudo("ln -s /home/%(user)s/django-deployment-workshop/apache/apache2.conf ." % env)
        sudo("ln -s /home/%(user)s/django-deployment-workshop/mingus-config/mingus.wsgi /home/%(user)s/mingus.wsgi" % env)
        sudo("mkdir -m777 -p /var/www/.python-eggs")
        
    # Now do the normal deploy.
    deploy()


def run_chef():
    _config()
    """
    Run Chef-solo on the remote server
    """
    project.rsync_project(local_dir='chef', remote_dir='/tmp', delete=True)
    sudo('rsync -ar --delete /tmp/chef/ /etc/chef/')
    sudo('chef-solo')
    
    
    
    
