Django Deployment Workshop
==========================

This is code and configuration for my Django Deployment Workshop.

Here you'll find example config used to set up an example deployment
environment for a Python WSGI stack, including:

* A Django site deployed with Pip_, Virtualenv_, and Fabric_.
* Apache/mod_wsgi_ and Gunicorn_ application servers.
* Nginx_ load balancers and media servers.
* Memcached_.
* PostgreSQL_ with `pgpool`_

.. _pip: http://pip.rtfd.org/
.. _virtualenv: http://virtualenv.rtfd.org/
.. _fabric: http://fabfile.org/
.. _mod_wsgi: http://modwsgi.org/
.. _nginx: http://wiki.nginx.org/
.. _memcached: http://memcached.org/
.. _postgresql: http://postgresql.org/
.. _pgpool: http://pgpool.projects.postgresql.org/
.. _gunicorn: http://gunicorn.org/

I've made comments and notes where possible, but it's entirely possible that
this won't make a whole lot of sense without actually taking the class. But
this is all BSD-licensed, so please feel free to use it as a starting point
for you own deployments.

The Django site used for the examples is Kevin Fricovsky's Mingus_, a blog
application built on a bunch existing reusable apps.

.. _mingus: https://github.com/montylounge/django-mingus

Getting the app running
=======================

Install putty_, msysgit_, virtualbox_, ruby_ (jruby_ on 64bit oses) and vagrant_.

.. _putty: http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html
.. _virtualbox: http://www.virtualbox.org/

.. _vagrant: http://vagrantup.com/

When installing msysgit_ add the context menu for "Git bash here".

.. _msysgit: http://code.google.com/p/msysgit/

After installing ruby_ or jruby_ and the devkit_ , open a cmd shell and do a (j)gem install vagrant


.. _jruby: http://www.jruby.org/
.. _devkit: http://rubyinstaller.org/add-ons/devkit/

Make a dir to check out the workshop. Eg. C:\\vagrant\\ right click the dir and "Git bash here".

    git clone https://github.com/fivethreeo/django-deployment-workshop.git

Close the git bash window. Hold shift and right clik the dir and "Open command window here".

    copy django-deployment-workshop\\vagrant\\Vagrantfile .

    vagrant up

Connect to 127.0.0.1:4422 using putty with the keyfile C:\Ruby192\lib\ruby\gems\1.9.1\gems\vagrant-0.7.2\keys\vagrant.ppk, depending on ruby_ version.

.. _ruby: http://www.ruby-lang.org/

In the terminal window (putty) do:

    cd /vagrant/django-deployment-workshop

    sudo bash bootstrap_dev.sh

    fab setup_all -R develop -p vagrant

Open a webbrowser to http://127.0.0.1:4480/admin/, login using user: mingus password: mingus

Further reading
===============

By my count this three-hour class covers about a dozen different pieces of
technology. Below are some links to documentation of these various bits. If
you read through all of it until you understand every command and
configuration option I've used, you'll be well on your way towards groking
this stuff. Good luck!

    * Ubuntu_.
    * git_ (also see the `git book`_).
    * Pip_.
    * Virtualenv_.
    * Django_; see particularly the `settings reference`_.
    * Apache_; the `directive quick reference`_ is especially useful.
    * mod_wsgi_:
        * `Django's mod_wsgi docs`_.
        * `mod_wsgi's Django docs`_.
    * Gunicorn_
    * `PostgreSQL docs`_, including:
        * `Server configuration`_ (``postgresql.conf``).
        * `Client authentication`_ (``pg_hba.conf``).
    * Fabric_.
    * Nginx_, specifically the upstream_ and proxy_ modules.
    * memcached_.
    * Django's `caching framework`_.
    * pgpool2_.
    
.. _ubuntu:
.. _git: http://git-scm.com/documentation
.. _`git book`: http://book.git-scm.com/
.. _django: http://docs.djangoproject.com/en/dev/
.. _`settings reference`: http://docs.djangoproject.com/en/dev/ref/settings/
.. _apache: http://httpd.apache.org/docs/2.2/
.. _`directive quick reference`: http://httpd.apache.org/docs/2.2/mod/quickreference.html
.. _`django's mod_wsgi docs`: http://docs.djangoproject.com/en/dev/howto/deployment/modwsgi/
.. _`mod_wsgi's Django docs`: http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango
.. _`postgresql docs`: http://www.postgresql.org/docs/current/static/
.. _`server configuration`: http://www.postgresql.org/docs/8.4/static/runtime-config.html
.. _`client authentication`: http://www.postgresql.org/docs/8.4/static/client-authentication.html
.. _upstream: http://wiki.nginx.org/NginxHttpUpstreamModule
.. _proxy: http://wiki.nginx.org/NginxHttpProxyModule
.. _`caching framework`: http://docs.djangoproject.com/en/dev/topics/cache/
.. _pgpool2: http://pgpool.projects.postgresql.org/pgpool-II/doc/pgpool-en.html
