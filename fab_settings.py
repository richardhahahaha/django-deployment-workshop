
global_settings = {
    'project_name': 'carpool',
    'root': "/home/%(user)s/%(project_name)s",
    'wsgipath': "/home/%(user)s/%(project_name)s.wsgi",
    'wsgi_user': "%(user)s",
    'extra_settings': ''
}

group_settings = {
    'vagrant': {
        'wsgi_group': 'www-data',
        'apache_pid_file': '/var/run/apache2.pid',
        'apache_run_user': 'www-data',
        'apache_run_group': 'www-data',
        'servername': 'carpool.com',
        'db_user':  "carpool",
        'db_password': "carpool",
        'db_name': "carpool",
        'db_host': "localhost"
    },
    'bsd': {
        'wsgi_group': 'www',
        'servername': 'carpool.cylon.no',
        'db_user':  "carpool",
        'db_password': "carpool",
        'db_name': "carpool",
        'db_host': "localhost",
        'postgres_user': 'pgsql',
        'extra_settings': 'GEOS_LIBRARY_PATH=\'/opt/lib/libgeos_c.so.7\'',
        'use_nginx': 'true',
        'gunicorn_host': '127.0.0.1',
        'gunicorn_port': '8050',
        'extra_paths': '/home/%(user)s/%(project_name)s/django-carpool:/home/%(user)s/%(project_name)s/django-carpool/carpool/'
    }  
}

servers = {
# 'role', [
#     ['me@server:port', 'settings_group']
# ],
    'develop': [['vagrant@127.0.0.1:22', 'vagrant']],
    'staging': [['vagrant@10.0.2.2:5522', 'vagrant']],
    'production': [
        ['vagrant@10.0.2.2:6622', 'vagrant'],
        ['carpool@mainframe.cylon.no', 'bsd']
    ]
}