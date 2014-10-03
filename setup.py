import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(here, 'README.rst')).read()
changes = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [

    # Pyramid
    'pyramid >=1.5, <1.6',
    'pyramid_mako',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'pyramid_beaker',
    'waitress',

    # Backend
    'sqlalchemy >=0.9, <0.10',
    'alembic >=0.6.2, <0.7',
    'celery >=3.1, <3.2',
    'transaction',
    'psycopg2',
    'zope.sqlalchemy',
    'redis',
    'hiredis',
    'dogpile.cache',
    'python3-memcached',
    'pytz',
    'IPy',
    'requests',

    # Frontend
    'isodate',
    'misaka',

    # Tests
    'nose',
    'coverage',
    'mock',

    # Python 3.2 compatible
    'MarkupSafe==0.15', # https://github.com/mitsuhiko/markupsafe/pull/13
    'wtforms==1.0.3', # https://bitbucket.org/simplecodes/wtforms/issue/153/

    ]

setup(name='fanboi2',
      version='0.8.3',
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
      fb2_celery = fanboi2.scripts.celery:main
      """,
      )
