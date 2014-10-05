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
