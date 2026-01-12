import unittest
from unittest.mock import patch
import socket

from netx.core.models import RequestContext
from netx.phases.dns import DNSResolutionPhase
from netx.core.exceptions import DNSResolutionError


class TestDNSResolutionPhase(unittest.TestCase):

    @patch('socket.getaddrinfo')
    def test_dns_resolution_success(self, mock_getaddrinfo):
        # Mock the return value of socket.getaddrinfo
        mock_getaddrinfo.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('2a00:1450:4009:820::200e', 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('142.250.180.78', 443))
        ]

        context = RequestContext(url="https://google.com", host="google.com", port=443)
        phase = DNSResolutionPhase()
        result = phase.run(context)

        self.assertEqual(result.count, 2)
        self.assertEqual(result.addresses[0].ip, '2a00:1450:4009:820::200e')
        self.assertEqual(result.addresses[0].family, 'IPv6')
        self.assertEqual(result.addresses[1].ip, '142.250.180.78')
        self.assertEqual(result.addresses[1].family, 'IPv4')

    @patch('socket.getaddrinfo')
    def test_dns_resolution_failure(self, mock_getaddrinfo):
        # Mock socket.getaddrinfo to raise a gaierror
        mock_getaddrinfo.side_effect = socket.gaierror("DNS lookup failed")

        context = RequestContext(url="https://nonexistent.domain", host="nonexistent.domain", port=443)
        phase = DNSResolutionPhase()
        with self.assertRaises(DNSResolutionError):
            phase.run(context)


if __name__ == '__main__':
    unittest.main()
