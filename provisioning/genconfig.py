import os
from jinja2 import Environment, FileSystemLoader

pvdir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.abspath(os.path.join(pvdir, os.path.pardir))
jinja_env = Environment(loader=FileSystemLoader(pvdir))

default_config = {
    'development': True,
    'db_user': 'fanboi2',
    'db_pass': 'fanboi2',
    'db_name': 'fanboi2',
    'csrf_secret': 'changeme',
    'session_secret': 'changeme',
    'timezone': 'Asia/Bangkok',

    # Path stubs.
    'base': basedir,
    'root': os.path.join(basedir, 'app'),

    # Ansible stubs.
    'ansible_default_ipv4': {'address': '127.0.0.1'},
}


def gen(source, dest):
    tmpl = jinja_env.get_template(source)
    output = tmpl.render(default_config)
    with open(os.path.join(basedir, dest), 'wb') as f:
        f.write(bytes(output.encode('utf-8')))
    print('%s written.' % dest)


if __name__ == '__main__':
    gen('files/srv/settings.ini.j2', 'settings.ini')
    gen('files/srv/alembic.ini.j2', 'alembic.ini')
