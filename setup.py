# coding: utf-8
from __future__ import print_function


from setuptools import setup, find_packages
from setuptools import Command
from setuptools.command.sdist import sdist
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from setuptools.command.bdist_egg import bdist_egg

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    bdist_wheel = None


# To use a consistent encoding
from codecs import open
import os
import sys
from subprocess import check_call, CalledProcessError, check_output
from os.path import join as pjoin
SEPARATORS = os.sep if os.altsep is None else os.sep + os.altsep
from collections import defaultdict
import shlex


NAME = 'ething'


here = os.path.abspath(os.path.dirname(__file__))
root = pjoin(here, NAME)
webui_root = pjoin(root, 'webui')
is_repo = os.path.exists(pjoin(here, '.git'))


with open(pjoin(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


exec(open(pjoin(here, NAME, 'version.py')).read())


# class BuildWebUI(Command):
#     """
#     Build the webui
#     """
#
#     description = 'build the webui'
#     user_options = []
#
#     node_modules = pjoin(webui_root, 'node_modules')
#     dist_dir = pjoin(webui_root, 'dist')
#     src_dir = pjoin(webui_root, 'src')
#
#     def initialize_options(self):
#         pass
#
#     def finalize_options(self):
#         pass
#
#     def run(self):
#
#         if not which('npm'):
#             print("ERROR: `{0}` unavailable. If you're running this command using sudo, make sure `{0}` is available to sudo.".format('npm'), file=sys.stderr)
#             return
#
#
#         # start build webui
#
#         if is_stale(self.dist_dir, self.src_dir):
#
#             print("webui build required.")
#
#             try:
#                 print("Installing webui build dependencies with npm. This may take a while...")
#
#                 run('npm install --only=dev', cwd=webui_root)
#
#                 print("Building webui. This may take a while...")
#
#                 run('npm run build', cwd=webui_root)
#
#             except CalledProcessError as e:
#                 print('ERROR: Failed to build the webui: %s'.format(e), file=sys.stderr)
#                 return
#
#         else :
#             print("no webui build required.")
#
#         # end build webui
#
#         print("Installing webui dependencies with npm. This may take a while...")
#
#         try:
#             run('npm install --only=prod', cwd=webui_root)
#         except CalledProcessError as e:
#             print('ERROR: Failed to install the webui: %s'.format(e), file=sys.stderr)
#             return
#
#
#
#         self.update_package_data()
#
#
#
#
#
#     def update_package_data(self):
#
#         package_data = self.distribution.package_data
#
#         package_data.setdefault(NAME, [])
#
#         for d in run('npm ls --only=prod --parseable', output=True, cwd=webui_root).splitlines():
#
#             d = d.decode("utf-8")
#
#             if d.startswith(self.node_modules):
#
#                 reld = os.path.relpath(d, root)
#                 print(reld)
#                 package_data[NAME] += _get_package_data(NAME, reld+'/**' )


def update_package_data(distribution):
    """update build_py options to get package_data changes"""
    build_py = distribution.get_command_obj('build_py')
    build_py.finalize_options()


class bdist_egg_disabled(bdist_egg):
    """Disabled version of bdist_egg
    Prevents setup.py install performing setuptools' default easy_install,
    which it should never ever do.
    """

    def run(self):
        sys.exit("Aborting implicit building of eggs. Use `pip install .` "
                 " to install from source.")


def wrapper(cls, strict=True):

    class Cmd(cls):
        def run(self):
            print("############## start %s" % cls.__name__)
            # if not getattr(self, 'uninstall', None):
            #     try:
            #         self.run_command('build_webui')
            #         #self.run_command('handle_files')
            #     except Exception:
            #         if strict:
            #             raise
            #         else:
            #             pass

            # update package data
            update_package_data(self.distribution)

            print("############## wrap end %s" % cls.__name__)
            result = cls.run(self)
            print("############## end %s" % cls.__name__)
            return result

    return Cmd


cmdclass = {
    # 'build_webui': BuildWebUI,
    'build_py': wrapper(build_py, strict=is_repo),
    'bdist_egg': wrapper(bdist_egg, strict=True) if 'bdist_egg' in sys.argv else bdist_egg_disabled,
    'sdist': wrapper(sdist, strict=True),
    'develop': wrapper(develop, strict=True),
}

if bdist_wheel:
    cmdclass['bdist_wheel'] = wrapper(bdist_wheel, strict=True)


# ----------------------
# some tools
# ----------------------

def run(cmd, output=False, **kwargs):
    """Echo a command before running it.  Defaults to repo as cwd"""
    kwargs.setdefault('cwd', here)
    kwargs.setdefault('shell', os.name == 'nt')
    if not isinstance(cmd, (list, tuple)) and os.name != 'nt':
        cmd = shlex.split(cmd)
    cmd[0] = which(cmd[0])
    print('> ' + ' '.join(cmd))
    return check_output(cmd, **kwargs) if output else check_call(cmd, **kwargs)


def is_stale(target, source):
    """Test whether the target file/directory is stale based on the source
       file/directory.
    """
    if not os.path.exists(target):
        return True
    target_mtime = recursive_mtime(target) or 0
    return compare_recursive_mtime(source, cutoff=target_mtime)


def compare_recursive_mtime(path, cutoff, newest=True):
    """Compare the newest/oldest mtime for all files in a directory.
    Cutoff should be another mtime to be compared against. If an mtime that is
    newer/older than the cutoff is found it will return True.
    E.g. if newest=True, and a file in path is newer than the cutoff, it will
    return True.
    """
    if os.path.isfile(path):
        mt = mtime(path)
        if newest:
            if mt > cutoff:
                return True
        elif mt < cutoff:
            return True
    for dirname, _, filenames in os.walk(path, topdown=False):
        for filename in filenames:
            mt = mtime(pjoin(dirname, filename))
            if newest:  # Put outside of loop?
                if mt > cutoff:
                    return True
            elif mt < cutoff:
                return True
    return False


def recursive_mtime(path, newest=True):
    """Gets the newest/oldest mtime for all files in a directory."""
    if os.path.isfile(path):
        return mtime(path)
    current_extreme = None
    for dirname, dirnames, filenames in os.walk(path, topdown=False):
        for filename in filenames:
            mt = mtime(pjoin(dirname, filename))
            if newest:  # Put outside of loop?
                if mt >= (current_extreme or mt):
                    current_extreme = mt
            elif mt <= (current_extreme or mt):
                current_extreme = mt
    return current_extreme


def mtime(path):
    """shorthand for mtime"""
    return os.stat(path).st_mtime


# `shutils.which` function copied verbatim from the Python-3.3 source.
def which(cmd, mode=os.F_OK | os.X_OK, path=None):
    """Given a command, mode, and a PATH string, return the path which
    conforms to the given mode on the PATH, or None if there is no such
    file.
    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), or can be overridden with a custom search
    path.
    """

    # Check that a given file can be accessed with the correct mode.
    # Additionally check that `file` is not a directory, as on Windows
    # directories pass the os.access check.
    def _access_check(fn, mode):
        return (os.path.exists(fn) and os.access(fn, mode) and
                not os.path.isdir(fn))

    # Short circuit. If we're given a full path which matches the mode
    # and it exists, we're done here.
    if _access_check(cmd, mode):
        return cmd

    path = (path or os.environ.get("PATH", os.defpath)).split(os.pathsep)

    if sys.platform == "win32":
        # The current directory takes precedence on Windows.
        if os.curdir not in path:
            path.insert(0, os.curdir)

        # PATHEXT is necessary to check on Windows.
        pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
        # See if the given file matches any of the expected path extensions.
        # This will allow us to short circuit when given "python.exe".
        matches = [cmd for ext in pathext if cmd.lower().endswith(ext.lower())]
        # If it does match, only test that one, otherwise we have to try
        # others.
        files = [cmd] if matches else [cmd + ext.lower() for ext in pathext]
    else:
        # On other platforms you don't have things like PATHEXT to tell you
        # what file suffixes are executable, so just pass on cmd as-is.
        files = [cmd]

    seen = set()
    for dir in path:
        dir = os.path.normcase(dir)
        if dir not in seen:
            seen.add(dir)
            for thefile in files:
                name = os.path.join(dir, thefile)
                if _access_check(name, mode):
                    return name
    return None


def _get_data_files(data_specs, existing):
    """Expand data file specs into valid data files metadata.
    Parameters
    ----------
    data_specs: list of tuples
        See [createcmdclass] for description.
    existing: list of tuples
        The existing distrubution data_files metadata.
    Returns
    -------
    A valid list of data_files items.
    """
    # Extract the existing data files into a staging object.
    file_data = defaultdict(list)
    for (path, files) in existing or []:
        file_data[path] = files

    # Extract the files and assign them to the proper data
    # files path.
    for (path, dname, pattern) in data_specs or []:
        dname = dname.replace(os.sep, '/')
        offset = len(dname) + 1

        files = _get_files(pjoin(dname, pattern))
        for fname in files:
            # Normalize the path.
            root = os.path.dirname(fname)
            full_path = '/'.join([path, root[offset:]])
            if full_path.endswith('/'):
                full_path = full_path[:-1]
            file_data[full_path].append(fname)

    # Construct the data files spec.
    data_files = []
    for (path, files) in file_data.items():
        data_files.append((path, files))
    return data_files


def _get_files(file_patterns, top=here):
    """Expand file patterns to a list of paths.
    Parameters
    -----------
    file_patterns: list or str
        A list of glob patterns for the data file locations.
        The globs can be recursive if they include a `**`.
        They should be relative paths from the top directory or
        absolute paths.
    top: str
        the directory to consider for data files

    Note:
    Files in `node_modules` are ignored.
    """
    if not isinstance(file_patterns, (list, tuple)):
        file_patterns = [file_patterns]

    for i, p in enumerate(file_patterns):
        if os.path.isabs(p):
            file_patterns[i] = os.path.relpath(p, top)

    matchers = [_compile_pattern(p) for p in file_patterns]

    files = set()

    for root, dirnames, filenames in os.walk(top):
        for m in matchers:
            for filename in filenames:
                fn = os.path.relpath(pjoin(root, filename), top)
                if m(fn):
                    files.add(fn.replace(os.sep, '/'))

    return list(files)


def _get_package_data(root, file_patterns=None):
    """Expand file patterns to a list of `package_data` paths.
    Parameters
    -----------
    root: str
        The relative path to the package root from `HERE`.
    file_patterns: list or str, optional
        A list of glob patterns for the data file locations.
        The globs can be recursive if they include a `**`.
        They should be relative paths from the root or
        absolute paths.  If not given, all files will be used.

    Note:
    Files in `node_modules` are ignored.
    """
    if file_patterns is None:
        file_patterns = ['*']
    return _get_files(file_patterns, pjoin(here, root))


import re


def _compile_pattern(pat, ignore_case=True):
    """Translate and compile a glob pattern to a regular expression matcher."""
    if isinstance(pat, bytes):
        pat_str = pat.decode('ISO-8859-1')
        res_str = _translate_glob(pat_str)
        res = res_str.encode('ISO-8859-1')
    else:
        res = _translate_glob(pat)
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(res, flags=flags).match


def _iexplode_path(path):
    """Iterate over all the parts of a path.
    Splits path recursively with os.path.split().
    """
    (head, tail) = os.path.split(path)
    if not head or (not tail and head == path):
        if head:
            yield head
        if tail or not head:
            yield tail
        return
    for p in _iexplode_path(head):
        yield p
    yield tail


def _translate_glob(pat):
    """Translate a glob PATTERN to a regular expression."""
    translated_parts = []
    for part in _iexplode_path(pat):
        translated_parts.append(_translate_glob_part(part))
    os_sep_class = '[%s]' % re.escape(SEPARATORS)
    res = _join_translated(translated_parts, os_sep_class)
    return '{res}\\Z(?ms)'.format(res=res)


def _join_translated(translated_parts, os_sep_class):
    """Join translated glob pattern parts.
    This is different from a simple join, as care need to be taken
    to allow ** to match ZERO or more directories.
    """
    res = ''
    for part in translated_parts[:-1]:
        if part == '.*':
            # drop separator, since it is optional
            # (** matches ZERO or more dirs)
            res += part
        else:
            res += part + os_sep_class

    if translated_parts[-1] == '.*':
        # Final part is **
        res += '.+'
        # Follow stdlib/git convention of matching all sub files/directories:
        res += '({os_sep_class}?.*)?'.format(os_sep_class=os_sep_class)
    else:
        res += translated_parts[-1]
    return res


def _translate_glob_part(pat):
    """Translate a glob PATTERN PART to a regular expression."""
    # Code modified from Python 3 standard lib fnmatch:
    if pat == '**':
        return '.*'
    i, n = 0, len(pat)
    res = []
    while i < n:
        c = pat[i]
        i = i + 1
        if c == '*':
            # Match anything but path separators:
            res.append('[^%s]*' % SEPARATORS)
        elif c == '?':
            res.append('[^%s]?' % SEPARATORS)
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j + 1
            if j < n and pat[j] == ']':
                j = j + 1
            while j < n and pat[j] != ']':
                j = j + 1
            if j >= n:
                res.append('\\[')
            else:
                stuff = pat[i:j].replace('\\', '\\\\')
                i = j + 1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res.append('[%s]' % stuff)
        else:
            res.append(re.escape(c))
    return ''.join(res)


# ----------------------
# setup
# ----------------------

requires = [
    "future",
    "pymongo==3.5.1",
    "python-dateutil",
    "pillow",
    "shortid",
    "python-magic",
    "Flask",
    "flask-cors",
    "paramiko",
    "jsonderef",
    "pyserial",
    "paho-mqtt",
    "jsonpath-rw",
    "croniter",
    "dateparser",
    "pyaes",
    "scapy",
    "PyJWT",
    "netaddr",
    "webargs",
    "apispec",  # http api
    "Jinja2",  # http api
    "xmltodict",
    "python-magic",
    "cherrypy",
    "pytz",
    "flask-compress"
]

if os.name != "nt":
    requires.append("bluepy")

setup(
    name='ething',

    version=__version__,

    description='A home automation project',

    long_description=long_description,

    url='https://github.com/e-thing/ething',

    author='Adrien Mezerette',
    author_email='a.mezerette@gmail.com',

    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],


    keywords='home automation ething iot mysensors rflink zigate',

    packages=find_packages(),


    install_requires=requires,

    extras_require={
        "dev": [
            "pytest",  # unit test
        ]
    },

    include_package_data=False,

    package_data={
        # accept ** wildcard
        NAME: _get_package_data(NAME, [
            'nodejs/*.js',
            'mongodb/**',
            'webui/index.html',
            'webui/src/**',
            'webui/dist/**',
            'webui/images/**',
            'webserver/api.md.j2',
            'webserver/routes/*.html',
        ])
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

    zip_safe=False,

    cmdclass=cmdclass,

)
