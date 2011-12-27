"""unit tests for sanitize"""
__author__ = "Aaron Swartz <http://www.aaronsw.com/>"
__version__ = "0.33"
__license__ = "public domain"
_adaptedfrom_ = [
  "http://www.iamcal.com/publish/articles/php/processing_html_part_2/",
  "http://feedparser.org/tests/wellformed/sanitize/",
  "http://alpha-geek.com/example/crazy_html2.html"]

import sanitize

def HTML(a, b, baseuri=None, addnofollow=False):
    try:
        assert sanitize.HTML(a, baseuri=baseuri, addnofollow=addnofollow) == b
    except AssertionError:
        print ' in:', repr(a)
        print 'out:', repr(sanitize.HTML(a, baseuri=baseuri))
        print 'exp:', repr(b)
        raise

## basics
HTML("","")
HTML("hello","hello")

## balancing tags
HTML("<b>hello","<b>hello</b>")
HTML("hello<b>","hello<b></b>")
HTML("hello</b>","hello")
HTML("hello<b/>","hello<b></b>")
HTML("<b><b><b>hello","<b><b><b>hello</b></b></b>")
HTML("</b><b>","<b></b>")

## trailing slashes
HTML('<img>','<img />')
HTML('<img/>','<img />')
HTML('<b/></b>','<b></b>')

## balancing angle brakets
HTML('<img src="foo"','')
HTML('b>','b>')
HTML('<img src="foo"/','')
HTML('>','>')
HTML('foo<b','foo')
HTML('b>foo','b>foo')
HTML('><b','>')
HTML('b><','b>')
HTML('><b>','><b></b>')

## attributes
HTML('<img src=foo>','<img src="foo" />')
HTML('<img asrc=foo>','<img />')
HTML('<img src=test test>','<img src="test" />')
HTML('<input type="checkbox" checked>', '<input type="checkbox" checked="checked" />')

## dangerous tags (a small sample)
sHTML = lambda x: HTML(x, 'safe <b>description</b>')
sHTML('safe<applet code="foo.class" codebase="http://example.com/"></applet> <b>description</b>')
sHTML('<notinventedyet>safe</notinventedyet> <b>description</b>')
sHTML('<blink>safe</blink> <b>description</b>')
sHTML('safe<embed src="http://example.com/"> <b>description</b>')
sHTML('safe<frameset rows="*"><frame src="http://example.com/"></frameset> <b>description</b>')
sHTML('safe<iframe src="http://example.com/"> <b>description</b></iframe>')
sHTML('safe<link rel="stylesheet" type="text/css" href="http://example.com/evil.css"> <b>description</b>')
sHTML('safe<meta http-equiv="Refresh" content="0; URL=http://example.com/"> <b>description</b>')
sHTML('safe<object classid="clsid:C932BA85-4374-101B-A56C-00AA003668DC"> <b>description</b>')
sHTML('safe<script type="text/javascript">location.href=\'http:/\'+\'/example.com/\';</script> <b>description</b>')

for x in ['onabort', 'onblur', 'onchange', 'onclick', 'ondblclick', 'onerror', 'onfocus', 'onkeydown', 'onkeypress', 'onkeyup', 'onload', 'onmousedown', 'onmouseout', 'onmouseover', 'onmouseup', 'onreset', 'resize', 'onsubmit', 'onunload']:
    HTML('<img src="http://www.ragingplatypus.com/i/cam-full.jpg" %s="location.href=\'http://www.ragingplatypus.com/\';" />' % x,
    '<img src="http://www.ragingplatypus.com/i/cam-full.jpg" />')

HTML('<a href="http://www.ragingplatypus.com/" style="display:block; position:absolute; left:0; top:0; width:100%; height:100%; z-index:1; background-color:black; background-image:url(http://www.ragingplatypus.com/i/cam-full.jpg); background-x:center; background-y:center; background-repeat:repeat;">never trust your upstream platypus</a>', '<a href="http://www.ragingplatypus.com/">never trust your upstream platypus</a>')

## ignorables
HTML('foo<style>bar', 'foo')
HTML('foo<style>bar</style>', 'foo')

## non-allowed tags
HTML('<script>','')
HTML('<script','')
HTML('<script/>','')
HTML('</script>','')
HTML('<script woo=yay>','')
HTML('<script woo="yay">','')
HTML('<script woo="yay>','')
HTML('<script woo="yay<b>','')
HTML('<script<script>>','')
HTML('<<script>script<script>>','')
HTML('<<script><script>>','')
HTML('<<script>script>>','')
HTML('<<script<script>>','')
HTML('<scr\0ipt>', '')

## bad protocols (a small sample)
HTML('<a href="http://foo">bar</a>', '<a href="http://foo">bar</a>')
HTML('<a href="ftp://foo">bar</a>', '<a href="ftp://foo">bar</a>')
HTML('<a href="mailto:foo">bar</a>', '<a href="mailto:foo">bar</a>')
HTML('<a href="javascript:foo">bar</a>', '<a href="#foo">bar</a>')
HTML('<a href="java script:foo">bar</a>', '<a href="#foo">bar</a>')
HTML('<a href="java\tscript:foo">bar</a>', '<a href="#foo">bar</a>')
HTML('<a href="java\nscript:foo">bar</a>', '<a href="#foo">bar</a>')
HTML('<a href="java'+chr(1)+'script:foo">bar</a>', '<a href="#foo">bar</a>')
HTML('<a href="jscript:foo">bar</a>', '<a href="#foo">bar</a>')
HTML('<a href="vbscript:foo">bar</a>', '<a href="#foo">bar</a>')
HTML('<a href="view-source:foo">bar</a>', '<a href="#foo">bar</a>')
HTML('<a href="notinventedyet:foo">bar</a>', '<a href="#foo">bar</a>')

