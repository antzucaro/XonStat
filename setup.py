import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'repoze.tm2>=1.0b1', # default_commit_veto
    'zope.sqlalchemy',
    'WebError',
    'pyramid-jinja2',
    'sqlahelper',
    'webhelpers',
    'psycopg2',
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup(name='XonStat',
      version='0.0',
      description='XonStat',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='xonstat',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = xonstat:main
      """,
      paster_plugins=['pyramid'],
      )

