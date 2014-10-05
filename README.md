[![Build Status](https://secure.travis-ci.org/Alir3z4/python-sanitize.png)](http://travis-ci.org/Alir3z4/python-sanitize)
[![Coverage Status](https://coveralls.io/repos/Alir3z4/python-sanitize/badge.png)](https://coveralls.io/r/Alir3z4/python-sanitize)
[![Downloads](https://pypip.in/d/sanitize/badge.png)](https://pypi.python.org/pypi/sanitize/)
[![Version](https://pypip.in/v/sanitize/badge.png)](https://pypi.python.org/pypi/sanitize/)
[![Egg?](https://pypip.in/egg/sanitize/badge.png)](https://pypi.python.org/pypi/sanitize/)
[![Wheel?](https://pypip.in/wheel/sanitize/badge.png)](https://pypi.python.org/pypi/sanitize/)
[![Format](https://pypip.in/format/sanitize/badge.png)](https://pypi.python.org/pypi/sanitize/)
[![License](https://pypip.in/license/sanitize/badge.png)](https://pypi.python.org/pypi/sanitize/)

`sanitize` is a Python module for making sure various things (e.g. HTML) are safe to use. 
It was originally written by Mark Pilgrim and is distributed under the BSD license.

Usage:

    >>> import sanitize
	>>> sanitize.HTML('safe<meta http-equiv="Refresh" content="0; URL=/">')
	'safe'

## How to do a release

1. Update the version in `sanitize.py`
2. Update the version in `setup.py`
3. Run the test cases: `python sanitize_test.py`
4. Run `python setup.py sdist upload`
5. `git commit -am "released version XX"`
6. `git push`
