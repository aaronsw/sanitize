from unittest import TestCase

import sanitize


class TestSanitizeHTML(TestCase):
    def _html(self, html_source, expected_data, base_uri=None, add_nofollow=False):
        """
        :type html_source: str
        :type expected_data: str
        :type base_uri: str
        :type add_nofollow: bool
        """
        self.assertEqual(
            sanitize.HTML(
                htmlSource=html_source,
                baseuri=base_uri,
                addnofollow=add_nofollow
            ),
            expected_data
        )
    
    def test_basics(self):
        self._html("", "")
        self._html("hello", "hello")
    
    def test_balancing_tags(self):
        self._html("<b>hello", "<b>hello</b>")
        self._html("hello<b>", "hello<b></b>")
        self._html("hello</b>", "hello")
        self._html("hello<b/>", "hello<b></b>")
        self._html("<b><b><b>hello", "<b><b><b>hello</b></b></b>")
        self._html("</b><b>", "<b></b>")
    
    def test_trailing_slashes(self):
        self._html('<img>', '<img />')
        self._html('<img/>', '<img />')
        self._html('<b/></b>', '<b></b>')
    
    def test_balancing_angle_brakets(self):
        self._html('<img src="foo"', '')
        self._html('b>', 'b>')
        self._html('<img src="foo"/', '')
        self._html('>', '>')
        self._html('foo<b', 'foo')
        self._html('b>foo', 'b>foo')
        self._html('><b', '>')
        self._html('b><', 'b>')
        self._html('><b>', '><b></b>')
    
    def test_attributes(self):
        self._html('<img src=foo>', '<img src="foo" />')
        self._html('<img asrc=foo>', '<img />')
        self._html('<img src=test test>', '<img src="test" />')
        self._html('<input type="checkbox" checked>', '<input type="checkbox" checked="checked" />')
    
    def test_dangerous_small_sample(self):
        ## dangerous tags (a small sample)
        sHTML = lambda x: self._html(x, 'safe <b>description</b>')
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

        for x in ['onabort', 'onblur', 'onchange', 'onclick', 'ondblclick', 'onerror', 'onfocus', 'onkeydown', 'onkeypress',
                  'onkeyup', 'onload', 'onmousedown', 'onmouseout', 'onmouseover', 'onmouseup', 'onreset', 'resize', 'onsubmit',
                  'onunload']:
            self._html(
                '<img src="http://www.ragingplatypus.com/i/cam-full.jpg" %s="location.href=\'http://www.ragingplatypus.com/\';" />' % x,
                '<img src="http://www.ragingplatypus.com/i/cam-full.jpg" />')
        
        self._html(
            '<a href="http://www.ragingplatypus.com/" style="display:block; position:absolute; left:0; top:0; width:100%; height:100%; z-index:1; background-color:black; background-image:url(http://www.ragingplatypus.com/i/cam-full.jpg); background-x:center; background-y:center; background-repeat:repeat;">never trust your upstream platypus</a>',
            '<a href="http://www.ragingplatypus.com/">never trust your upstream platypus</a>')

    def test_ignorables(self):
        self._html('foo<style>bar', 'foo')
        self._html('foo<style>bar</style>', 'foo')

    def test_non_allowed_tags(self):
        self._html('<script>', '')
        self._html('<script', '')
        self._html('<script/>', '')
        self._html('</script>', '')
        self._html('<script woo=yay>', '')
        self._html('<script woo="yay">', '')
        self._html('<script woo="yay>', '')
        self._html('<script woo="yay<b>', '')
        self._html('<script<script>>', '')
        self._html('<<script>script<script>>', '')
        self._html('<<script><script>>', '')
        self._html('<<script>script>>', '')
        self._html('<<script<script>>', '')
        self._html('<scr\0ipt>', '')

    def test_bad_protocols_small_sample(self):
        ## bad protocols (a small sample)
        self._html('<a href="http://foo">bar</a>', '<a href="http://foo">bar</a>')
        self._html('<a href="ftp://foo">bar</a>', '<a href="ftp://foo">bar</a>')
        self._html('<a href="mailto:foo">bar</a>', '<a href="mailto:foo">bar</a>')
        self._html('<a href="javascript:foo">bar</a>', '<a href="#foo">bar</a>')
        self._html('<a href="java script:foo">bar</a>', '<a href="#foo">bar</a>')
        self._html('<a href="java\tscript:foo">bar</a>', '<a href="#foo">bar</a>')
        self._html('<a href="java\nscript:foo">bar</a>', '<a href="#foo">bar</a>')
        self._html('<a href="java' + chr(1) + 'script:foo">bar</a>', '<a href="#foo">bar</a>')
        self._html('<a href="jscript:foo">bar</a>', '<a href="#foo">bar</a>')
        self._html('<a href="vbscript:foo">bar</a>', '<a href="#foo">bar</a>')
        self._html('<a href="view-source:foo">bar</a>', '<a href="#foo">bar</a>')
        self._html('<a href="notinventedyet:foo">bar</a>', '<a href="#foo">bar</a>')

    def test_base_uris(self):
        self._html('<a href="foo">bar</a>', '<a href="http://baz.net/foo">bar</a>', base_uri='http://baz.net')
        self._html('<a href="foo">bar</a>', '<a href="http://baz.net/foo">bar</a>', base_uri='http://baz.net/')
        self._html('<a href="foo">bar</a>', '<a href="http://baz.net/foo">bar</a>', base_uri='http://baz.net/goo')
        self._html('<img src="foo" />', '<img src="http://baz.net/foo" />', base_uri='http://baz.net')

    def test_auto_closers(self):
        self._html('<img src="a">', '<img src="a" />')
        self._html('<img src="a">foo</img>', '<img src="a" />foo')
        self._html('</img>', '')

    def test_cooments(self):
        self._html('<!--foo-->', '<!--foo-->')
        self._html('doo<!--', 'doo')

    def test_crazy(self):
        ## crazy: http://alpha-geek.com/example/crazy_html2.html
        self._html(
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\r\n\r\n<html xmlns="http://www.w3.org/1999/xhtml">\r\n<head>\r\n<title>Crazy HTML -- Can Your Regex Parse This?</title>\r\n</head>\r\n<body    notRealAttribute="value"onload="executeMe();"foo="bar"\r\n\r\n>\r\n<!-- <script> -->\r\n\r\n<!-- \r\n\t<script> \r\n-->\r\n\r\n</script>\r\n\r\n\r\n<script\r\n\r\n\r\n>\r\n\r\nfunction executeMe()\r\n{\r\n\r\n\r\n\r\n\r\n/* <script> \r\nfunction am_i_javascript()\r\n{\r\n\tvar str = "Some innocuously commented out stuff";\r\n}\r\n< /script>\r\n*/\r\n\r\n\t\r\n\t\r\n\t\r\n\t\r\n\t\r\n\t\r\n\t\r\n\t\r\n\talert("Executed");\r\n}\r\n\r\n                                   </script\r\n\r\n\r\n\r\n>\r\n<h1>Did The Javascript Execute?</h1>\r\n<div notRealAttribute="value\r\n"onmouseover="\r\nexecuteMe();\r\n"foo="bar">\r\nI will execute here, too, if you mouse over me\r\n</div>\r\nThis is to keep you guys honest...<br />\r\nI like ontonology.  I like to script ontology.  Though, script>style>this.\r\n</body>\r\n</html>',
            'Crazy HTML -- Can Your Regex Parse This?\n\n\n<!-- <script> -->\n\n<!-- \n\t<script> \n-->\n\n\n\nfunction executeMe()\n{\n\n\n\n\n/* \n<h1>Did The Javascript Execute?</h1>\n<div>\nI will execute here, too, if you mouse over me\n</div>\nThis is to keep you guys honest...<br />\nI like ontonology.  I like to script ontology.  Though, script>style>this.')

    def test_validate_entity_references(self):
            self._html("&nbsp;", "&nbsp;")
            self._html("&#160;", "&#160;")
            self._html("&#xa0;", "&#xa0;")
            self._html("&#xA0;", "&#xA0;")

    def test_unescaped_ampersands(self):
        self._html("AT&T", "AT&amp;T")
        self._html("http://example.org?a=1&b=2", "http://example.org?a=1&amp;b=2")

    def test_attribute_values(self):
        self._html('<a title="&">amp</a>', '<a title="&amp;">amp</a>')
        self._html('<a title="AT&amp;T">test</a>', '<a title="AT&amp;T">test</a>')
        self._html('<a title=\'"foo"\'>test</a>', '<a title="&quot;foo&quot;">test</a>')
        self._html('<a title="&quot;foo&quot;">test</a>', '<a title="&quot;foo&quot;">test</a>')
        self._html('<a title="foo&nbsp;bar">test</a>', '<a title="foo&nbsp;bar">test</a>')
        self._html('<a title="foo&#xa0;bar">test</a>', '<a title="foo&#xa0;bar">test</a>')
        self._html('<a title="foo&#xA0;bar">test</a>', '<a title="foo&#xA0;bar">test</a>')
        self._html('<a title="foo&#160;bar">test</a>', '<a title="foo&#160;bar">test</a>')
        self._html('<a title="foo<bar">test</a>', '<a title="foo<bar">test</a>')
        self._html('<a title="foo&lt;bar">test</a>', '<a title="foo<bar">test</a>')

    def test_quote_characters(self):
        self._html('<a title="&#34;">quote</a>', '<a title="&quot;">quote</a>')
        self._html('<a title="&#39;">quote</a>', '<a title="\'">quote</a>')

    def test_adding_nofollow(self):
        self._html(
            html_source='<a href="http://spam.example.org/">viagra</a>',
            expected_data='<a href="http://spam.example.org/" rel="nofollow">viagra</a>',
             add_nofollow=True
        )
        self._html(
            html_source='<a rel="foo" href="http://spam.example.org/">viagra</a>',
             expected_data='<a href="http://spam.example.org/" rel="nofollow">viagra</a>',
             add_nofollow=True
        )
