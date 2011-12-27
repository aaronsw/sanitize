import sys
from setuptools import setup, find_packages

setup(
   name = "sanitize",
   version = "0.33",
   description = "bringing sanitiy to world of messed-up data",
   author = "Aaron Swartz",
   author_email = "me@aaronsw.com",
   url='http://www.aaronsw.com/2002/sanitize/',
   classifiers=[
       'Development Status :: 5 - Production/Stable',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: GNU General Public License (GPL)',
       'Programming Language :: Python',
       'Programming Language :: Python :: 2',
       'Programming Language :: Python :: 2.3',
       'Programming Language :: Python :: 2.4',
       'Programming Language :: Python :: 2.5',
       'Programming Language :: Python :: 2.6',
       'Programming Language :: Python :: 2.7',
       'Programming Language :: Python :: 3',
       'Programming Language :: Python :: 3.0',
       'Programming Language :: Python :: 3.1',
       'Programming Language :: Python :: 3.2'
     ],
   license='BSD',
   packages=find_packages(),
   py_modules=['sanitize'],
   include_package_data=True,
   zip_safe=False,
)
