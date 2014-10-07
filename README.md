# Sanitize

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

Usage
=====
```
>>> from sanitize import HTML
>>> HTML('<b>hello')
'<b>hello</b>'
>>> HTML('<img>')
'<img />'
>>> HTML(("<b><b><b>hello")
... )
'<b><b><b>hello</b></b></b>'
>>> HTML('<img src="foo"/')
''
>>> HTML('<input type="checkbox" checked>')
'<input type="checkbox" checked="checked" />'
>>> # dangerous tags (a small sample)
... 
>>> HTML('safe<applet code="foo.class" codebase="http://example.com/"></applet> <b>description</b>')
'safe <b>description</b>'
>>> HTML('safe<frameset rows="*"><frame src="http://example.com/"></frameset> <b>description</b>')
'safe <b>description</b>'
>>> # bad protocols (a small sample)
>>> HTML('<a href="java' + chr(1) + 'script:foo">bar</a>')
'<a href="#foo">bar</a>'
>>> HTML('<a href="vbscript:foo">bar</a>')
'<a href="#foo">bar</a>'
>>> 
```
To see more usage examples see `tests/test_sanitize_html.py`.


Installation
============

`python-sanitize` is available on pypi

http://pypi.python.org/pypi/python-sanitize

So easily install it by `pip`:

```
pip install sanitize
```

Or by `easy_install`:

```
$ easy_install sanitize
```

Another way is by cloning `python-sanitize`'s git repository

```
$ git clone git://github.com/Alir3z4/python-sanitize.git
```

Then install it by running

```
$ python setup.py install
```

Tests
=====

To run unit tests:

```
$ python setup.py test
```


License
=======

`Sanitize` is distributed under BSD license.
