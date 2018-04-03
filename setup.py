from __future__ import print_function

# Always prefer setuptools over distutils
from setuptools import setup, Command, find_packages
from setuptools.command.sdist import sdist
from setuptools.command.build_py import build_py
# To use a consistent encoding
from codecs import open
import os, sys
from subprocess import check_call, CalledProcessError, check_output



here = os.path.abspath(os.path.dirname(__file__))
webui_root = os.path.join(here, 'ething/webui')
is_repo = os.path.exists(os.path.join(here, '.git'))


with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()


exec(open(os.path.join(here,'ething/version.py')).read())


shell = True



def has_npm():
	try:
		check_call('npm --version', shell=shell)
		return True
	except:
		print("npm unavailable. If you're running this command using sudo, make sure `npm` is available to sudo", file=sys.stderr)
		return False


def mtime(path):
	"""shorthand for mtime"""
	return os.stat(path).st_mtime


class BuildWebUI(Command):
	"""
	Build the webui
	"""
	
	description = 'build the webui'
	user_options = []
	
	node_modules = os.path.join(webui_root, 'node_modules')
	dist_dir = os.path.join(webui_root, 'dist')
	src_dir = os.path.join(webui_root, 'src')
	
	def initialize_options(self):
		pass
	
	def finalize_options(self):
		pass
	
	def run(self):
		
		if has_npm():
			
			# start build webui
			
			if self.should_build():
				
				try:
					print("Installing webui build dependencies with npm. This may take a while...")
					
					check_call('npm install --only=dev', shell=shell, cwd=webui_root)
					
					print("Building webui. This may take a while...")
					
					check_call('npm run build', shell=shell, cwd=webui_root)
					
				except CalledProcessError as e:
					print('ERROR: Failed to build the webui: %s'.format(e), file=sys.stderr)
			
			else :
				print("no webui build required.")
			
			# end build webui
			
			print("Installing webui dependencies with npm. This may take a while...")
			
			try:
				check_call('npm install --only=prod', shell=shell, cwd=webui_root)
			except CalledProcessError as e:
				print('ERROR: Failed to install the webui: %s'.format(e), file=sys.stderr)
			
			self.distribution.data_files = self.get_node_dependencies()
			
		
		
	
	def should_build(self):
		if not os.path.exists(self.dist_dir):
			return True
		return mtime(self.dist_dir) < mtime(self.src_dir)
	
	
	def get_node_dependencies(self):
		
		ntrim = len(here + os.path.sep)
		data_files = []
		
		for d in check_output('npm ls --only=prod --parseable', shell=shell, cwd=webui_root).splitlines():
			if d.startswith(self.node_modules):
				
				for (dd, dirs, filenames) in os.walk(d):
					dd = dd[ntrim:]
					for f in filenames:
						f = os.path.join(dd, f)
						print((os.path.dirname(f), f))
						data_files.append( (os.path.dirname(f), [f]) )
		
		return data_files
	
	



def npm_preproc(cls, strict=True):
	
	class Cmd(cls):
		def run(self):
			try:
				self.run_command('build_webui')
			except Exception:
				if strict:
					raise
				else:
					pass
			return cls.run(self)
	
	return Cmd
	


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
	],
	
	
	keywords='home automation ething iot mysensors rflink zigate', 
	
	packages=['ething'],

	
	install_requires=[
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
	],
	
	extras_require={
		"dev": [
			"apispec", # http api
            "Jinja2",
		]
	},
	
	include_package_data=True,
	
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
	
	cmdclass={
		'build_webui': BuildWebUI,
		'build_py': npm_preproc(build_py, is_repo),
	},
	
)
