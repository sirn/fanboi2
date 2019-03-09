import os
from setuptools import setup, find_packages


if os.path.exists("README.md"):
    with open("README.md", "rb") as readme:
        LONG_DESCRIPTION = readme.read().decode("utf-8")
else:
    LONG_DESCRIPTION = ""


setup(
    name="fanboi2",
    version="2019.02",
    description="Board engine behind fanboi.ch",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://git.sr.ht/~sirn/fanboi2",
    author="Kridsada Thanabulpong",
    author_email="sirn@ogsite.net",
    license="BSD-3-Clause",
    classifiers=[
        "Framework :: Pyramid",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet",
    ],
    keywords="web wsgi bfg pylons pyramid",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "MarkupSafe",
        "alembic >=0.9, <0.10",
        "argon2_cffi",
        "celery >=4.1, <4.2",
        "dogpile.cache >=0.6",
        "geoip2",
        "gunicorn",
        "hiredis >=0.2, <0.3",
        "isodate",
        "kombu >= 4.3, <4.4",
        "lark-parser >=0.6, <0.7",
        "misaka",
        "passlib",
        "psycopg2",
        "pyramid >=1.9, <1.10",
        "pyramid_debugtoolbar",
        "pyramid_mako",
        "pyramid_nacl_session",
        "pyramid_services",
        "pyramid_tm",
        "pytz",
        "redis >=2.0, <3.0",
        "requests",
        "sqlalchemy >=1.2, <1.3",
        "transaction",
        "wtforms >=2.1, <3.0",
        "zope.sqlalchemy",
    ],
    zip_safe=False,
    test_suite="fanboi2.tests",
    extras_require={
        "dev": ["honcho", "hupper", "pre-commit"],
        "test": ["nose", "coverage", "rednose"],
        "deploy": ["fabric", "patchwork", "invocations", "colorama"],
    },
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "fbctl = fanboi2.cmd.ctl:main",
            "fbcelery = fanboi2.cmd.celery:main",
            "fbdeploy = fanboi2.cmd.deploy:main",
        ]
    },
)
