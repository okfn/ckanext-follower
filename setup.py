from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-follower',
	version=version,
	description="Allows users to follow packages",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='John Glover',
	author_email='j@johnglover.net',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.follower'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here, eg
	# myplugin=ckanext.follower:PluginClass
	""",
)
