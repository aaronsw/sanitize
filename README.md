`sanitize` is a Python module for making sure various things (e.g. HTML) are safe to use. It was originally written by Mark Pilgrim and is distributed under the BSD license.

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
