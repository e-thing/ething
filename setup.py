
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import os
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

NAME = 'ething'

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

requires = [
    # --core
    "future",
    "python-dateutil",
    "pillow", # used for thumbnail
    "shortid",
    "python-magic",
    "pyserial",
    "croniter",
    "dateparser",
    "pytz",
    "jsonschema",
    "multiping",
    "requests",
    "eventlet",

    # --db
    #"pymongo==3.5.1",
    #"unqlite",

    # --webserver
    "Flask",
    "flask-cors",
    "flask-compress",
    "flask_socketio",
    "PyJWT",
    "netaddr",
    "webargs",

    # --ssh
    "paramiko",

    # --mqtt
    "paho-mqtt",
    "jsonpath-rw",

    # --mihome
    "pyaes",

    # --denon
    "xmltodict",
]

if os.name != "nt":
    requires.append("bluepy")

setup(
    name=NAME,

    version='0.1.2',

    description='A home automation project',

    long_description=long_description,

    long_description_content_type='text/markdown',

    url='https://github.com/e-thing/ething',

    author='Adrien Mezerette',
    author_email='a.mezerette@gmail.com',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='home automation ething iot mysensors rflink zigate',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    include_package_data=True,

    install_requires=requires,

    extras_require={
        "dev": [
            "pytest",  # unit test
            "apispec==0.38.0",  # http api
            "Jinja2",  # http api
        ]
    },

    entry_points={
        'console_scripts': [
            'ething=ething.main:main',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/e-thing/ething/issues',
        'Source': 'https://github.com/e-thing/ething/',
    },
)
