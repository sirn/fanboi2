import os
from setuptools import setup, find_packages
from fanboi2 import __VERSION__

here = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(here, 'README.rst')).read()
changes = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'pyramid',
    'sqlalchemy',
    'transaction',
    'psycopg2',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'pyramid_zcml',
    'pyramid_jinja2',
    'pyramid_beaker',
    'zope.sqlalchemy',
    'waitress',
    'alembic',
    'wtforms',
    'webtest',
    'isodate',
    'pytz',
    'misaka',
    'redis',
    'hiredis',
    'IPy',
    'nose',
    'coverage',
    'requests',

    # Python 3.2 compatible
    'MarkupSafe==0.15', # https://github.com/mitsuhiko/markupsafe/pull/13
    'Jinja2==2.6',
    ]

setup(name='fanboi2',
      version=__VERSION__,
      description='fanboi2',
      long_description=readme + '\n\n' + changes,
      classifiers=[
        "programming language :: python",
        "programming language :: python :: 3",
        "framework :: pyramid",
        "topic :: internet :: www/http",
        "topic :: internet :: www/http :: wsgi :: application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='fanboi2',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = fanboi2:main
      [console_scripts]
      fb2_create_board = fanboi2.scripts.create_board:main
      fb2_update_board = fanboi2.scripts.update_board:main
      """,
      )
