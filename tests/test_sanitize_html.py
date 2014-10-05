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
