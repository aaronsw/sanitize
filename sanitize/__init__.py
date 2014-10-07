"""
sanitize: bringing sanitiy to world of messed-up data
"""
import string
import sgmllib
import re
import urlparse
import sys
import chardet
from sanitize import config


__version__ = (2014, 10, 7)

if config.DEBUG:
    import chardet.constants

    chardet.constants._debug = 1

_chardet = lambda data: chardet.detect(data)['encoding']


class BaseHTMLProcessor(sgmllib.SGMLParser):
    elements_no_end_tag = config.BASE_HTML_PROCESSOR__ELEMENTS_NO_END_TAGS

    _r_barebang = re.compile(r'<!((?!DOCTYPE|--|\[))', re.IGNORECASE)
    _r_bareamp = re.compile("&(?!#\d+;|#x[0-9a-fA-F]+;|\w+;)")
    _r_shorttag = re.compile(r'<([^<\s]+?)\s*/>')

    def __init__(self, encoding):
        self.encoding = encoding
        if config.DEBUG:
            sys.stderr.write('entering BaseHTMLProcessor, encoding=%s\n' % self.encoding)

        sgmllib.SGMLParser.__init__(self)

    def reset(self):
        self.pieces = []
        sgmllib.SGMLParser.reset(self)

    def _shorttag_replace(self, match):
        tag = match.group(1)
        if tag in self.elements_no_end_tag:
            return '<' + tag + ' />'
        else:
            return '<' + tag + '></' + tag + '>'

    def feed(self, data):
        if config.DEBUG:
            sys.stderr.write('BaseHTMLProcessor, feed, data=%s\n' % repr(data))

        data = self._r_barebang.sub(r'&lt;!\1', data)
        data = self._r_bareamp.sub("&amp;", data)
        data = self._r_shorttag.sub(self._shorttag_replace, data)

        if self.encoding and type(data) == type(u''):
            data = data.encode(self.encoding)

        sgmllib.SGMLParser.feed(self, data)

    def normalize_attrs(self, attrs):
        # utility method to be called by descendants
        attrs = [(k.lower(), v) for k, v in attrs]
        attrs = [(k, k in ('rel', 'type') and v.lower() or v) for k, v in attrs]

        return attrs

    def unknown_starttag(self, tag, attrs):
        # called for each start tag
        # attrs is a list of (attr, value) tuples
        # e.g. for <pre class='screen'>, tag='pre', attrs=[('class', 'screen')]
        if config.DEBUG:
            sys.stderr.write('BaseHTMLProcessor, unknown_starttag, tag=%s\n' % tag)

        def attrquote(data):
            data = self._r_bareamp.sub("&amp;", data)
            data = data.replace('"', '&quot;')

            return data

        newattrs = []
        # hack to reverse attribute decoding in py2.5
        for key, value in attrs:
            newvalue = []
            for c in value:
                if ord(c) > 127:
                    c = '&#' + str(ord(c)) + ';'
                newvalue.append(c)
            newattrs.append((key, ''.join(newvalue)))

        strattrs = ''.join([' %s="%s"' % (key, attrquote(value)) for key, value in newattrs])

        if tag in self.elements_no_end_tag:
            self.pieces.append('<%(tag)s%(strattrs)s />' % locals())
        else:
            self.pieces.append('<%(tag)s%(strattrs)s>' % locals())

    def unknown_endtag(self, tag):
        # called for each end tag, e.g. for </pre>, tag will be 'pre'
        # Reconstruct the original end tag.
        if tag not in self.elements_no_end_tag:
            self.pieces.append("</%(tag)s>" % locals())

    def handle_charref(self, ref):
        # called for each character reference, e.g. for '&#160;', ref will be '160'
        # Reconstruct the original character reference.
        self.pieces.append('&#%(ref)s;' % locals())

    def handle_entityref(self, ref):
        # called for each entity reference, e.g. for '&copy;', ref will be 'copy'
        # Reconstruct the original entity reference.
        self.pieces.append('&%(ref)s;' % locals())

    def handle_data(self, text):
        # called for each block of plain text, i.e. outside of any tag and
        # not containing any character or entity references
        # Store the original text verbatim.
        if config.DEBUG:
            sys.stderr.write('BaseHTMLProcessor, handle_text, text=%s\n' % text)

        self.pieces.append(text)

    def handle_comment(self, text):
        # called for each HTML comment, e.g. <!-- insert Javascript code here -->
        # Reconstruct the original comment.
        self.pieces.append('<!--%(text)s-->' % locals())

    def handle_pi(self, text):
        # called for each processing instruction, e.g. <?instruction>
        # Reconstruct original processing instruction.
        self.pieces.append('<?%(text)s>' % locals())

    def handle_decl(self, text):
        # called for the DOCTYPE, if present, e.g.
        # <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        # "http://www.w3.org/TR/html4/loose.dtd">
        # Reconstruct original DOCTYPE
        self.pieces.append('<!%(text)s>' % locals())

    _new_declname_match = re.compile(r'[a-zA-Z][-_.a-zA-Z0-9:]*\s*').match

    def _scan_name(self, i, declstartpos):
        rawdata = self.rawdata
        n = len(rawdata)
        if i == n:
            return None, -1
        m = self._new_declname_match(rawdata, i)
        if m:
            s = m.group()
            name = s.strip()
            if (i + len(s)) == n:
                return None, -1  # end of buffer
            return name.lower(), m.end()
        else:
            self.handle_data(rawdata)
            return None, -1

    def output(self):
        """
        Return processed HTML as a single string
        """
        return ''.join(self.pieces)
        # used to be: [str(p) for p in self.pieces]
        # not sure why... -- ASw


