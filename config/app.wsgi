import os
import site
import sys

# Add the virtualenv packages to the site directory. This uses the technique
# described at http://code.google.com/p/modwsgi/wiki/VirtualEnvironments

# Remember original sys.path.
prev_sys_path = list(sys.path) 

# Add the virtualenv site-packages to the site packages
site.addsitedir('%(root)s/lib/python2.6/site-packages')

# Reorder sys.path so the new directories are at the front.
new_sys_path = [] 
for item in list(sys.path): 
    if item not in prev_sys_path: 
        new_sys_path.append(item) 
        sys.path.remove(item) 
sys.path[:0] = new_sys_path 

# Add the app code to the path
for pth in '%(extra_paths)s'.split(':'):
    sys.path.append(pth)

# Now do DJANGO_SETTINGS_MODULE and create the WSGI app.
os.environ['DJANGO_SETTINGS_MODULE'] = 'carpool.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

from paste.exceptions.errormiddleware import ErrorMiddleware
application = ErrorMiddleware(application, debug=True)






