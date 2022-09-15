
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

install_requires = [
    # --core
    "future",
    "python-dateutil",
    "shortid",
    "python-magic",
    "pyserial",
    "croniter",
    "dateparser",
    "pytz",
    "jsonschema",
    "multiping",
    "requests",
    "gevent",
    "jsonpath-rw", # flow
    "objectpath",
    "Jinja2",
    "zeroconf",
    "btlewrap",
    "psutil",
    "unidecode",

    # --webserver
    "Flask>=1.0.2",
    "flask-cors",
    "flask-compress",
    "flask_socketio==3.1.2",
    "python-socketio==4.6.0",
    "python-engineio==3.13.2",
    "PyJWT==1.7.1",
    "netaddr",
    "webargs==6.1.0",

    # --ssh
    "paramiko",

    # --mqtt
    "paho-mqtt",

    # --mihome
    "pyaes",

    # --denon
    "xmltodict",

    # --zigate
    "zigate",

    # --miflora
    "miflora",

    # --google
    "authlib",
    "google-api-python-client",
    "google-auth",

    # --spotipy
    "spotipy-homeassistant",

    # --orno
    "minimalmodbus",

    # --SomfyHomeAlarm
    "somfy-protect-api",
]

ble_require = [
    "bluepy", # on most Debian-based systems : sudo apt-get install libglib2.0-dev , see https://github.com/IanHarvey/bluepy
]

tests_require = [
    "pytest>=3.6",  # unit test
    "pytest-cov",
    "coveralls",
]

docs_require = [
    'sphinx',
    'm2r',
    "apispec==0.38.0",  # http api
]

extras_require = {
    "docs": docs_require,
    "tests": tests_require,
    "ble": ble_require,
}

setup(
    name=NAME,

    version='0.1.4',

    description='A home automation project',

    long_description=long_description,

    long_description_content_type='text/markdown',

    url='https://github.com/e-thing/ething',

    author='Adrien Mezerette',
    author_email='a.mezerette@gmail.com',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='home automation ething iot mysensors rflink zigate',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    include_package_data=True,

    install_requires=install_requires,

    extras_require=extras_require,

    # tests : cf. https://docs.pytest.org/en/latest/goodpractices.html
    setup_requires=["pytest-runner"],
    tests_require=tests_require,

    entry_points={
        'console_scripts': [
            'ething=ething.__main__:main',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/e-thing/ething/issues',
        'Source': 'https://github.com/e-thing/ething/',
    },
)