## base uris

HTML('<a href="foo">bar</a>', '<a href="http://baz.net/foo">bar</a>', baseuri='http://baz.net')
HTML('<a href="foo">bar</a>', '<a href="http://baz.net/foo">bar</a>', baseuri='http://baz.net/')
HTML('<a href="foo">bar</a>', '<a href="http://baz.net/foo">bar</a>', baseuri='http://baz.net/goo')

HTML('<img src="foo" />', '<img src="http://baz.net/foo" />', baseuri='http://baz.net')

## auto closers
HTML('<img src="a">', '<img src="a" />')
HTML('<img src="a">foo</img>', '<img src="a" />foo')
HTML('</img>', '')

## comments
HTML('<!--foo-->', '<!--foo-->')
HTML('doo<!--', 'doo')

## crazy: http://alpha-geek.com/example/crazy_html2.html
HTML('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\r\n\r\n<html xmlns="http://www.w3.org/1999/xhtml">\r\n<head>\r\n<title>Crazy HTML -- Can Your Regex Parse This?</title>\r\n</head>\r\n<body    notRealAttribute="value"onload="executeMe();"foo="bar"\r\n\r\n>\r\n<!-- <script> -->\r\n\r\n<!-- \r\n\t<script> \r\n-->\r\n\r\n</script>\r\n\r\n\r\n<script\r\n\r\n\r\n>\r\n\r\nfunction executeMe()\r\n{\r\n\r\n\r\n\r\n\r\n/* <script> \r\nfunction am_i_javascript()\r\n{\r\n\tvar str = "Some innocuously commented out stuff";\r\n}\r\n< /script>\r\n*/\r\n\r\n\t\r\n\t\r\n\t\r\n\t\r\n\t\r\n\t\r\n\t\r\n\t\r\n\talert("Executed");\r\n}\r\n\r\n                                   </script\r\n\r\n\r\n\r\n>\r\n<h1>Did The Javascript Execute?</h1>\r\n<div notRealAttribute="value\r\n"onmouseover="\r\nexecuteMe();\r\n"foo="bar">\r\nI will execute here, too, if you mouse over me\r\n</div>\r\nThis is to keep you guys honest...<br />\r\nI like ontonology.  I like to script ontology.  Though, script>style>this.\r\n</body>\r\n</html>', 'Crazy HTML -- Can Your Regex Parse This?\n\n\n<!-- <script> -->\n\n<!-- \n\t<script> \n-->\n\n\n\nfunction executeMe()\n{\n\n\n\n\n/* \n<h1>Did The Javascript Execute?</h1>\n<div>\nI will execute here, too, if you mouse over me\n</div>\nThis is to keep you guys honest...<br />\nI like ontonology.  I like to script ontology.  Though, script>style>this.')

## valid entity references
HTML("&nbsp;","&nbsp;")
HTML("&#160;","&#160;")
HTML("&#xa0;","&#xa0;")
HTML("&#xA0;","&#xA0;")

## unescaped ampersands
HTML("AT&T","AT&amp;T")
HTML("http://example.org?a=1&b=2","http://example.org?a=1&amp;b=2")

## attribute values
HTML('<a title="&">amp</a>','<a title="&amp;">amp</a>')
HTML('<a title="AT&amp;T">test</a>', '<a title="AT&amp;T">test</a>')
HTML('<a title=\'"foo"\'>test</a>', '<a title="&quot;foo&quot;">test</a>')
HTML('<a title="&quot;foo&quot;">test</a>', '<a title="&quot;foo&quot;">test</a>')
HTML('<a title="foo&nbsp;bar">test</a>', '<a title="foo&nbsp;bar">test</a>')
HTML('<a title="foo&#xa0;bar">test</a>', '<a title="foo&#xa0;bar">test</a>')
HTML('<a title="foo&#xA0;bar">test</a>', '<a title="foo&#xA0;bar">test</a>')
HTML('<a title="foo&#160;bar">test</a>', '<a title="foo&#160;bar">test</a>')
HTML('<a title="foo<bar">test</a>', '<a title="foo<bar">test</a>')
HTML('<a title="foo&lt;bar">test</a>', '<a title="foo<bar">test</a>')

## quote characters
HTML('<a title="&#34;">quote</a>','<a title="&quot;">quote</a>')
HTML('<a title="&#39;">quote</a>','<a title="\'">quote</a>')

## adding nofollow
HTML('<a href="http://spam.example.org/">viagra</a>', '<a href="http://spam.example.org/" rel="nofollow">viagra</a>', addnofollow=True)
HTML('<a rel="foo" href="http://spam.example.org/">viagra</a>', '<a href="http://spam.example.org/" rel="nofollow">viagra</a>', addnofollow=True)
