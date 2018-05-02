import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(here, 'README.rst')).read()
changes = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [

    # Pyramid
    'pyramid >=1.9, <1.10',
    'pyramid_nacl_session',
    'pyramid_debugtoolbar',
    'pyramid_mako',
    'pyramid_services',
    'pyramid_tm',
    'waitress',

    # Backend
    'alembic >=0.9, <0.10',
    'argon2_cffi',
    'celery >=4.1, <4.2',
    'coloredlogs',
    'dogpile.cache',
    'geoip2',
    'hiredis',
    'passlib',
    'psycopg2',
    'python3-memcached',
    'pytz',
    'redis',
    'requests',
    'sqlalchemy >=1.2, <1.3',
    'transaction',
    'zope.sqlalchemy',

    # Frontend
    'MarkupSafe',
    'isodate',
    'misaka',
    'wtforms',

    # Tests
    'coverage',
    'nose',
    'rednose',

    ]

setup(name='fanboi2',
      version='0.29.9',
      description='board engine behind fanboi.ch',
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
      test_suite='fanboi2.tests',
      install_requires=requires,
      entry_points="""
      [console_scripts]
      fbctl = fanboi2.cmd.ctl:main
      fbcelery = fanboi2.cmd.celery:main
      """)
