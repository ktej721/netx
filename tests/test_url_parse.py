import unittest
from netx.core.models import RequestContext
from netx.phases.url_parse import URLParsePhase
from netx.core.exceptions import URLParseError


class TestURLParsePhase(unittest.TestCase):

    def test_valid_https_url(self):
        context = RequestContext(url="https://www.google.com/search?q=test")
        phase = URLParsePhase()
        result = phase.run(context)
        self.assertEqual(result.scheme, "https")
        self.assertEqual(result.host, "www.google.com")
        self.assertEqual(result.port, 443)
        self.assertEqual(result.path, "/search")
        self.assertEqual(result.query, "q=test")

    def test_valid_http_url_with_port(self):
        context = RequestContext(url="http://localhost:8080")
        phase = URLParsePhase()
        result = phase.run(context)
        self.assertEqual(result.scheme, "http")
        self.assertEqual(result.host, "localhost")
        self.assertEqual(result.port, 8080)
        self.assertEqual(result.path, "/")
        self.assertEqual(result.query, "")

    def test_invalid_scheme(self):
        context = RequestContext(url="ftp://google.com")
        phase = URLParsePhase()
        with self.assertRaises(URLParseError):
            phase.run(context)

    def test_missing_host(self):
        context = RequestContext(url="https://")
        phase = URLParsePhase()
        with self.assertRaises(URLParseError):
            phase.run(context)


if __name__ == '__main__':
    unittest.main()