class HTMLSanitizer(BaseHTMLProcessor):
    acceptable_elements = config.HTML_SANITIZER__ACCEPTABLE_ELEMENTS
    acceptable_attributes = config.HTML_SANITIZER__ACCEPTABLE_ATTRIBUTES
    acceptable_uri_schemes = config.HTML_SANITIZER__ACCEPTABLE_URI_SCHEMES
    ignorable_elements = config.HTML_SANITIZER__IGNORABLE_ELEMENTS
    relative_uris = config.HTML_SANITIZER__RELATIVE_URIS

    def __init__(self, baseuri, encoding, required_attributes=None):
        BaseHTMLProcessor.__init__(self, encoding)
        self.baseuri = baseuri
        self.required_attributes = required_attributes
        # urlparse caches URL parsing for some reason
        # and its cache doesn't distinguish between Unicode and non-unicode
        # so it caches the Unicode version feedparser sends it
        # which causes breakage
        urlparse._parse_cache = {}

    def resolveURI(self, uri):
        if ':' in uri:
            scheme, rest = uri.split(':', 1)
            if scheme not in self.acceptable_uri_schemes:
                uri = '#' + rest
        if self.baseuri:
            return urlparse.urljoin(self.baseuri, uri)
        else:
            return uri

    def reset(self):
        BaseHTMLProcessor.reset(self)
        self.tag_stack = []
        self.ignore_level = 0

    def feed(self, data):
        BaseHTMLProcessor.feed(self, data)
        while self.tag_stack:
            BaseHTMLProcessor.unknown_endtag(self, self.tag_stack.pop())

    def unknown_starttag(self, tag, attrs):
        if tag in self.ignorable_elements:
            self.ignore_level += 1
            return

        if self.ignore_level:
            return

        if tag in self.acceptable_elements:
            attrs = self.normalize_attrs(attrs)
            attrs = [(key, value) for key, value in attrs if key in self.acceptable_attributes]
            attrs = [(key, ((tag, key) in self.relative_uris) and self.resolveURI(value) or value) for key, value in
                     attrs]
            if self.required_attributes and tag in self.required_attributes:
                attrs = [(key, value) for key, value in attrs if
                         key not in [k for k, v in self.required_attributes[tag]]]
                attrs += self.required_attributes[tag]

            if tag not in self.elements_no_end_tag:
                self.tag_stack.append(tag)
            BaseHTMLProcessor.unknown_starttag(self, tag, attrs)

    def unknown_endtag(self, tag):
        if tag in self.ignorable_elements:
            self.ignore_level -= 1
            return

        if self.ignore_level:
            return

        if tag in self.acceptable_elements and tag not in self.elements_no_end_tag:
            match = False
            while self.tag_stack:
                top = self.tag_stack.pop()
                if top == tag:
                    match = True
                    break
                BaseHTMLProcessor.unknown_endtag(self, top)

            if match:
                BaseHTMLProcessor.unknown_endtag(self, tag)

    def handle_pi(self, text):
        pass

    def handle_decl(self, text):
        pass

    def handle_data(self, text):
        if not self.ignore_level:
            text = text.replace('<', '')
            BaseHTMLProcessor.handle_data(self, text)


