import unittest
import sys

from setuptools import setup, find_packages, Command


PKG_NAME = 'sanitize'


class RunTests(Command):
    """
    New setup.py command to run all tests for the package.
    """
    description = "run all tests for {0}".format(PKG_NAME)

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        tests = unittest.TestLoader().discover('.')
        runner = unittest.TextTestRunner()
        results = runner.run(tests)
        sys.exit(not results.wasSuccessful())


setup(
    name=PKG_NAME,
    version=".".join(map(str, __import__(PKG_NAME).__version__)),
    description="Bringing sanitiy to world of messed-up data",
    long_description=open('README.md').read(),
    author="Aaron Swartz",
    author_email="me@aaronsw.com",
    maintainer='Alireza Savand',
    maintainer_email='alireza.savand@gmail.com',
    url='http://www.aaronsw.com/2002/sanitize/',
    cmdclass={'test': RunTests},
    license=open('LICENSE').read(),
    packages=find_packages(exclude=['tests']),
    py_modules=[PKG_NAME],
    include_package_data=True,
    zip_safe=False,
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.3',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
