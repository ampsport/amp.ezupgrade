from setuptools import setup, find_packages
import os

version = '.1'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(name='amp.ezupgrade',
      version=version,
      description="A set of conventions to make writing upgrade steps easier",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
	"Framework :: Plone",
        ],
      keywords='genericsetup upgrade plone profiles',
      author='IGS, Ltd.',
      author_email='eleddy@ampsport.com',
      url='https://github.com/digiyouadmin/amp.ezupgrade',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['amp'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