def HTML(htmlSource, encoding='utf8', baseuri=None, required_attributes=None, addnofollow=False):
    if not required_attributes:
        required_attributes = {}

    if addnofollow:
        required_attributes['a'] = [('rel', 'nofollow')]

    p = HTMLSanitizer(baseuri, encoding, required_attributes)
    p.feed(htmlSource)
    data = p.output()

    if config.TIDY_MARKUP:
        # loop through list of preferred Tidy interfaces looking for one that's installed,
        # then set up a common _tidy function to wrap the interface-specific API.
        _tidy = None
        for tidy_interface in config.PREFERRED_TIDY_INTERFACES:
            try:
                if tidy_interface == "uTidy":
                    from tidy import parseString as _utidy

                    def _tidy(data, **kwargs):
                        return str(_utidy(data, **kwargs))

                    break
                elif tidy_interface == "mxTidy":
                    from mx.Tidy import Tidy as _mxtidy

                    def _tidy(data, **kwargs):
                        nerrors, nwarnings, data, errordata = _mxtidy.tidy(data, **kwargs)
                        return data

                    break
            except:
                pass

        if _tidy:
            utf8 = type(data) == type(u'')
            if utf8:
                data = data.encode('utf-8')
            data = _tidy(data, output_xhtml=1, numeric_entities=1, wrap=0, char_encoding="utf8")
            if utf8:
                data = unicode(data, 'utf-8')
            if data.count('<body'):
                data = data.split('<body', 1)[1]
                if data.count('>'):
                    data = data.split('>', 1)[1]
            if data.count('</body'):
                data = data.split('</body', 1)[0]
    data = data.strip().replace('\r\n', '\n')

    return data


_ebcdic_to_ascii_map = None


def _ebcdic_to_ascii(s):
    global _ebcdic_to_ascii_map

    if not _ebcdic_to_ascii_map:
        emap = config.EMAP
        _ebcdic_to_ascii_map = string.maketrans(''.join(map(chr, range(256))), ''.join(map(chr, emap)))

    return s.translate(_ebcdic_to_ascii_map)


def _startswithbom(text, bom):
    for i, c in enumerate(bom):
        if c == '#':
            if text[i] == '\x00':
                return False
        else:
            if text[i] != c:
                return False

    return True


def _detectbom(text, bom_map=config.UNICODE_BOM_MAP):
    for bom, encoding in bom_map.iteritems():
        if _startswithbom(text, bom):
            return encoding

    return None


def characters(text, isXML=False, guess=None):
    """
    Takes a string text of unknown encoding and tries to
    provide a Unicode string for it.
    """
    _triedEncodings = []

    def tryEncoding(encoding):
        if encoding and encoding not in _triedEncodings:
            if encoding == 'ebcdic':
                return _ebcdic_to_ascii(text)
            try:
                return unicode(text, encoding)
            except UnicodeDecodeError:
                pass
            _triedEncodings.append(encoding)

    return (
        tryEncoding(guess) or
        tryEncoding(_detectbom(text)) or
        isXML and tryEncoding(_detectbom(text, config.XML_BOM_MAP)) or
        tryEncoding(_chardet(text)) or
        tryEncoding('utf8') or
        tryEncoding('windows-1252') or
        tryEncoding('iso-8859-1')
    )
