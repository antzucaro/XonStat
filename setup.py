from setuptools import setup, find_packages

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'repoze.tm2>=1.0b1',
    'zope.sqlalchemy',
    'WebError',
    'webhelpers',
    'psycopg2',
    'pyramid_beaker',
    'pyramid_mako',
    'waitress',
]

setup(
    name='XonStat',
    version='1.0',
    description='XonStat',
    long_description='XonStat: The statistics web application for Xonotic',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Ant Zucaro',
    author_email='azucaro@gmail.com',
    url='http://stats.xonotic.org',
    keywords='web wsgi pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = xonstat:main',
        ],
    },
)
