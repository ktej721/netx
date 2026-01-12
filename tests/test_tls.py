import unittest
from unittest.mock import patch, MagicMock
import ssl
import socket

from netx.core.models import RequestContext
from netx.phases.tls import TLSHandshakePhase
from netx.core.exceptions import TLSHandshakeError


class TestTLSHandshakePhase(unittest.TestCase):

    @patch('ssl.create_default_context')
    def test_tls_handshake_success(self, mock_create_context):
        # Mock the SSL context and the wrapped socket
        mock_ssl_context = MagicMock()
        mock_tls_sock = MagicMock()
        mock_create_context.return_value = mock_ssl_context
        mock_ssl_context.wrap_socket.return_value = mock_tls_sock

        # Mock the return values for version and cipher
        mock_tls_sock.version.return_value = "TLSv1.3"
        mock_tls_sock.cipher.return_value = ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256)

        # Setup context
        context = RequestContext(url="https://google.com", scheme="https", host="google.com")
        context.sock = socket.socket() # A real socket is fine here as it's not used

        phase = TLSHandshakePhase()
        result = phase.run(context)

        self.assertEqual(result.tls_version, "TLSv1.3")
        self.assertEqual(result.cipher, "TLS_AES_256_GCM_SHA384")
        self.assertEqual(result.sni, "google.com")
        self.assertFalse(result.skipped)
        
        # Use ANY for the socket argument since it's an instance we created in the test
        from unittest.mock import ANY
        mock_ssl_context.wrap_socket.assert_called_with(ANY, server_hostname="google.com")

    def test_tls_handshake_skipped_for_http(self):
        context = RequestContext(url="http://google.com", scheme="http", host="google.com")
        phase = TLSHandshakePhase()
        result = phase.run(context)
        self.assertTrue(result.skipped)
        self.assertEqual(result.reason, "Scheme is not HTTPS")

    @patch('ssl.create_default_context')
    def test_tls_handshake_failure(self, mock_create_context):
        mock_ssl_context = MagicMock()
        mock_create_context.return_value = mock_ssl_context
        mock_ssl_context.wrap_socket.side_effect = ssl.SSLError("Handshake failed")

        context = RequestContext(url="https://google.com", scheme="https", host="google.com")
        context.sock = socket.socket()

        phase = TLSHandshakePhase()
        with self.assertRaises(TLSHandshakeError):
            phase.run(context)


if __name__ == '__main__':
    unittest.main()
