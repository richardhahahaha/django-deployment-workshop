
global_settings = {
    'project_name': 'carpool',
    'root': '/home/%(user)s/%(project_name)s',
    'extra_settings': '',
    'db_user': 'carpool',
    'db_password': 'carpool',
    'db_name': 'carpool',
    'db_host': 'localhost',
    'servername': 'carpool.com',
    'postgres_user': 'postgres'
}

group_settings = {
    'vagrant_apache': {
        'wsgipath': '/home/%(user)s/%(project_name)s.wsgi',
        'wsgi_user': '%(user)s',
        'wsgi_group': 'www-data',
        'apache_pid_file': '/var/run/apache2.pid',
        'apache_run_user': 'www-data',
        'apache_run_group': 'www-data'
    },
    'vagrant_nginx': {
        'use_nginx': 'true',
        'nginx_user': 'www-data',
        'gunicorn_host': '127.0.0.1',
        'gunicorn_port': '8001',
        'extra_paths': '/home/%(user)s/%(project_name)s/django-carpool:/home/%(user)s/%(project_name)s/django-carpool/carpool/',
        'nginx_confdir': '/etc/nginx/',
        'nginx_pidfile': '/var/run/nginx.pid',
        'nginx_bin': '/usr/sbin/nginx'
    },
    'bsd': {
        'servername': 'carpool.cylon.no',
        'postgres_user': 'pgsql',
        'extra_settings': 'GEOS_LIBRARY_PATH=\'/opt/lib/libgeos_c.so.7\'',
        'use_nginx': 'true',
        'gunicorn_host': '127.0.0.1',
        'gunicorn_port': '8050',
        'extra_paths': '/home/%(user)s/%(project_name)s/django-carpool:/home/%(user)s/%(project_name)s/django-carpool/carpool/',
        'nginx_confdir': '/usr/local/nginx/conf/',
        'nginx_pidfile': '/usr/local/nginx/logs/nginx.pid',
        'nginx_bin': '/usr/local/nginx/sbin/nginx'
    }  
}

servers = {
# 'role', [
#     ['me@server:port', 'settings_group']
# ],
    'develop': [['vagrant@127.0.0.1:22', 'vagrant_nginx']],
    'staging': [['vagrant@10.0.2.2:5522', 'vagrant_apache']],
    'production': [
        # ['vagrant@10.0.2.2:6622', 'vagrant_apache'],
        ['carpool@mainframe.cylon.no', 'bsd']
    ]
}